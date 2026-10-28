"""Tests for nb-collab CLI parsing and cell-source resolution.

These tests don't talk to a running JupyterLab; they only exercise the
argparse layer where the cell-ordering bug lived, plus the stdin/file
resolution pass that fills in cell sources before the websocket
handshake.
"""

from __future__ import annotations

import asyncio
import io
import json
import os
import time

from pathlib import Path, PureWindowsPath

import pytest

from datetime import datetime, timedelta

import tools.nb_collab as nb_collab
from tools.nb_collab import (
    DEFAULT_EXEC_ALL_TIMEOUT,
    DEFAULT_WAIT_TIMEOUT,
    DELETE_POLICIES,
    EDIT_POLICIES,
    EXECUTE_POLICIES,
    EXIT_NOT_RUNNING,
    HERA_CELL_VERSION,
    HERA_TAG_KEY,
    POLICY_APPEND_EXEC,
    POLICY_APPEND_ONLY,
    POLICY_EDIT_EXEC,
    POLICY_EDIT_NO_EXEC,
    STDIN_DELIM,
    _build_parser,
    _cell_is_running,
    _escape_md,
    _exec_timeout_message,
    _find_kernel_for_path,
    _format_output_tail,
    _insert_after_heading,
    _parse_eta_minutes,
    _read_policy,
    _rel_path,
    _render_duration_display,
    _render_eta_clock,
    _render_summary_line,
    _require_policy,
    _resolve_cells,
    _resolve_server,
    _resolve_single_source,
    _runtime_mtimes,
    _server_alive,
    _split_stdin,
    _stamp_cell_event,
    _timeout_message,
    _utc_now_iso,
    _warn_if_legacy_format,
)

# Source that bash would mangle under double-quote command substitution:
# backtick-wrapped path and a $(...) form. The whole point of the file path
# is that this survives byte-for-byte (the 2026-06-14 QC0426 backtick-path drop).
_SHELL_HOSTILE_SRC = (
    "# see `hera/models/aba_trilayer` for the forward model\n"
    "result = $(should not run)  # and `also not this`\n"
    'msg = "embedded $HOME and `backtick`"\n'
)


def _parse(*argv: str):
    return _build_parser().parse_args(["append", "x.ipynb", *argv])


def _parse_edit(*argv: str):
    return _build_parser().parse_args(["edit-cell", "x.ipynb", "cell-id-1", *argv])


# --------------------------------------------------------------------- #
# argparse layer
# --------------------------------------------------------------------- #


def test_interleaved_markdown_and_code_preserves_cli_order() -> None:
    args = _parse(
        "--markdown", "A",
        "--code", "B",
        "--markdown", "C",
        "--code", "D",
    )
    assert args.cells == [
        ("markdown", "A"),
        ("code", "B"),
        ("markdown", "C"),
        ("code", "D"),
    ]


def test_only_markdown_flags_collect_in_order() -> None:
    args = _parse("--markdown", "first", "--markdown", "second")
    assert args.cells == [("markdown", "first"), ("markdown", "second")]


def test_only_code_flags_collect_in_order() -> None:
    args = _parse("--code", "x = 1", "--code", "y = 2")
    assert args.cells == [("code", "x = 1"), ("code", "y = 2")]


def test_no_cell_flags_yields_empty_list() -> None:
    args = _parse()
    assert args.cells == []


def test_each_invocation_starts_with_fresh_cells_list() -> None:
    """Guard against mutable-default leakage between parse calls."""
    a = _parse("--markdown", "A")
    b = _parse("--code", "B")
    assert a.cells == [("markdown", "A")]
    assert b.cells == [("code", "B")]


def test_subcommand_required() -> None:
    with pytest.raises(SystemExit):
        _build_parser().parse_args([])


def test_dash_argument_tagged_as_stdin_placeholder() -> None:
    args = _parse("--markdown", "-", "--code", "-")
    assert args.cells == [("markdown_stdin", None), ("code_stdin", None)]


def test_file_flag_carries_path_string() -> None:
    args = _parse("--markdown-file", "./hello.md", "--code-file", "./snippet.py")
    assert args.cells == [
        ("markdown_file", "./hello.md"),
        ("code_file", "./snippet.py"),
    ]


def test_all_four_forms_share_dest_and_preserve_order() -> None:
    args = _parse(
        "--markdown", "intro",
        "--code-file", "./a.py",
        "--markdown", "-",
        "--code", "print(1)",
        "--markdown-file", "./section.md",
        "--code", "-",
    )
    assert args.cells == [
        ("markdown", "intro"),
        ("code_file", "./a.py"),
        ("markdown_stdin", None),
        ("code", "print(1)"),
        ("markdown_file", "./section.md"),
        ("code_stdin", None),
    ]


# --------------------------------------------------------------------- #
# append --wait / --execute / --follow argparse
# --------------------------------------------------------------------- #


def test_append_wait_flag_parses() -> None:
    args = _parse("--code", "c", "--wait")
    assert args.wait is True
    assert args.execute is False
    assert args.follow is False


def test_append_wait_follow_parses() -> None:
    args = _parse("--code", "c", "--wait", "--follow")
    assert args.wait is True
    assert args.follow is True


def test_append_execute_and_wait_mutually_exclusive() -> None:
    with pytest.raises(SystemExit):
        _build_parser().parse_args(
            ["append", "x.ipynb", "--code", "c", "--execute", "--wait"]
        )


def test_append_follow_requires_wait() -> None:
    """--follow alone (no --wait) is rejected before any websocket connect."""
    args = _build_parser().parse_args(["append", "x.ipynb", "--code", "c", "--follow"])
    with pytest.raises(SystemExit) as exc:
        nb_collab._cmd_append(args)
    assert "--follow applies only with --wait" in str(exc.value)


# --------------------------------------------------------------------- #
# append --summary / --eta argparse + dispatch-level validation
# --------------------------------------------------------------------- #


def test_append_summary_and_eta_default_none() -> None:
    args = _parse("--code", "c")
    assert args.summary is None
    assert args.eta is None


def test_append_summary_and_eta_parse_values() -> None:
    args = _parse("--code", "c", "--summary", "check the pocket", "--eta", "40m")
    assert args.summary == "check the pocket"
    assert args.eta == "40m"


def test_append_summary_requires_markdown_cell() -> None:
    """--summary/--eta need a markdown cell to render into; a code-only append
    is rejected before any websocket connect."""
    args = _parse("--code", "c", "--summary", "do the thing")
    with pytest.raises(SystemExit) as exc:
        nb_collab._cmd_append(args)
    assert "markdown cell" in str(exc.value)


def test_append_eta_alone_requires_markdown_cell() -> None:
    args = _parse("--code", "c", "--eta", "40m")
    with pytest.raises(SystemExit) as exc:
        nb_collab._cmd_append(args)
    assert "markdown cell" in str(exc.value)


def test_append_summary_rejects_backtick() -> None:
    args = _parse("--markdown", "# T", "--summary", "see the region (not a `path`)")
    with pytest.raises(SystemExit) as exc:
        nb_collab._cmd_append(args)
    assert "backtick" in str(exc.value)


def test_append_eta_bad_duration_rejected_before_connect() -> None:
    """A bare number (missing suffix) fails fast, before any cell lands."""
    args = _parse("--markdown", "# T", "--eta", "40")
    with pytest.raises(SystemExit) as exc:
        nb_collab._cmd_append(args)
    msg = str(exc.value).lower()
    assert "eta" in msg
    assert "suffix" in msg or "unit" in msg


# --------------------------------------------------------------------- #
# _split_stdin
# --------------------------------------------------------------------- #


def test_split_stdin_single_chunk_no_delimiter() -> None:
    raw = "import numpy as np\nprint(np.pi)\n"
    assert _split_stdin(raw, STDIN_DELIM) == ["import numpy as np\nprint(np.pi)"]


def test_split_stdin_multiple_chunks() -> None:
    raw = "chunk1\n---|\nchunk2\n---|\nchunk3\n"
    assert _split_stdin(raw, STDIN_DELIM) == ["chunk1", "chunk2", "chunk3"]


def test_split_stdin_preserves_internal_blank_lines() -> None:
    raw = "para 1\n\npara 2\n---|\nother\n"
    assert _split_stdin(raw, STDIN_DELIM) == ["para 1\n\npara 2", "other"]


def test_split_stdin_empty_input_yields_single_empty_chunk() -> None:
    assert _split_stdin("", STDIN_DELIM) == [""]


def test_split_stdin_delimiter_must_be_exact_match() -> None:
    """A line that merely starts with the delim is not a delimiter line."""
    raw = "header\n---| not the delim\nbody\n"
    assert _split_stdin(raw, STDIN_DELIM) == [
        "header\n---| not the delim\nbody"
    ]


# --------------------------------------------------------------------- #
# _resolve_cells — stdin
# --------------------------------------------------------------------- #


class _FakeStdin(io.StringIO):
    def __init__(self, content: str, tty: bool = False) -> None:
        super().__init__(content)
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


def _patch_stdin(monkeypatch: pytest.MonkeyPatch, content: str, tty: bool = False) -> None:
    monkeypatch.setattr("tools.nb_collab.sys.stdin", _FakeStdin(content, tty=tty))


def test_resolve_single_stdin_chunk_no_delimiter(monkeypatch: pytest.MonkeyPatch) -> None:
    body = "def f(x):\n    return x  # 'apostrophes' and \"quotes\" and $vars\n"
    _patch_stdin(monkeypatch, body)
    resolved = _resolve_cells([("code_stdin", None)])
    # _split_stdin drops the trailing newline of the final line.
    assert resolved == [("code", body.rstrip("\n"))]


def test_resolve_multi_chunk_stdin_preserves_order(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = "## Section header\n---|\nimport numpy as np\n---|\nprint('done')\n"
    _patch_stdin(monkeypatch, raw)
    parsed = [
        ("markdown_stdin", None),
        ("code_stdin", None),
        ("code_stdin", None),
    ]
    resolved = _resolve_cells(parsed)
    assert resolved == [
        ("markdown", "## Section header"),
        ("code", "import numpy as np"),
        ("code", "print('done')"),
    ]


def test_resolve_stdin_count_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_stdin(monkeypatch, "only one chunk\n")
    with pytest.raises(SystemExit) as exc:
        _resolve_cells([("code_stdin", None), ("code_stdin", None)])
    msg = str(exc.value)
    assert "chunk count (1)" in msg
    assert "flag count (2)" in msg


def test_resolve_stdin_tty_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_stdin(monkeypatch, "", tty=True)
    with pytest.raises(SystemExit) as exc:
        _resolve_cells([("code_stdin", None)])
    assert "tty" in str(exc.value)


def test_resolve_quoting_edge_cases_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verbatim source through stdin — the whole point of this feature."""
    body = (
        "import numpy as np\n"
        "def f(x):\n"
        "    # 'single' \"double\" $shell `back` \\escape\n"
        "    return x  # EOF-ish: 'EOF' EOF1 <<HEREDOC\n"
    )
    _patch_stdin(monkeypatch, body)
    resolved = _resolve_cells([("code_stdin", None)])
    assert resolved == [("code", body.rstrip("\n"))]


# --------------------------------------------------------------------- #
# _resolve_cells — files
# --------------------------------------------------------------------- #


def test_resolve_file_reads_utf8_contents(tmp_path) -> None:
    p = tmp_path / "snippet.py"
    body = "x = 1  # 'fine'\nprint(x)\n"
    p.write_text(body, encoding="utf-8")
    resolved = _resolve_cells([("code_file", str(p))])
    assert resolved == [("code", body)]


def test_resolve_file_preserves_shell_hostile_chars_verbatim(tmp_path) -> None:
    """A markdown-file/code-file source with backticks and $(...) must round-trip
    byte-for-byte — this is the bulletproof path that avoids shell substitution."""
    p = tmp_path / "snippet.py"
    p.write_text(_SHELL_HOSTILE_SRC, encoding="utf-8")
    resolved = _resolve_cells([("code_file", str(p))])
    assert resolved == [("code", _SHELL_HOSTILE_SRC)]
    # The backtick-wrapped path fragment that the 2026-06-14 session lost.
    assert "`hera/models/aba_trilayer`" in resolved[0][1]


def test_resolve_file_missing_aborts(tmp_path) -> None:
    missing = tmp_path / "nope.py"
    with pytest.raises(SystemExit) as exc:
        _resolve_cells([("code_file", str(missing))])
    assert "file not found" in str(exc.value)


def test_resolve_file_non_utf8_aborts(tmp_path) -> None:
    p = tmp_path / "bin.py"
    p.write_bytes(b"\xff\xfe\x00\x00not utf-8")
    with pytest.raises(SystemExit) as exc:
        _resolve_cells([("code_file", str(p))])
    assert "UTF-8" in str(exc.value)


# --------------------------------------------------------------------- #
# _resolve_cells — inline backtick / $(...) refusal
# --------------------------------------------------------------------- #


@pytest.mark.parametrize("kind, flag", [("markdown", "--markdown"), ("code", "--code")])
@pytest.mark.parametrize("bad", ["see `path`", "x = $(cmd)"])
def test_resolve_inline_backtick_or_subst_refused(kind, flag, bad) -> None:
    with pytest.raises(SystemExit) as exc:
        _resolve_cells([(kind, bad)])
    msg = str(exc.value)
    assert flag in msg and f"{kind}-file" in msg


def test_resolve_file_and_stdin_allow_backticks(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """The substitution-free paths (file, stdin) must NOT be refused."""
    p = tmp_path / "snip.py"
    p.write_text(_SHELL_HOSTILE_SRC, encoding="utf-8")
    _patch_stdin(monkeypatch, "x = `y`\n")
    resolved = _resolve_cells([("code_file", str(p)), ("code_stdin", None)])
    assert resolved == [("code", _SHELL_HOSTILE_SRC), ("code", "x = `y`")]


# --------------------------------------------------------------------- #
# _resolve_cells — combined
# --------------------------------------------------------------------- #


def test_resolve_mixed_inline_file_stdin_preserves_order(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    md_file = tmp_path / "section.md"
    md_file.write_text("# from file\n", encoding="utf-8")
    code_file = tmp_path / "snippet.py"
    code_file.write_text("print('file')\n", encoding="utf-8")

    raw = "stdin markdown\n---|\nprint('stdin code')\n"
    _patch_stdin(monkeypatch, raw)

    parsed = [
        ("markdown", "## inline header"),
        ("code_file", str(code_file)),
        ("markdown_stdin", None),
        ("code", "x = 42"),
        ("markdown_file", str(md_file)),
        ("code_stdin", None),
    ]
    resolved = _resolve_cells(parsed)
    assert resolved == [
        ("markdown", "## inline header"),
        ("code", "print('file')\n"),
        ("markdown", "stdin markdown"),
        ("code", "x = 42"),
        ("markdown", "# from file\n"),
        ("code", "print('stdin code')"),
    ]


def test_resolve_no_stdin_no_file_passes_through() -> None:
    parsed = [("markdown", "A"), ("code", "B")]
    assert _resolve_cells(parsed) == [("markdown", "A"), ("code", "B")]


# --------------------------------------------------------------------- #
# edit-cell argparse layer
# --------------------------------------------------------------------- #


def test_edit_cell_requires_source_flag() -> None:
    with pytest.raises(SystemExit):
        _parse_edit()


def test_edit_cell_mutually_exclusive_source_flags() -> None:
    with pytest.raises(SystemExit):
        _parse_edit("--source", "x", "--source-file", "y.py")


def test_edit_cell_inline_source() -> None:
    args = _parse_edit("--source", "print(1)")
    assert args.cell_id == "cell-id-1"
    assert args.source == "print(1)"
    assert args.source_file is None
    assert args.keep_outputs is False


def test_edit_cell_source_file() -> None:
    args = _parse_edit("--source-file", "./snippet.py")
    assert args.source is None
    assert args.source_file == "./snippet.py"


def test_edit_cell_stdin_sentinel_preserved() -> None:
    """argparse should pass '-' through; resolution happens later."""
    args = _parse_edit("--source", "-")
    assert args.source == "-"


def test_edit_cell_keep_outputs_flag() -> None:
    args = _parse_edit("--source", "x = 1", "--keep-outputs")
    assert args.keep_outputs is True


# --------------------------------------------------------------------- #
# _resolve_single_source
# --------------------------------------------------------------------- #


def test_resolve_single_source_inline() -> None:
    assert _resolve_single_source("hello", None) == "hello"


def test_resolve_single_source_file(tmp_path) -> None:
    p = tmp_path / "snip.py"
    p.write_text("print('file')\n", encoding="utf-8")
    assert _resolve_single_source(None, str(p)) == "print('file')\n"


def test_resolve_single_source_file_preserves_shell_hostile_chars(tmp_path) -> None:
    """edit-cell --source-file must round-trip backticks/$(...) verbatim."""
    p = tmp_path / "snip.py"
    p.write_text(_SHELL_HOSTILE_SRC, encoding="utf-8")
    assert _resolve_single_source(None, str(p)) == _SHELL_HOSTILE_SRC


@pytest.mark.parametrize("bad", ["see `path`", "x = $(cmd)"])
def test_resolve_single_source_inline_backtick_or_subst_refused(bad) -> None:
    with pytest.raises(SystemExit) as exc:
        _resolve_single_source(bad, None)
    msg = str(exc.value)
    assert "--source" in msg and "--source-file" in msg


def test_resolve_single_source_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_stdin(monkeypatch, "from stdin\nmulti line\n")
    assert _resolve_single_source("-", None) == "from stdin\nmulti line\n"


def test_resolve_single_source_stdin_tty_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_stdin(monkeypatch, "", tty=True)
    with pytest.raises(SystemExit) as exc:
        _resolve_single_source("-", None)
    assert "tty" in str(exc.value)


def test_resolve_single_source_missing_file(tmp_path) -> None:
    missing = tmp_path / "nope.py"
    with pytest.raises(SystemExit) as exc:
        _resolve_single_source(None, str(missing))
    assert "file not found" in str(exc.value)


def test_resolve_single_source_non_utf8(tmp_path) -> None:
    p = tmp_path / "bin.py"
    p.write_bytes(b"\xff\xfe\x00\x00")
    with pytest.raises(SystemExit) as exc:
        _resolve_single_source(None, str(p))
    assert "UTF-8" in str(exc.value)


def test_resolve_single_source_neither_provided() -> None:
    with pytest.raises(SystemExit):
        _resolve_single_source(None, None)


def test_resolve_single_source_both_provided() -> None:
    with pytest.raises(SystemExit):
        _resolve_single_source("text", "path")


# --------------------------------------------------------------------- #
# Policy helpers
# --------------------------------------------------------------------- #


class _FakeClient:
    """Stand-in for NbModelClient.get_notebook_metadata calls."""

    def __init__(self, hera_meta) -> None:
        self._meta = hera_meta

    def get_notebook_metadata(self, key, default=None):
        if key == "hera":
            return self._meta if self._meta is not None else default
        return default


def test_read_policy_missing_defaults_to_append_only() -> None:
    assert _read_policy(_FakeClient(None)) == POLICY_APPEND_ONLY


def test_read_policy_explicit_append_only() -> None:
    assert _read_policy(_FakeClient({"policy": POLICY_APPEND_ONLY})) == POLICY_APPEND_ONLY


def test_read_policy_edit_no_exec() -> None:
    assert _read_policy(_FakeClient({"policy": POLICY_EDIT_NO_EXEC})) == POLICY_EDIT_NO_EXEC


def test_read_policy_edit_exec() -> None:
    assert _read_policy(_FakeClient({"policy": POLICY_EDIT_EXEC})) == POLICY_EDIT_EXEC


def test_read_policy_append_exec() -> None:
    assert _read_policy(_FakeClient({"policy": POLICY_APPEND_EXEC})) == POLICY_APPEND_EXEC


def test_read_policy_unknown_value_falls_back_to_append_only() -> None:
    """Defensive: a typo in the metadata shouldn't accidentally grant write access."""
    assert _read_policy(_FakeClient({"policy": "edit_evrything"})) == POLICY_APPEND_ONLY


def test_read_policy_wrong_type_falls_back() -> None:
    """A non-dict 'hera' (e.g. the legacy cell-level 'v0' string) yields the safe default."""
    assert _read_policy(_FakeClient("v0")) == POLICY_APPEND_ONLY


def test_require_policy_allows_matching() -> None:
    client = _FakeClient({"policy": POLICY_EDIT_NO_EXEC})
    assert _require_policy(client, EDIT_POLICIES, "edit-cell") == POLICY_EDIT_NO_EXEC


def test_require_policy_refuses_append_only_for_edit() -> None:
    client = _FakeClient({"policy": POLICY_APPEND_ONLY})
    with pytest.raises(SystemExit) as exc:
        _require_policy(client, EDIT_POLICIES, "edit-cell")
    msg = str(exc.value)
    assert "append_only" in msg
    assert "edit-cell" in msg


def test_require_policy_refuses_edit_no_exec_for_execute() -> None:
    client = _FakeClient({"policy": POLICY_EDIT_NO_EXEC})
    with pytest.raises(SystemExit) as exc:
        _require_policy(client, EXECUTE_POLICIES, "execute-cell")
    assert POLICY_EDIT_NO_EXEC in str(exc.value)


def test_require_policy_missing_metadata_refuses_edit() -> None:
    """Belt-and-suspenders: in-flight notebooks without the field must not be editable."""
    client = _FakeClient(None)
    with pytest.raises(SystemExit) as exc:
        _require_policy(client, EDIT_POLICIES, "edit-cell")
    assert "append_only" in str(exc.value)


def test_append_exec_allows_execute() -> None:
    client = _FakeClient({"policy": POLICY_APPEND_EXEC})
    assert _require_policy(client, EXECUTE_POLICIES, "execute-cell") == POLICY_APPEND_EXEC


def test_append_exec_refuses_edit() -> None:
    """The append-only record contract: append_exec can run cells but not rewrite them."""
    client = _FakeClient({"policy": POLICY_APPEND_EXEC})
    with pytest.raises(SystemExit) as exc:
        _require_policy(client, EDIT_POLICIES, "edit-cell")
    assert POLICY_APPEND_EXEC in str(exc.value)


def test_append_exec_refuses_delete() -> None:
    """delete stays edit_exec-only; append_exec must never remove a measure cell."""
    client = _FakeClient({"policy": POLICY_APPEND_EXEC})
    with pytest.raises(SystemExit) as exc:
        _require_policy(client, DELETE_POLICIES, "delete-cell")
    assert POLICY_APPEND_EXEC in str(exc.value)


def test_edit_exec_still_allows_delete() -> None:
    client = _FakeClient({"policy": POLICY_EDIT_EXEC})
    assert _require_policy(client, DELETE_POLICIES, "delete-cell") == POLICY_EDIT_EXEC


# --------------------------------------------------------------------- #
# append --wait / --execute end-to-end (fake RTC client) — policy gating
# --------------------------------------------------------------------- #


class _FakeAppendClient:
    """Async-context stand-in for NbModelClient covering exactly the surface
    ``_append`` touches: sync, notebook/cell metadata, and cell adders."""

    def __init__(self, policy: str = POLICY_APPEND_ONLY) -> None:
        self._policy = policy
        self._cells: list[dict] = []

    async def __aenter__(self) -> "_FakeAppendClient":
        return self

    async def __aexit__(self, *exc) -> bool:  # noqa: ANN002
        return False

    async def wait_until_synced(self) -> None:
        return None

    def get_notebook_metadata(self, key, default=None):
        return {"policy": self._policy} if key == "hera" else default

    def __len__(self) -> int:
        return len(self._cells)

    def __getitem__(self, idx: int) -> dict:
        return self._cells[idx]

    def add_markdown_cell(self, src: str) -> int:
        self._cells.append(
            {"id": f"md{len(self._cells)}", "cell_type": "markdown", "metadata": {}, "source": src}
        )
        return len(self._cells) - 1

    def add_code_cell(self, src: str) -> int:
        self._cells.append(
            {
                "id": f"code{len(self._cells)}",
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "source": src,
            }
        )
        return len(self._cells) - 1

    def get_cell_metadata(self, idx, key, default=None):
        return self._cells[idx]["metadata"].get(key, default)

    def set_cell_metadata(self, idx, key, value) -> None:
        self._cells[idx]["metadata"][key] = value


def _patch_append_server(monkeypatch, tmp_path, client) -> Path:
    """Stub server discovery + RTC client so ``_append`` runs without JupyterLab."""
    nb_path = tmp_path / "m.ipynb"
    _write_nb(
        nb_path,
        minor=5,
        cells=[{"cell_type": "code", "id": "a" * 32, "metadata": {}, "source": "", "outputs": [], "execution_count": None}],
    )
    monkeypatch.setattr(nb_collab, "_resolve_with_overrides", lambda p, s, t: ("http://s", "tok", tmp_path))
    monkeypatch.setattr(nb_collab, "get_jupyter_notebook_websocket_url", lambda *a, **k: "ws://room")
    monkeypatch.setattr(nb_collab, "NbModelClient", lambda *a, **k: client)
    return nb_path


def test_append_wait_routes_to_wait_under_append_only(monkeypatch, tmp_path) -> None:
    """--wait is permitted under append_only (the E0 measure policy): it appends,
    then hands the last appended code cell to _wait — no policy SystemExit."""
    client = _FakeAppendClient(POLICY_APPEND_ONLY)
    nb_path = _patch_append_server(monkeypatch, tmp_path, client)

    captured: dict[str, object] = {}

    async def fake_wait(notebook, cell_id, timeout, poll, wait_for_rerun, su, tok):  # noqa: ANN001
        captured.update(cell_id=cell_id, timeout=timeout, poll=poll, rerun=wait_for_rerun)
        return 0

    monkeypatch.setattr(nb_collab, "_wait", fake_wait)

    rc = asyncio.run(
        nb_collab._append(
            nb_path, [("markdown", "m"), ("code", "c")], "http://s", "tok",
            0.0, False, True, True, 570.0, 0.01,
        )
    )
    assert rc == 0
    # md is cell 0, the code cell is 1 — wait binds the last appended code cell.
    assert captured["cell_id"] == "code1"
    # --follow lifts the deadline; the default (not --wait-for-rerun) baseline waits
    # for the first execution.
    assert captured["timeout"] is None
    assert captured["rerun"] is False


def test_append_wait_passes_finite_timeout_without_follow(monkeypatch, tmp_path) -> None:
    client = _FakeAppendClient(POLICY_APPEND_ONLY)
    nb_path = _patch_append_server(monkeypatch, tmp_path, client)
    captured: dict[str, object] = {}

    async def fake_wait(notebook, cell_id, timeout, poll, wait_for_rerun, su, tok):  # noqa: ANN001
        captured["timeout"] = timeout
        return 0

    monkeypatch.setattr(nb_collab, "_wait", fake_wait)
    asyncio.run(
        nb_collab._append(
            nb_path, [("code", "c")], "http://s", "tok",
            0.0, False, True, False, 123.0, 0.01,
        )
    )
    assert captured["timeout"] == 123.0


def test_append_execute_gated_under_append_only(monkeypatch, tmp_path) -> None:
    """Contrast with --wait: --execute IS policy-gated and refuses append_only."""
    client = _FakeAppendClient(POLICY_APPEND_ONLY)
    nb_path = _patch_append_server(monkeypatch, tmp_path, client)

    def _no_wait(*a, **k):  # _wait must never be reached on the execute path
        raise AssertionError("_wait should not be called for --execute")

    monkeypatch.setattr(nb_collab, "_wait", _no_wait)
    with pytest.raises(SystemExit) as exc:
        asyncio.run(
            nb_collab._append(
                nb_path, [("code", "c")], "http://s", "tok",
                0.0, True, False, False, 570.0, 0.01,
            )
        )
    msg = str(exc.value)
    assert "append --execute" in msg
    assert POLICY_APPEND_EXEC in msg


def test_append_wait_requires_code_cell(monkeypatch, tmp_path) -> None:
    """--wait needs a code cell to bind to — a markdown-only append errors before
    any wait is armed (markdown cells have no execution_count to flip)."""
    client = _FakeAppendClient(POLICY_APPEND_ONLY)
    nb_path = _patch_append_server(monkeypatch, tmp_path, client)

    def _no_wait(*a, **k):
        raise AssertionError("_wait should not be reached without a code cell")

    monkeypatch.setattr(nb_collab, "_wait", _no_wait)
    with pytest.raises(SystemExit) as exc:
        asyncio.run(
            nb_collab._append(
                nb_path, [("markdown", "m")], "http://s", "tok",
                0.0, False, True, False, 570.0, 0.01,
            )
        )
    assert "requires an appended code cell" in str(exc.value)


def test_append_summary_and_eta_render_into_first_markdown_cell_and_stamp(
    monkeypatch, tmp_path
) -> None:
    """End-to-end wiring: the rendered line lands in the first markdown cell's
    source before it's added, and metadata.hera picks up summary/eta_at
    alongside the appended_at every cell already gets."""
    client = _FakeAppendClient(POLICY_APPEND_ONLY)
    nb_path = _patch_append_server(monkeypatch, tmp_path, client)

    rc = asyncio.run(
        nb_collab._append(
            nb_path,
            [("markdown", "# Plan\nDetails here"), ("code", "sweep()")],
            "http://s", "tok",
            0.0, False, False, False, 570.0, 0.01,
            "check the pocket", 40,
        )
    )
    assert rc == 0

    md_cell = client._cells[0]
    src = md_cell["source"]
    assert src.startswith("# Plan\n\n")
    assert src.endswith("\n\nDetails here")
    assert "> **" in src
    assert "check the pocket" in src
    assert "**ETA ~" in src
    assert "(≈40 min)" in src

    hera_meta = md_cell["metadata"]["hera"]
    assert hera_meta["summary"] == "check the pocket"
    assert "appended_at" in hera_meta
    assert datetime.fromisoformat(hera_meta["eta_at"]).tzinfo is not None

    # Code cell (not the target of the rendered line) is untouched and still
    # gets its own appended_at.
    code_cell = client._cells[1]
    assert code_cell["source"] == "sweep()"
    assert "summary" not in code_cell["metadata"]["hera"]


def test_append_without_summary_or_eta_leaves_markdown_source_untouched(
    monkeypatch, tmp_path
) -> None:
    """No behavior change when neither flag is passed."""
    client = _FakeAppendClient(POLICY_APPEND_ONLY)
    nb_path = _patch_append_server(monkeypatch, tmp_path, client)

    rc = asyncio.run(
        nb_collab._append(
            nb_path, [("markdown", "# Plan\nDetails here")], "http://s", "tok",
            0.0, False, False, False, 570.0, 0.01,
        )
    )
    assert rc == 0
    md_cell = client._cells[0]
    assert md_cell["source"] == "# Plan\nDetails here"
    hera_meta = md_cell["metadata"]["hera"]
    assert "summary" not in hera_meta
    assert "eta_at" not in hera_meta


def test_append_eta_echoed_to_stdout(monkeypatch, tmp_path, capsys) -> None:
    client = _FakeAppendClient(POLICY_APPEND_ONLY)
    nb_path = _patch_append_server(monkeypatch, tmp_path, client)

    asyncio.run(
        nb_collab._append(
            nb_path, [("markdown", "# Plan")], "http://s", "tok",
            0.0, False, False, False, 570.0, 0.01,
            None, 40,
        )
    )
    out = capsys.readouterr().out
    assert "eta: ~" in out
    assert "(≈40 min)" in out


# --------------------------------------------------------------------- #
# execute-cell argparse
# --------------------------------------------------------------------- #


def _parse_exec(*argv: str):
    return _build_parser().parse_args(["execute-cell", "x.ipynb", "cid", *argv])


def test_execute_cell_minimal() -> None:
    args = _parse_exec()
    assert args.notebook.name == "x.ipynb"
    assert args.cell_id == "cid"
    assert args.timeout > 0  # has a default


def test_execute_cell_custom_timeout() -> None:
    args = _parse_exec("--timeout", "30")
    assert args.timeout == 30.0


def test_execute_cell_requires_cell_id() -> None:
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["execute-cell", "x.ipynb"])


# --------------------------------------------------------------------- #
# delete-cell argparse
# --------------------------------------------------------------------- #


def _parse_delete(*argv: str):
    return _build_parser().parse_args(["delete-cell", "x.ipynb", "cid", *argv])


def test_delete_cell_minimal() -> None:
    args = _parse_delete()
    assert args.notebook.name == "x.ipynb"
    assert args.cell_id == "cid"


def test_delete_cell_requires_cell_id() -> None:
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["delete-cell", "x.ipynb"])


def test_delete_cell_accepts_settle_override() -> None:
    args = _parse_delete("--settle", "1.5")
    assert args.settle == 1.5


# --------------------------------------------------------------------- #
# legacy nbformat warning (regression guard against the YDoc-room-bloat bug)
# --------------------------------------------------------------------- #


def _write_nb(path, *, minor: int, cells: list[dict]) -> None:
    nb = {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": minor}
    path.write_text(json.dumps(nb), encoding="utf-8")


def test_warn_legacy_fires_on_nbformat_44_no_ids(tmp_path, capsys) -> None:
    nb_path = tmp_path / "legacy.ipynb"
    _write_nb(
        nb_path,
        minor=4,
        cells=[
            {"cell_type": "markdown", "metadata": {}, "source": "hi"},
            {"cell_type": "code", "metadata": {}, "source": "x = 1", "outputs": [], "execution_count": None},
        ],
    )
    _warn_if_legacy_format(nb_path)
    err = capsys.readouterr().err
    assert "legacy nbformat 4.4" in err
    assert "2/2 cells missing IDs" in err


def test_warn_legacy_silent_on_nbformat_45_with_ids(tmp_path, capsys) -> None:
    nb_path = tmp_path / "modern.ipynb"
    _write_nb(
        nb_path,
        minor=5,
        cells=[
            {"cell_type": "markdown", "id": "a" * 32, "metadata": {}, "source": "hi"},
        ],
    )
    _warn_if_legacy_format(nb_path)
    assert capsys.readouterr().err == ""


def test_warn_legacy_fires_on_partial_ids(tmp_path, capsys) -> None:
    """Even at minor=5, a single ID-less cell trips the warning."""
    nb_path = tmp_path / "mixed.ipynb"
    _write_nb(
        nb_path,
        minor=5,
        cells=[
            {"cell_type": "markdown", "id": "a" * 32, "metadata": {}, "source": "hi"},
            {"cell_type": "markdown", "metadata": {}, "source": "missing id"},
        ],
    )
    _warn_if_legacy_format(nb_path)
    err = capsys.readouterr().err
    assert "1/2 cells missing IDs" in err


def test_warn_legacy_silent_on_malformed_json(tmp_path, capsys) -> None:
    """Don't print the cell-ID warning over a parse error — let the
    downstream open-and-fail report it precisely."""
    nb_path = tmp_path / "broken.ipynb"
    nb_path.write_text("{ this is not json", encoding="utf-8")
    _warn_if_legacy_format(nb_path)
    assert capsys.readouterr().err == ""


# --------------------------------------------------------------------- #
# Cell-landing timestamps (_utc_now_iso / _stamp_cell_event)
# --------------------------------------------------------------------- #


class _FakeCellClient:
    """Minimal stand-in for NbModelClient's per-cell metadata accessors.

    Backs a list of cells, each a dict with a "metadata" dict, matching the
    real get_cell_metadata(index, key, default) / set_cell_metadata(index,
    key, value) semantics (set replaces the key wholesale).
    """

    def __init__(self, cells: list[dict]) -> None:
        self._cells = cells

    def get_cell_metadata(self, index, key, default=None):
        return self._cells[index]["metadata"].get(key, default)

    def set_cell_metadata(self, index, key, value):
        self._cells[index]["metadata"][key] = value


def test_utc_now_iso_is_timezone_aware_and_utc() -> None:
    ts = _utc_now_iso()
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None
    # UTC offset is exactly zero — unambiguous across PT/EDT operators.
    assert parsed.utcoffset() == timedelta(0)
    assert ts.endswith("+00:00")


def test_stamp_appended_at_writes_dict() -> None:
    client = _FakeCellClient([{"metadata": {}}])
    _stamp_cell_event(client, 0, "appended_at", "2026-06-11T18:30:00+00:00")
    hera = client.get_cell_metadata(0, HERA_TAG_KEY)
    assert hera == {"v": HERA_CELL_VERSION, "appended_at": "2026-06-11T18:30:00+00:00"}


def test_stamp_edit_merges_without_clobbering_append() -> None:
    """A later edit/execute stamp must preserve the earlier appended_at."""
    client = _FakeCellClient([{"metadata": {}}])
    _stamp_cell_event(client, 0, "appended_at", "2026-06-11T18:30:00+00:00")
    _stamp_cell_event(client, 0, "edited_at", "2026-06-11T18:45:00+00:00")
    hera = client.get_cell_metadata(0, HERA_TAG_KEY)
    assert hera == {
        "v": HERA_CELL_VERSION,
        "appended_at": "2026-06-11T18:30:00+00:00",
        "edited_at": "2026-06-11T18:45:00+00:00",
    }


def test_stamp_upgrades_legacy_string_in_place() -> None:
    """A cell carrying the legacy bare 'v0' string is replaced by a dict."""
    client = _FakeCellClient([{"metadata": {"hera": "v0"}}])
    _stamp_cell_event(client, 0, "executed_at", "2026-06-11T19:00:00+00:00")
    hera = client.get_cell_metadata(0, HERA_TAG_KEY)
    assert hera == {"v": HERA_CELL_VERSION, "executed_at": "2026-06-11T19:00:00+00:00"}


def test_stamp_uses_timezone_aware_timestamp_end_to_end() -> None:
    """The value produced by the real clock helper parses back tz-aware."""
    client = _FakeCellClient([{"metadata": {}}])
    _stamp_cell_event(client, 0, "appended_at", _utc_now_iso())
    stamped = client.get_cell_metadata(0, HERA_TAG_KEY)["appended_at"]
    assert datetime.fromisoformat(stamped).tzinfo is not None


# --------------------------------------------------------------------- #
# append --summary / --eta — pure helpers
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text, minutes",
    [("40m", 40), ("2h", 120), ("1h30m", 90), ("90m", 90)],
)
def test_parse_eta_minutes_accepts_valid_forms(text, minutes) -> None:
    assert _parse_eta_minutes(text) == minutes


@pytest.mark.parametrize(
    "text",
    ["40", "1.5h", "", "h", "m", "0m", "-5m", "30m1h"],
)
def test_parse_eta_minutes_rejects_invalid_forms(text) -> None:
    with pytest.raises(ValueError):
        _parse_eta_minutes(text)


def test_parse_eta_minutes_bare_number_names_the_suffix() -> None:
    """A bare number gets a pointed nudge rather than a generic parse error."""
    with pytest.raises(ValueError) as exc:
        _parse_eta_minutes("40")
    msg = str(exc.value)
    assert "40m" in msg
    assert "40h" in msg


def test_render_duration_display_under_hour() -> None:
    assert _render_duration_display(40) == "≈40 min"


def test_render_duration_display_exact_hours() -> None:
    assert _render_duration_display(120) == "≈2h"


def test_render_duration_display_hours_and_minutes() -> None:
    assert _render_duration_display(90) == "≈1h30m"


def test_render_summary_line_summary_and_eta() -> None:
    appended = "2026-01-01T12:00:00+00:00"
    local = datetime.fromisoformat(appended).astimezone()
    eta_local = local + timedelta(minutes=40)
    expected = (
        f"> **{local.strftime('%H:%M')}** · check the pocket · "
        f"**ETA ~{eta_local.strftime('%H:%M')}** (≈40 min)"
    )
    assert _render_summary_line(appended, "check the pocket", 40) == expected


def test_render_summary_line_summary_only() -> None:
    appended = "2026-01-01T12:00:00+00:00"
    local = datetime.fromisoformat(appended).astimezone()
    expected = f"> **{local.strftime('%H:%M')}** · quick check"
    assert _render_summary_line(appended, "quick check", None) == expected


def test_render_summary_line_eta_only() -> None:
    appended = "2026-01-01T12:00:00+00:00"
    local = datetime.fromisoformat(appended).astimezone()
    eta_local = local + timedelta(minutes=90)
    expected = (
        f"> **{local.strftime('%H:%M')}** · "
        f"**ETA ~{eta_local.strftime('%H:%M')}** (≈1h30m)"
    )
    assert _render_summary_line(appended, None, 90) == expected


def test_render_summary_line_no_eta_no_summary_is_just_the_clock() -> None:
    appended = "2026-01-01T12:00:00+00:00"
    local = datetime.fromisoformat(appended).astimezone()
    assert _render_summary_line(appended, None, None) == f"> **{local.strftime('%H:%M')}**"


def test_render_summary_line_escapes_markdown_in_summary() -> None:
    """A spec like ``n_e`` must not italicize inside the blockquote."""
    appended = "2026-01-01T12:00:00+00:00"
    line = _render_summary_line(appended, "n_e ramp *fast* 2x", None)
    assert r"n\_e ramp \*fast\* 2x" in line


def test_escape_md() -> None:
    assert _escape_md("n_e *x* a\\b") == r"n\_e \*x\* a\\b"
    assert _escape_md("plain: 2.8-6.0 T {base,10} K") == "plain: 2.8-6.0 T {base,10} K"


def test_render_summary_line_cross_midnight_adds_day_marker() -> None:
    """Force local tz to UTC (deterministic regardless of the runner's tz) so
    the +40min ETA from 23:50 provably crosses into the next calendar day."""
    old_tz = os.environ.get("TZ")
    os.environ["TZ"] = "UTC"
    time.tzset()
    try:
        line = _render_summary_line("2026-01-01T23:50:00+00:00", None, 40)
        assert line == "> **23:50** · **ETA ~00:30 (+1d)** (≈40 min)"
    finally:
        if old_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old_tz
        time.tzset()


def test_render_summary_line_same_day_has_no_day_marker() -> None:
    old_tz = os.environ.get("TZ")
    os.environ["TZ"] = "UTC"
    time.tzset()
    try:
        line = _render_summary_line("2026-01-01T12:00:00+00:00", None, 40)
        assert "+1d" not in line
        assert "(+" not in line
    finally:
        if old_tz is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = old_tz
        time.tzset()


def test_render_eta_clock_agrees_with_summary_line() -> None:
    """The stdout echo (_render_eta_clock) and the in-cell line render the
    same clock and duration, differing only in markdown emphasis."""
    appended = "2026-01-01T12:00:00+00:00"
    eta_clause = _render_eta_clock(appended, 40)
    line = _render_summary_line(appended, None, 40)
    clock, _, duration = eta_clause.partition(" ")
    assert eta_clause.startswith("~")
    assert clock in line
    assert duration in line


def test_insert_after_heading_on_first_line() -> None:
    src = "# Title\nSome text"
    assert _insert_after_heading(src, "LINE") == "# Title\n\nLINE\n\nSome text"


def test_insert_after_heading_after_leading_blank_lines() -> None:
    src = "\n\n# Title\nSome text"
    assert _insert_after_heading(src, "LINE") == "\n\n# Title\n\nLINE\n\nSome text"


def test_insert_after_heading_no_heading_prepends_line() -> None:
    src = "Some text\nmore text"
    assert _insert_after_heading(src, "LINE") == "LINE\n\nSome text\nmore text"


def test_insert_after_heading_no_double_blank_when_already_present() -> None:
    """A markdown cell already shaped heading/blank/content must not gain a
    second blank line between the heading and the inserted line."""
    src = "# Title\n\nSome text"
    assert _insert_after_heading(src, "LINE") == "# Title\n\nLINE\n\nSome text"


# --------------------------------------------------------------------- #
# wait timeout — loud, unmistakable message (T-3)
# --------------------------------------------------------------------- #


def test_timeout_message_is_loud_and_names_running_state() -> None:
    msg = _timeout_message("cell-abc", 570.0, 12)
    assert "TIMED OUT" in msg
    assert "STILL RUNNING" in msg
    assert "did NOT finish" in msg
    assert "cell-abc" in msg


def test_timeout_message_surfaces_timeout_value() -> None:
    assert "570s" in _timeout_message("cid", 570.0, None)
    assert "60s" in _timeout_message("cid", 60.0, None)


def test_timeout_message_includes_last_execution_count() -> None:
    assert "12" in _timeout_message("cid", 1.0, 12)
    assert "None" in _timeout_message("cid", 1.0, None)


def test_exec_timeout_message_is_loud_and_names_running_state() -> None:
    msg = _exec_timeout_message("cell-xyz", 570.0)
    assert "TIMED OUT" in msg
    assert "STILL RUNNING" in msg
    assert "NOT a failure" in msg
    assert "cell-xyz" in msg


def test_exec_timeout_message_surfaces_timeout_value() -> None:
    assert "570s" in _exec_timeout_message("cid", 570.0)
    assert "60s" in _exec_timeout_message("cid", 60.0)


def test_run_cell_timeout_returns_exit_timeout(monkeypatch, tmp_path, capsys) -> None:
    # A client-side TimeoutError (kernel still running) must return EXIT_TIMEOUT
    # with a loud stderr line — not propagate as a generic exit-1 failure.
    conn = tmp_path / "kernel-x.json"
    conn.write_text("{}")
    monkeypatch.setattr(nb_collab, "_find_or_create_kernel", lambda *a: "kid-1")
    monkeypatch.setattr(nb_collab, "_kernel_connection_file", lambda kid: conn)

    class _FakeKC:
        def load_connection_file(self, *a) -> None: ...
        def start_channels(self) -> None: ...
        def wait_for_ready(self, timeout=None) -> None: ...
        def stop_channels(self) -> None: ...

    monkeypatch.setattr(nb_collab, "BlockingKernelClient", _FakeKC)

    class _FakeExecClient:
        def execute_cell(self, idx, kc, timeout=None):
            raise TimeoutError("Timeout waiting for output")

    rc = nb_collab._run_cell_on_open_client(
        _FakeExecClient(), 3, "cell-xyz", "http://s", "tok", "nb.ipynb", 570.0
    )
    assert rc == nb_collab.EXIT_TIMEOUT
    out = capsys.readouterr()
    assert "STILL RUNNING" in out.err
    assert "cell-xyz" in out.err
    assert "status: TIMEOUT" in out.out


def test_wait_timeout_flag_default_and_override() -> None:
    args = _build_parser().parse_args(["wait", "x.ipynb", "cid"])
    assert args.timeout == DEFAULT_WAIT_TIMEOUT
    args = _build_parser().parse_args(["wait", "x.ipynb", "cid", "--timeout", "1200"])
    assert args.timeout == 1200.0


def test_wait_default_timeout_is_generous() -> None:
    # Raised from the old 570s sub-Bash-cap value: 570s clean-timed-out mid-run
    # on multi-hour E1 sweeps and read as completion. 30 min covers the start-
    # gate + medium sweeps; --follow handles multi-hour.
    assert DEFAULT_WAIT_TIMEOUT == 1800.0


def test_wait_follow_flag_defaults_false_and_parses() -> None:
    args = _build_parser().parse_args(["wait", "x.ipynb", "cid"])
    assert args.follow is False
    args = _build_parser().parse_args(["wait", "x.ipynb", "cid", "--follow"])
    assert args.follow is True


def test_cmd_wait_follow_lifts_deadline(monkeypatch: pytest.MonkeyPatch) -> None:
    # --follow must hand _wait timeout=None (no deadline) for backgrounded
    # multi-hour waits; otherwise the finite --timeout is passed through.
    captured: dict[str, object] = {}

    async def fake_wait(notebook, cell_id, timeout, *rest):  # noqa: ANN001
        captured["timeout"] = timeout
        return 0

    monkeypatch.setattr(nb_collab, "_wait", fake_wait)

    nb_collab._cmd_wait(_build_parser().parse_args(["wait", "x.ipynb", "cid", "--follow"]))
    assert captured["timeout"] is None

    nb_collab._cmd_wait(_build_parser().parse_args(["wait", "x.ipynb", "cid"]))
    assert captured["timeout"] == DEFAULT_WAIT_TIMEOUT


# --------------------------------------------------------------------- #
# interrupt — argparse + running-cell guard + kernel find-only
# --------------------------------------------------------------------- #


def _parse_interrupt(*argv: str):
    return _build_parser().parse_args(["interrupt", "x.ipynb", *argv])


def test_interrupt_minimal_no_cell_id() -> None:
    args = _parse_interrupt()
    assert args.notebook.name == "x.ipynb"
    assert args.cell_id is None  # bare interrupt targets whatever is running
    assert args.confirm_timeout > 0


def test_interrupt_with_cell_id() -> None:
    args = _parse_interrupt("--cell-id", "abc")
    assert args.cell_id == "abc"


def test_interrupt_custom_confirm_timeout_and_poll() -> None:
    args = _parse_interrupt("--cell-id", "abc", "--confirm-timeout", "5", "--poll", "0.2")
    assert args.confirm_timeout == 5.0
    assert args.poll == 0.2


def test_interrupt_requires_notebook() -> None:
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["interrupt"])


def test_cell_is_running_requires_busy_kernel_and_null_count() -> None:
    # running: kernel busy AND the cell hasn't completed (execution_count None)
    assert _cell_is_running({"execution_count": None}, "busy") is True
    # completed cell (count set) — e.g. it finished and the operator moved on
    assert _cell_is_running({"execution_count": 7}, "busy") is False
    # kernel idle — nothing is running
    assert _cell_is_running({"execution_count": None}, "idle") is False
    assert _cell_is_running({"execution_count": None}, None) is False
    # freshly appended cell, idle kernel
    assert _cell_is_running({}, "idle") is False


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:  # noqa: ANN002
        return None

    def read(self) -> bytes:
        return self._payload


def _fake_sessions(monkeypatch, sessions: list[dict]) -> None:
    payload = json.dumps(sessions).encode("utf-8")
    monkeypatch.setattr(
        nb_collab.urllib.request,
        "urlopen",
        lambda *a, **k: _FakeResponse(payload),
    )


def test_find_kernel_for_path_matches(monkeypatch) -> None:
    _fake_sessions(
        monkeypatch,
        [
            {"notebook": {"path": "other.ipynb"}, "kernel": {"id": "k-other"}},
            {"notebook": {"path": "z/measure.ipynb"}, "kernel": {"id": "k-1"}},
        ],
    )
    assert _find_kernel_for_path("http://s", "tok", "z/measure.ipynb") == "k-1"


def test_find_kernel_for_path_none_when_no_session(monkeypatch) -> None:
    """Find-only: a notebook with no running session yields None (interrupt then
    refuses instead of spawning a kernel)."""
    _fake_sessions(monkeypatch, [{"notebook": {"path": "other.ipynb"}, "kernel": {"id": "k"}}])
    assert _find_kernel_for_path("http://s", "tok", "z/measure.ipynb") is None


def test_rel_path_nested_forward_slash(tmp_path) -> None:
    """Production helper: a nested notebook resolves to a forward-slash rel_path.

    Exercises ``_rel_path`` end-to-end with real OS paths. On Windows this would
    catch the bug directly (native ``str`` gives backslashes); on Linux it pins
    the forward-slash contract. The path is two dirs deep — a root-level notebook
    has no separator, which is exactly why the win11-vm e2e missed the fork.
    """
    root = tmp_path
    nb = root / "zack" / "20260616-QC0426" / "20260616_measure.ipynb"
    nb.parent.mkdir(parents=True)
    nb.write_text("{}", encoding="utf-8")
    rel = _rel_path(nb, root)
    assert rel == "zack/20260616-QC0426/20260616_measure.ipynb"
    assert "\\" not in rel


def test_rel_path_normalizes_windows_separators(monkeypatch) -> None:
    """OS-independent reproduction of the dgg-vti kernel fork.

    ``PureWindowsPath`` models the Windows separator on any host: its ``str``
    always uses backslashes (the old ``str(...).relative_to`` form — the bug),
    while ``as_posix`` yields the forward-slash form Jupyter's session API
    stores. With both the live sessions present (forward-slash kernel
    ``d6d0fa97`` = operator's instrument kernel; backslash kernel ``6e9d8502``
    = the stray fresh one nb-collab spawned), the normalized rel_path must bind
    to ``d6d0fa97`` — the exact failure execute-cell hit live.
    """
    win_root = PureWindowsPath(r"C:\Users\toploader\measurements")
    win_nb = win_root / "zack" / "20260616-QC0426" / "20260616_measure.ipynb"
    rel_native = str(win_nb.relative_to(win_root))
    rel_norm = win_nb.relative_to(win_root).as_posix()

    # The old code path: native str() on a Windows relative path → backslashes.
    assert "\\" in rel_native
    # The fix: forward-slash, nested, matching Jupyter's notebook.path form.
    assert rel_norm == "zack/20260616-QC0426/20260616_measure.ipynb"

    _fake_sessions(
        monkeypatch,
        [
            {
                "notebook": {"path": "zack/20260616-QC0426/20260616_measure.ipynb"},
                "kernel": {"id": "d6d0fa97"},
            },
            {
                "notebook": {"path": r"zack\20260616-QC0426\20260616_measure.ipynb"},
                "kernel": {"id": "6e9d8502"},
            },
        ],
    )
    # Normalized rel_path binds the operator's live kernel; the old backslash
    # form would have matched the stray fresh kernel (6e9d8502) instead.
    assert _find_kernel_for_path("http://s", "tok", rel_norm) == "d6d0fa97"
    assert _find_kernel_for_path("http://s", "tok", rel_native) == "6e9d8502"


def test_exit_not_running_code_distinct() -> None:
    """The 'cell not executing' path has its own exit code so HERA can tell a
    benign no-op from an error."""
    assert EXIT_NOT_RUNNING == 4
    assert len({0, 1, 2, 3, EXIT_NOT_RUNNING}) == 5


# --------------------------------------------------------------------- #
# output-tail collapse (sweep progress-bar spam)
# --------------------------------------------------------------------- #


def _progress_dd() -> dict:
    """A sweep-progress-bar display_data output as stored under RTC — the
    text/plain placeholder is what the tail concatenates."""
    return {
        "output_type": "display_data",
        "data": {
            "text/html": "<div>bar</div>",
            "text/plain": "<IPython.core.display.HTML object>",
        },
    }


def test_output_tail_collapses_progress_spam() -> None:
    outputs = [_progress_dd() for _ in range(400)]
    outputs.append({"output_type": "stream", "name": "stdout", "text": "sweep done\n"})
    tail = _format_output_tail(outputs)
    # The 400-long run collapses: one placeholder + a counted collapse marker.
    assert tail.count("<IPython.core.display.HTML object>") == 1
    assert "×400 identical outputs collapsed" in tail
    # The real trailing output survives instead of being evicted by noise.
    assert "sweep done" in tail


def test_output_tail_preserves_short_runs() -> None:
    outputs = [
        {"output_type": "stream", "name": "stdout", "text": "one\n"},
        {"output_type": "stream", "name": "stdout", "text": "two\n"},
    ]
    tail = _format_output_tail(outputs)
    assert "one" in tail and "two" in tail
    assert "collapsed" not in tail


# --------------------------------------------------------------------- #
# Phase 1: deterministic server resolution
# --------------------------------------------------------------------- #

import urllib.error  # noqa: E402
from email.message import Message  # noqa: E402


class _FakeResp:
    """Minimal context-manager stand-in for urlopen's return value."""

    def __init__(self, status: int) -> None:
        self.status = status

    def __enter__(self) -> "_FakeResp":
        return self

    def __exit__(self, *exc) -> bool:
        return False


def test_server_alive_valid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    # /api/sessions returns 200 for a good token.
    monkeypatch.setattr(
        nb_collab.urllib.request, "urlopen", lambda *a, **k: _FakeResp(200)
    )
    assert _server_alive("http://localhost:8890", "goodtok") is True


def test_server_alive_wrong_token_403(monkeypatch: pytest.MonkeyPatch) -> None:
    # A stale jpserver-*.json with a wrong/expired token: /api/sessions 403s
    # (unlike the unauthenticated /api/status, which would falsely pass).
    def _raise_403(*a, **k):
        raise urllib.error.HTTPError(
            url="http://localhost:8890/api/sessions",
            code=403,
            msg="Forbidden",
            hdrs=Message(),
            fp=None,
        )

    monkeypatch.setattr(nb_collab.urllib.request, "urlopen", _raise_403)
    assert _server_alive("http://localhost:8890", "staletok") is False


def test_server_alive_dead_server(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise_conn(*a, **k):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr(nb_collab.urllib.request, "urlopen", _raise_conn)
    assert _server_alive("http://localhost:8890", "anytok") is False


def _write_jpserver(runtime: Path, name: str, url: str, token: str) -> Path:
    f = runtime / name
    f.write_text(json.dumps({"url": url, "token": token}), encoding="utf-8")
    return f


def test_runtime_mtimes_reads_faked_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    old = _write_jpserver(runtime, "jpserver-100.json", "http://a:8890/", "told")
    new = _write_jpserver(runtime, "jpserver-200.json", "http://b:8890/", "tnew")
    # Force a strict ordering rather than relying on write timing.
    import os

    os.utime(old, (1000, 1000))
    os.utime(new, (2000, 2000))
    # A malformed file is skipped, not fatal.
    (runtime / "jpserver-bad.json").write_text("{not json", encoding="utf-8")
    monkeypatch.setattr(nb_collab, "jupyter_runtime_dir", lambda: str(runtime))

    mtimes = _runtime_mtimes()
    # url is normalized (trailing slash stripped) to match _resolve_server keys.
    assert mtimes[("http://a:8890", "told")] == 1000
    assert mtimes[("http://b:8890", "tnew")] == 2000
    assert len(mtimes) == 2


def test_runtime_mtimes_missing_dir(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setattr(
        nb_collab, "jupyter_runtime_dir", lambda: str(tmp_path / "nope")
    )
    assert _runtime_mtimes() == {}


def _fake_resolution(
    monkeypatch: pytest.MonkeyPatch,
    servers: list[dict],
    alive: dict[tuple[str, str], bool],
    mtimes: dict[tuple[str, str], float] | None = None,
) -> None:
    monkeypatch.setattr(nb_collab, "_running_servers", lambda: servers)
    monkeypatch.setattr(
        nb_collab, "_server_alive", lambda url, tok: alive.get((url, tok), False)
    )
    monkeypatch.setattr(nb_collab, "_runtime_mtimes", lambda: mtimes or {})


def test_resolve_server_picks_live_over_stale(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    root = str(tmp_path)
    nb = tmp_path / "run" / "measure.ipynb"
    nb.parent.mkdir()
    nb.touch()
    # Stale file (wrong token) listed FIRST and NEWEST — must still lose to the
    # live server, because it fails the authenticated probe.
    servers = [
        {"url": "http://localhost:8890/", "token": "stale", "root_dir": root},
        {"url": "http://localhost:8890/", "token": "live", "root_dir": root},
    ]
    _fake_resolution(
        monkeypatch,
        servers,
        alive={("http://localhost:8890", "live"): True},
        mtimes={
            ("http://localhost:8890", "stale"): 9999,
            ("http://localhost:8890", "live"): 1,
        },
    )
    url, token, resolved_root = _resolve_server(nb)
    assert (url, token) == ("http://localhost:8890", "live")
    assert resolved_root == tmp_path.resolve()


def test_resolve_server_only_stale_exits_loud(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    root = str(tmp_path)
    nb = tmp_path / "measure.ipynb"
    nb.touch()
    servers = [{"url": "http://localhost:8890/", "token": "stale", "root_dir": root}]
    _fake_resolution(monkeypatch, servers, alive={})
    with pytest.raises(SystemExit) as exc:
        _resolve_server(nb)
    assert "authenticated liveness check" in str(exc.value)


def test_resolve_server_none_containing_exits(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    nb = tmp_path / "here" / "measure.ipynb"
    nb.parent.mkdir()
    nb.touch()
    # Server rooted at an unrelated dir — does not contain the notebook.
    servers = [
        {"url": "http://localhost:8890/", "token": "t", "root_dir": str(tmp_path / "other")}
    ]
    (tmp_path / "other").mkdir()
    _fake_resolution(monkeypatch, servers, alive={("http://localhost:8890", "t"): True})
    with pytest.raises(SystemExit) as exc:
        _resolve_server(nb)
    assert "under its root_dir" in str(exc.value)


def test_resolve_server_two_live_newest_mtime_wins(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    root = str(tmp_path)
    nb = tmp_path / "measure.ipynb"
    nb.touch()
    servers = [
        {"url": "http://localhost:8890/", "token": "older", "root_dir": root},
        {"url": "http://localhost:8891/", "token": "newer", "root_dir": root},
    ]
    _fake_resolution(
        monkeypatch,
        servers,
        alive={
            ("http://localhost:8890", "older"): True,
            ("http://localhost:8891", "newer"): True,
        },
        mtimes={
            ("http://localhost:8890", "older"): 100,
            ("http://localhost:8891", "newer"): 500,
        },
    )
    url, token, _ = _resolve_server(nb)
    assert (url, token) == ("http://localhost:8891", "newer")


@pytest.mark.parametrize("cmd", ["edit-cell", "execute-cell", "delete-cell", "wait"])
def test_cell_id_positional_strips_crlf_and_whitespace(cmd: str) -> None:
    # Windows Python print() emits CRLF; bash $(...) keeps the \r on every
    # line but the last, so loops hand over "<id>\r". The parser must strip it.
    extra = ["--source", "x = 1"] if cmd == "edit-cell" else []
    args = _build_parser().parse_args([cmd, "x.ipynb", "3cab5d4b6927489d8a9d29db6c249d2a\r", *extra])
    assert args.cell_id == "3cab5d4b6927489d8a9d29db6c249d2a"
    args = _build_parser().parse_args([cmd, "x.ipynb", "  abc123 \n", *extra])
    assert args.cell_id == "abc123"


@pytest.mark.parametrize("cmd", ["edit-cell", "execute-cell", "delete-cell", "wait"])
def test_cell_id_positional_rejects_blank(cmd: str) -> None:
    extra = ["--source", "x = 1"] if cmd == "edit-cell" else []
    with pytest.raises(SystemExit):
        _build_parser().parse_args([cmd, "x.ipynb", " \r\n", *extra])


# --------------------------------------------------------------------- #
# exec-all — argparse
# --------------------------------------------------------------------- #


def test_exec_all_parses_with_default_timeout() -> None:
    args = _build_parser().parse_args(["exec-all", "x.ipynb"])
    assert args.notebook.name == "x.ipynb"
    assert args.timeout == DEFAULT_EXEC_ALL_TIMEOUT


def test_exec_all_default_timeout_is_setup_sized() -> None:
    # exec-all runs setup-class cells (imports, instrument bring-up); a sweep
    # is appended and executed on its own, under execute-cell's larger cap.
    assert DEFAULT_EXEC_ALL_TIMEOUT == 120.0
    assert DEFAULT_EXEC_ALL_TIMEOUT < nb_collab.DEFAULT_EXEC_TIMEOUT


def test_exec_all_custom_timeout() -> None:
    args = _build_parser().parse_args(["exec-all", "x.ipynb", "--timeout", "30"])
    assert args.timeout == 30.0


def test_exec_all_rejects_cell_id_positional() -> None:
    # exec-all is whole-notebook; a stray cell id must not be swallowed.
    with pytest.raises(SystemExit):
        _build_parser().parse_args(["exec-all", "x.ipynb", "cid"])


# --------------------------------------------------------------------- #
# exec-all — run semantics (fake RTC client + fake kernel)
# --------------------------------------------------------------------- #


class _FakeExecAllKC:
    """Stand-in for BlockingKernelClient; records channel teardown."""

    stopped = 0

    def load_connection_file(self, *a) -> None: ...
    def start_channels(self) -> None: ...
    def wait_for_ready(self, timeout=None) -> None: ...

    def stop_channels(self) -> None:
        type(self).stopped += 1


class _FakeExecAllClient:
    """Async-context stand-in for NbModelClient covering the surface
    ``_exec_all`` touches: sync, policy metadata, cell reads, execute_cell,
    and the per-cell metadata accessors the executed_at stamp uses."""

    def __init__(self, cells: list[dict], policy: str = POLICY_APPEND_EXEC,
                 outcomes: dict[int, str] | None = None) -> None:
        self._cells = cells
        self._policy = policy
        self._outcomes = outcomes or {}
        self.executed: list[int] = []

    async def __aenter__(self) -> "_FakeExecAllClient":
        return self

    async def __aexit__(self, *exc) -> bool:  # noqa: ANN002
        return False

    async def wait_until_synced(self) -> None:
        return None

    def get_notebook_metadata(self, key, default=None):
        return {"policy": self._policy} if key == "hera" else default

    def __len__(self) -> int:
        return len(self._cells)

    def __getitem__(self, idx: int) -> dict:
        return self._cells[idx]

    def get_cell_metadata(self, index, key, default=None):
        return self._cells[index]["metadata"].get(key, default)

    def set_cell_metadata(self, index, key, value) -> None:
        self._cells[index]["metadata"][key] = value

    def execute_cell(self, idx, kc, timeout=None):
        self.executed.append(idx)
        outcome = self._outcomes.get(idx, "ok")
        if outcome == "timeout":
            raise TimeoutError("Timeout waiting for output")
        count = len(self.executed)
        self._cells[idx]["execution_count"] = count
        if outcome == "error":
            self._cells[idx]["outputs"] = [
                {"output_type": "error", "traceback": ["RuntimeError: boom"]}
            ]
            return {"status": "error", "execution_count": count}
        return {"status": "ok", "execution_count": count}


def _exec_all_cells() -> list[dict]:
    """md, code, blank code, code, raw, code — indices 1/3/5 are the run list."""

    def code(cell_id: str, source: str) -> dict:
        return {
            "id": cell_id, "cell_type": "code", "metadata": {},
            "source": source, "outputs": [], "execution_count": None,
        }

    return [
        {"id": "md0", "cell_type": "markdown", "metadata": {}, "source": "# setup"},
        code("c1", "import sweep"),
        code("blank2", "   \n"),
        code("c3", "mc = build()"),
        {"id": "raw4", "cell_type": "raw", "metadata": {}, "source": "raw"},
        code("c5", "print(mc)"),
    ]


def _patch_exec_all(monkeypatch, tmp_path, client) -> Path:
    """Stub server discovery, RTC client, and kernel so ``_exec_all`` runs dry."""
    nb_path = tmp_path / "m.ipynb"
    _write_nb(
        nb_path,
        minor=5,
        cells=[{"cell_type": "code", "id": "a" * 32, "metadata": {}, "source": "", "outputs": [], "execution_count": None}],
    )
    conn = tmp_path / "kernel-x.json"
    conn.write_text("{}")
    monkeypatch.setattr(nb_collab, "_resolve_with_overrides", lambda p, s, t: ("http://s", "tok", tmp_path))
    monkeypatch.setattr(nb_collab, "get_jupyter_notebook_websocket_url", lambda *a, **k: "ws://room")
    monkeypatch.setattr(nb_collab, "NbModelClient", lambda *a, **k: client)
    monkeypatch.setattr(nb_collab, "_find_or_create_kernel", lambda *a: "kid-1")
    monkeypatch.setattr(nb_collab, "_kernel_connection_file", lambda kid: conn)
    monkeypatch.setattr(nb_collab, "BlockingKernelClient", _FakeExecAllKC)
    return nb_path


def test_exec_all_runs_code_cells_in_order_skipping_md_and_blanks(monkeypatch, tmp_path, capsys) -> None:
    client = _FakeExecAllClient(_exec_all_cells())
    nb_path = _patch_exec_all(monkeypatch, tmp_path, client)
    _FakeExecAllKC.stopped = 0

    rc = asyncio.run(nb_collab._exec_all(nb_path, 120.0, "http://s", "tok"))

    assert rc == nb_collab.EXIT_OK
    assert client.executed == [1, 3, 5]
    out = capsys.readouterr().out
    assert "exec-all: 3 cells ran" in out
    assert "id=c1" in out and "id=c5" in out
    # One terse line per cell — the full status/tail block is for errors only.
    assert "status: done" not in out
    # One kernel for the whole run — opened once, torn down once.
    assert _FakeExecAllKC.stopped == 1


def test_exec_all_stamps_executed_at(monkeypatch, tmp_path) -> None:
    cells = _exec_all_cells()
    client = _FakeExecAllClient(cells)
    nb_path = _patch_exec_all(monkeypatch, tmp_path, client)

    asyncio.run(nb_collab._exec_all(nb_path, 120.0, "http://s", "tok"))

    assert "executed_at" in cells[1]["metadata"][HERA_TAG_KEY]


def test_exec_all_stops_at_first_error(monkeypatch, tmp_path, capsys) -> None:
    client = _FakeExecAllClient(_exec_all_cells(), outcomes={3: "error"})
    nb_path = _patch_exec_all(monkeypatch, tmp_path, client)
    _FakeExecAllKC.stopped = 0

    rc = asyncio.run(nb_collab._exec_all(nb_path, 120.0, "http://s", "tok"))

    assert rc == nb_collab.EXIT_ERROR
    # Cell 5 is never started — JupyterLab's Run All stops at the failure.
    assert client.executed == [1, 3]
    out = capsys.readouterr().out
    assert "status: error" in out
    assert "RuntimeError: boom" in out
    assert "error @ 3 id=c3" in out
    assert "exec-all: stopped at cell 2 of 3" in out
    assert _FakeExecAllKC.stopped == 1


def test_exec_all_timeout_returns_exit_timeout(monkeypatch, tmp_path, capsys) -> None:
    client = _FakeExecAllClient(_exec_all_cells(), outcomes={3: "timeout"})
    nb_path = _patch_exec_all(monkeypatch, tmp_path, client)

    rc = asyncio.run(nb_collab._exec_all(nb_path, 120.0, "http://s", "tok"))

    assert rc == nb_collab.EXIT_TIMEOUT
    assert client.executed == [1, 3]
    captured = capsys.readouterr()
    assert "status: TIMEOUT" in captured.out
    assert "STILL RUNNING" in captured.err


def test_exec_all_refuses_append_only_before_running(monkeypatch, tmp_path) -> None:
    """The E0 policy gate fires before any cell runs — same bucket as execute-cell."""
    client = _FakeExecAllClient(_exec_all_cells(), policy=POLICY_APPEND_ONLY)
    nb_path = _patch_exec_all(monkeypatch, tmp_path, client)

    with pytest.raises(SystemExit) as exc:
        asyncio.run(nb_collab._exec_all(nb_path, 120.0, "http://s", "tok"))

    assert "exec-all" in str(exc.value)
    assert client.executed == []


def test_exec_all_with_no_code_cells_is_a_clean_noop(monkeypatch, tmp_path, capsys) -> None:
    cells = [{"id": "md0", "cell_type": "markdown", "metadata": {}, "source": "# nothing to run"}]
    client = _FakeExecAllClient(cells)
    nb_path = _patch_exec_all(monkeypatch, tmp_path, client)

    rc = asyncio.run(nb_collab._exec_all(nb_path, 120.0, "http://s", "tok"))

    assert rc == nb_collab.EXIT_OK
    assert client.executed == []
    assert "exec-all: 0 cells ran" in capsys.readouterr().out
