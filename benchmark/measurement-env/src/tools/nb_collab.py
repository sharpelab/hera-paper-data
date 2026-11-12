"""nb-collab — drop cells into a JupyterLab-open notebook over the YDoc/RTC channel.

Subcommands:
  append        Append markdown and/or code cells to a live notebook.
  edit-cell     Replace an existing cell's source (policy-gated).
  execute-cell  Run an existing cell against the notebook's kernel (policy-gated).
  exec-all      Run every code cell in document order on one kernel (policy-gated).
  delete-cell   Remove an existing cell (policy-gated).
  wait          Block until a specific cell finishes executing (or times out).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

from jupyter_client import BlockingKernelClient
from jupyter_core.paths import jupyter_runtime_dir
from jupyter_nbmodel_client import NbModelClient, get_jupyter_notebook_websocket_url
from jupyter_server.serverapp import list_running_servers


HERA_TAG_KEY = "hera"
HERA_CELL_VERSION = "v0"

# Notebook-level policy keys live under nb.metadata.hera.policy.
# Cell-level metadata.hera is a dict carrying the version tag plus
# operation timestamps (appended_at / edited_at / executed_at) — see
# _stamp_cell_event. Older notebooks may still hold the legacy bare
# string "v0"; the stamper upgrades it in place.
POLICY_APPEND_ONLY = "append_only"
POLICY_APPEND_EXEC = "append_exec"
POLICY_EDIT_NO_EXEC = "edit_no_exec"
POLICY_EDIT_EXEC = "edit_exec"
ALL_POLICIES = (
    POLICY_APPEND_ONLY,
    POLICY_APPEND_EXEC,
    POLICY_EDIT_NO_EXEC,
    POLICY_EDIT_EXEC,
)
# Per-operation buckets. execute and delete are deliberately split: append_exec
# (the autonomous measure-notebook policy) grants execute but NOT edit or
# delete, so HERA can run a cell it appended while the append-only scientific
# record — no source rewrites, no removals — stays intact.
EDIT_POLICIES = (POLICY_EDIT_NO_EXEC, POLICY_EDIT_EXEC)
EXECUTE_POLICIES = (POLICY_APPEND_EXEC, POLICY_EDIT_EXEC)
DELETE_POLICIES = (POLICY_EDIT_EXEC,)

# Raised from 570s (the old sub-Bash-cap value): autonomous E1 sweeps run
# multi-hour and the wait is backgrounded, where a 570s clean timeout looked
# like completion (QC0426 2026-06-16: bit twice on a ~70 min snake and a
# multi-hour F(n) fan). 30 min covers the start-gate and most medium sweeps
# without re-arming; --follow lifts the deadline entirely for multi-hour runs.
# A foreground (non-backgrounded) wait can still outlive the harness's ~600s
# shell cap — background long waits (run_in_background) or pass a smaller
# --timeout for a foreground start-gate.
DEFAULT_WAIT_TIMEOUT = 1800.0
DEFAULT_WAIT_POLL = 1.0
DEFAULT_EXEC_TIMEOUT = 570.0
# exec-all runs setup-class cells (imports, instrument bring-up), never a
# sweep, so its per-cell deadline is far tighter than execute-cell's.
DEFAULT_EXEC_ALL_TIMEOUT = 120.0
DEFAULT_INTERRUPT_CONFIRM_TIMEOUT = 30.0
DEFAULT_KERNEL_READY_TIMEOUT = 15.0
OUTPUT_TAIL_MAX_CHARS = 2000

# Line that separates stdin chunks when multiple `-` flags are used.
# Rare enough not to collide with typical notebook content.
STDIN_DELIM = "---|"

# Raised from upstream's 16 MB default. Two distinct pressures:
#  (1) full-doc YDoc sync on the initial SYNC_STEP1/SYNC_STEP2 handshake
#      = ~size of the .ipynb on disk (22 MB on b1c2 ana);
#  (2) accumulated CRDT history in the live YDoc room can be several×
#      the on-disk size (observed 89 MB after a session of edits + a
#      tab hard-reload + a second-browser open) and only resets when
#      the JupyterLab server restarts.
# nb-collab is one-shot, so every invocation pays the cost. Keep loose.
# Bumped 5/20: b1c2 measure room hit 290 MB after a long session (1009 close
# from a 303 MB sync frame vs 256 MB cap). Operator declined a JL restart so
# the room won't compact today; 1 GB ceiling buys headroom for the rest of
# the session without thrash. Revisit once the room is restarted clean.
WS_MAX_BODY_SIZE = 1024 * 1024 * 1024

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_TIMEOUT = 2
EXIT_DELETED = 3
EXIT_NOT_RUNNING = 4


def _utc_now_iso() -> str:
    """Current UTC time as an ISO-8601 string with an explicit offset.

    Sessions span operators in PT and EDT; a bare local timestamp would be
    ambiguous, so cell stamps are always UTC with a trailing ``+00:00``.
    Joins to sweep ``start_time``/``end_time`` (Unix epoch, also UTC) are
    then mechanical via ``datetime.fromisoformat(...).timestamp()``.
    """
    return datetime.now(timezone.utc).isoformat()


def _stamp_cell_event(client: "NbModelClient", idx: int, field: str, when: str) -> None:
    """Record ``metadata.hera.<field> = when`` on cell ``idx``, merging.

    Reads the existing ``metadata.hera`` and preserves any prior keys (so a
    later edit/execute stamp doesn't clobber ``appended_at``). A legacy bare
    ``"v0"`` string (or any non-dict) is replaced by a fresh dict. The
    version tag lives under ``v`` so presence-based filtering of HERA cells
    still works.
    """
    existing = client.get_cell_metadata(idx, HERA_TAG_KEY, None)
    meta = dict(existing) if isinstance(existing, dict) else {}
    meta["v"] = HERA_CELL_VERSION
    meta[field] = when
    client.set_cell_metadata(idx, HERA_TAG_KEY, meta)


# append --summary/--eta: matches an optional <N>h then optional <N>m, h
# before m, at least one required. Bare numbers and fractional values don't
# match (no unit) and are refused with a dedicated message in _parse_eta_minutes.
_ETA_RE = re.compile(r"^(?:(\d+)h)?(?:(\d+)m)?$")


def _parse_eta_minutes(text: str) -> int:
    """Parse an ETA duration (``40m``, ``2h``, ``1h30m``) into whole minutes.

    Accepts an optional ``<N>h`` followed by an optional ``<N>m`` — h before
    m, at least one component, positive total. Raises ``ValueError`` with a
    message telling the caller how to fix it; a bare number gets a pointed
    "add the suffix" nudge since that's the most likely mistake.
    """
    text = text.strip()
    if text.isdigit():
        raise ValueError(
            f"--eta {text!r} has no unit — add a suffix, e.g. '{text}m' or "
            f"'{text}h' (accepted forms: 40m, 2h, 1h30m)."
        )
    m = _ETA_RE.match(text)
    if not m or (m.group(1) is None and m.group(2) is None):
        raise ValueError(
            f"--eta {text!r} is not a valid duration; accepted forms: 40m, 2h, "
            f"1h30m (optional <N>h then optional <N>m, h before m)."
        )
    hours = int(m.group(1)) if m.group(1) else 0
    minutes = int(m.group(2)) if m.group(2) else 0
    total = hours * 60 + minutes
    if total <= 0:
        raise ValueError(f"--eta {text!r} must be a positive duration.")
    return total


def _render_duration_display(minutes: int) -> str:
    """Render a minute count as ``≈40 min`` (<60) or ``≈1h30m``/``≈2h`` (>=60)."""
    if minutes < 60:
        return f"≈{minutes} min"
    hours, rem = divmod(minutes, 60)
    return f"≈{hours}h" if rem == 0 else f"≈{hours}h{rem}m"


def _render_eta_clock(appended_at_utc_iso: str, eta_minutes: int) -> str:
    """Render ``~15:12 (≈40 min)`` — the local ETA clock + duration parenthetical.

    Used for the stdout echo (the in-cell line bolds its pieces separately in
    ``_render_summary_line``). ``appended_at_utc_iso`` is converted to
    server-local time via ``.astimezone()`` (same instant as the
    ``appended_at`` stamp); if the ETA's local calendar date is after the
    append's, `` (+Nd)`` is inserted right after the clock.
    """
    appended_local = datetime.fromisoformat(appended_at_utc_iso).astimezone()
    eta_local = appended_local + timedelta(minutes=eta_minutes)
    day_delta = (eta_local.date() - appended_local.date()).days
    day_marker = f" (+{day_delta}d)" if day_delta > 0 else ""
    return f"~{eta_local.strftime('%H:%M')}{day_marker} ({_render_duration_display(eta_minutes)})"


# Markdown formatting characters escaped in the rendered summary text: the
# line is a blockquote (prose context), so a bare `_`/`*` in a spec like
# ``n_e`` would italicize. Backslash first so it can't swallow added escapes.
_MD_ESCAPE_RE = re.compile(r"([\\*_])")


def _escape_md(text: str) -> str:
    """Backslash-escape ``\\``, ``*``, ``_`` for prose-context markdown."""
    return _MD_ESCAPE_RE.sub(r"\\\1", text)


def _render_summary_line(
    appended_at_utc_iso: str, summary: str | None, eta_minutes: int | None
) -> str:
    """Render the blockquote line inserted into the first appended markdown cell.

    ``> **14:32** · <summary> · **ETA ~15:12** (≈40 min)`` (both), dropping
    the absent clause: ``> **14:32** · <summary>`` or ``> **14:32** ·
    **ETA ~15:12** (≈40 min)``. The clock is the append instant
    (``appended_at_utc_iso``) converted to server-local time via
    ``.astimezone()``; a day rollover adds `` (+1d)`` inside the bold, right
    after the ETA clock. Summary text is markdown-escaped (``_escape_md``).
    """
    appended_local = datetime.fromisoformat(appended_at_utc_iso).astimezone()
    parts = [f"**{appended_local.strftime('%H:%M')}**"]
    if summary is not None:
        parts.append(_escape_md(summary))
    if eta_minutes is not None:
        eta_local = appended_local + timedelta(minutes=eta_minutes)
        day_delta = (eta_local.date() - appended_local.date()).days
        day_marker = f" (+{day_delta}d)" if day_delta > 0 else ""
        parts.append(
            f"**ETA ~{eta_local.strftime('%H:%M')}{day_marker}** "
            f"({_render_duration_display(eta_minutes)})"
        )
    return "> " + " · ".join(parts)


def _insert_after_heading(markdown_src: str, line: str) -> str:
    """Insert ``line`` into ``markdown_src`` right after its leading heading.

    Skips leading blank lines to find the first non-blank line; if it starts
    with ``#``, ``line`` lands after it as heading / blank / line / blank /
    rest (an existing blank right after the heading is absorbed rather than
    doubled). With no leading heading, ``line`` is prepended: line / blank /
    original content, untouched.
    """
    lines = markdown_src.split("\n")
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("#"):
        rest = lines[i + 1 :]
        if rest and rest[0].strip() == "":
            rest = rest[1:]
        result = lines[: i + 1] + ["", line, ""] + rest
    else:
        result = [line, ""] + lines
    return "\n".join(result)


def _rel_path(notebook_path: Path, root: Path) -> str:
    """Notebook path relative to the server root, with forward-slash separators.

    Jupyter's session API stores ``notebook.path`` with forward slashes on every
    platform; ``Path.relative_to`` yields native separators, so ``str(...)`` gives
    backslashes on Windows (``zack\\run\\nb.ipynb``). That misses the exact-string
    match in ``_find_kernel_for_path`` and forks a fresh, empty kernel instead of
    binding the operator's live one (observed live on dgg-vti: a nested measure
    notebook spawned a stray kernel because only the backslash form was compared).
    ``as_posix()`` yields the forward-slash form Jupyter uses — correct for the
    session match, the create POST body/name, and the websocket URL alike. Linux
    is unaffected (``as_posix()`` already equals ``str()`` there). (CLAUDE.md
    Platform: use ``as_posix()`` for URLs, never hardcode separators.)
    """
    return notebook_path.resolve().relative_to(root).as_posix()


def _running_servers() -> list[dict]:
    return list(list_running_servers())


def _server_alive(url: str, token: str) -> bool:
    """Authenticated liveness probe against /api/sessions.

    /api/status is served *unauthenticated*, so a stale jpserver-*.json that
    lists the right port but a dead/restarted server with a wrong token still
    passes it — and gets selected, poisoning every later call with a bad token.
    /api/sessions is ``@web.authenticated``: it returns 200 only for a valid
    token, 403 for a wrong/expired one, and a connection error for a dead
    server — so a stale runtime file is correctly disqualified. HTTPError (the
    403) is a URLError subclass, so the existing except clause catches it.

    Plain HTTP GET: cross-platform (Windows / Git Bash) and adds no standing WS
    connection, honoring the room-bloat constraint.
    """
    try:
        with urllib.request.urlopen(
            f"{url}/api/sessions?token={token}", timeout=3
        ) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def _runtime_mtimes() -> dict[tuple[str, str], float]:
    """Map ``(url, token)`` -> jpserver-*.json mtime, for freshness ordering.

    ``list_running_servers`` drops the originating filename, so re-scan the
    runtime dir to recover mtimes. Best-effort: unreadable or malformed files
    are skipped and default to mtime 0.0 at the call site.
    """
    out: dict[tuple[str, str], float] = {}
    runtime = Path(jupyter_runtime_dir())
    if not runtime.is_dir():
        return out
    for f in runtime.glob("jpserver-*.json"):
        try:
            info = json.loads(f.read_text(encoding="utf-8"))
            mtime = f.stat().st_mtime
        except (OSError, json.JSONDecodeError):
            continue
        url = str(info.get("url", "")).rstrip("/")
        out[(url, info.get("token", ""))] = mtime
    return out


def _warn_if_legacy_format(path: Path) -> None:
    """Emit a stderr warning if ``path`` is nbformat <4.5 or has cell(s) without IDs.

    Cell-ID-less notebooks trigger JupyterLab's "recreate all cells on
    out-of-band edit" path (``jupyter_ydoc/ynotebook.py``'s ID-keyed diff
    falls through to delete-and-reinsert), which bloats the YDoc room
    by the full notebook size per autosave/file-touch. Fix by upgrading
    the file to nbformat 4.5 with a ``uuid4().hex`` ``id`` on each cell.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            nb = json.load(f)
    except (OSError, json.JSONDecodeError):
        return  # let downstream open-and-fail report a precise error
    minor = nb.get("nbformat_minor", 0)
    cells = nb.get("cells", [])
    missing_ids = sum(1 for c in cells if "id" not in c)
    if minor >= 5 and missing_ids == 0:
        return
    print(
        f"warning: {path} is legacy nbformat 4.{minor} "
        f"({missing_ids}/{len(cells)} cells missing IDs). "
        f"Out-of-band edits will bloat the YDoc room; "
        f"upgrade to nbformat 4.5 with uuid cell IDs.",
        file=sys.stderr,
    )


def _resolve_server(notebook_path: Path) -> tuple[str, str, Path]:
    """Find the running Jupyter server whose root_dir contains notebook_path.

    Returns (server_url, token, root_dir).
    """
    nb_abs = notebook_path.resolve()
    mtimes = _runtime_mtimes()

    # Collect every server whose root_dir contains the notebook, deduped by
    # (url, token). Dedup on the pair rather than url alone: a stale same-url
    # file must not be able to discard the live server's distinct token — the
    # authenticated probe below picks the valid one.
    candidates: list[tuple[str, str, Path]] = []
    seen: set[tuple[str, str]] = set()
    for info in _running_servers():
        root = Path(info["root_dir"]).resolve()
        try:
            nb_abs.relative_to(root)
        except ValueError:
            continue
        url = info["url"].rstrip("/")
        key = (url, info["token"])
        if key in seen:
            continue
        seen.add(key)
        candidates.append((url, info["token"], root))

    # Newest jpserver file first: the live server's runtime file is the
    # freshest; stale duplicates sort older and, failing the authenticated
    # probe, are never selected. Ordering makes selection deterministic even
    # when two servers pass the probe.
    candidates.sort(key=lambda c: mtimes.get((c[0], c[1]), 0.0), reverse=True)

    tried: list[str] = []
    for url, token, root in candidates:
        if _server_alive(url, token):
            return url, token, root
        tried.append(url)

    if tried:
        sys.exit(
            f"error: found runtime file(s) listing a server for {nb_abs}, but "
            f"none passed an authenticated liveness check (stale token or dead "
            f"server): {', '.join(tried)}.\n"
            f"hint: the jpserver-*.json files are stale — restart JupyterLab "
            f"from the launcher (uv run measurement-env), or run "
            f"`jupyter server list` and delete the dead entries."
        )
    sys.exit(
        f"error: no running JupyterLab server has {nb_abs} under its root_dir.\n"
        f"hint: start the launcher (uv run measurement-env) or run `jupyter server list`."
    )


def _resolve_with_overrides(
    notebook_path: Path, server_url: str | None, token: str | None
) -> tuple[str, str, Path]:
    if server_url:
        url = server_url.rstrip("/")
        if token is None:
            # Look up the token from the runtime files by URL match —
            # never silently fall through to auto-discovery.
            for info in _running_servers():
                if info["url"].rstrip("/") == url:
                    return url, info["token"], Path(info["root_dir"]).resolve()
            sys.exit(
                f"error: --server-url {url} matches no running server and no "
                f"--token was given.\n"
                f"hint: pass --token (use --token '' for token-less servers)."
            )
        for info in _running_servers():
            if info["url"].rstrip("/") == url and info["token"] == token:
                return url, token, Path(info["root_dir"]).resolve()
        sys.exit("error: --server-url/--token did not match any running server.")
    return _resolve_server(notebook_path)


async def _append(
    notebook_path: Path,
    cells: list[tuple[str, str]],
    server_url: str | None,
    token: str | None,
    settle: float,
    execute: bool,
    wait: bool,
    follow: bool,
    timeout: float,
    poll: float,
    summary: str | None = None,
    eta_minutes: int | None = None,
) -> int:
    if not notebook_path.exists():
        sys.exit(f"error: notebook does not exist: {notebook_path}")
    if not notebook_path.is_file() or notebook_path.suffix != ".ipynb":
        sys.exit(f"error: not an .ipynb file: {notebook_path}")
    _warn_if_legacy_format(notebook_path)

    server_url, token, root = _resolve_with_overrides(notebook_path, server_url, token)
    rel_path = _rel_path(notebook_path, root)

    try:
        ws_url = get_jupyter_notebook_websocket_url(server_url, rel_path, token)
    except Exception as e:
        sys.exit(f"error: failed to resolve collaboration room ({type(e).__name__}: {e})")

    wait_cell_id: str | None = None
    try:
        async with NbModelClient(ws_url, path=rel_path, ws_max_body_size=WS_MAX_BODY_SIZE) as client:
            await client.wait_until_synced()
            # Gate before any cell lands: a forbidden policy fails loud and
            # leaves the notebook untouched. --wait is deliberately NOT gated:
            # appending is never gated and the wait is read-only, so it is the
            # one auto-resume path available on an append_only (E0) measure nb.
            if execute:
                _require_policy(client, EXECUTE_POLICIES, "append --execute")
            print(f"connected: {server_url} path={rel_path} cells={len(client)}")

            appended_at = _utc_now_iso()

            # --summary/--eta render into the FIRST appended markdown cell's
            # source before it lands — no post-insert edit. Validation (a
            # markdown cell exists, no backtick, --eta parses) already ran in
            # _cmd_append before any websocket connect.
            first_md_pos: int | None = None
            if summary is not None or eta_minutes is not None:
                for i, (kind, _src) in enumerate(cells):
                    if kind == "markdown":
                        first_md_pos = i
                        break
                if first_md_pos is not None:
                    line = _render_summary_line(appended_at, summary, eta_minutes)
                    kind, src = cells[first_md_pos]
                    cells = list(cells)
                    cells[first_md_pos] = (kind, _insert_after_heading(src, line))

            inserted: list[tuple[str, int, str]] = []
            for kind, src in cells:
                if kind == "markdown":
                    idx = client.add_markdown_cell(src)
                else:
                    idx = client.add_code_cell(src)
                _stamp_cell_event(client, idx, "appended_at", appended_at)
                cell_id = client[idx].get("id", "")
                inserted.append((kind, idx, cell_id))

            if first_md_pos is not None:
                idx = inserted[first_md_pos][1]
                if summary is not None:
                    _stamp_cell_event(client, idx, "summary", summary)
                if eta_minutes is not None:
                    eta_at = (
                        datetime.fromisoformat(appended_at) + timedelta(minutes=eta_minutes)
                    ).isoformat()
                    _stamp_cell_event(client, idx, "eta_at", eta_at)

            for kind, idx, cell_id in inserted:
                print(f"  appended {kind} @ {idx} id={cell_id}")
            if eta_minutes is not None:
                print(f"  eta: {_render_eta_clock(appended_at, eta_minutes)}")
            await asyncio.sleep(settle)
            print(f"done. cells now = {len(client)}")

            if execute:
                # Run the last appended code cell by the id this append just
                # created — never nb['cells'][-1] off the (stale) on-disk file.
                code_cells = [(i, cid) for k, i, cid in inserted if k == "code"]
                if not code_cells:
                    sys.exit("error: --execute requires an appended code cell (--code/--code-file)")
                idx, cell_id = code_cells[-1]
                return _run_cell_on_open_client(
                    client, idx, cell_id, server_url, token, rel_path, timeout
                )

            if wait:
                # Wait on the last appended *code* cell (markdown cells have no
                # execution_count to flip). Captured here, then waited on after
                # this append client closes — same pattern the operator's two
                # commands used by hand.
                code_cells = [(i, cid) for k, i, cid in inserted if k == "code"]
                if not code_cells:
                    sys.exit("error: --wait requires an appended code cell (--code/--code-file)")
                wait_cell_id = code_cells[-1][1]
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"error: append failed ({type(e).__name__}: {e})")

    # --wait reconnects (after the append client closes) and blocks on the
    # operator running the just-appended cell, reusing the standalone `wait`
    # mechanics: --follow lifts the deadline for a backgrounded wait, and the
    # TIMEOUT contract stays loud/distinct. The cell starts with execution_count
    # None, so default _wait semantics block until the operator's first run.
    if wait_cell_id is not None:
        print(f"waiting for operator to run id={wait_cell_id} (follow={follow})")
        wait_timeout = None if follow else timeout
        return await _wait(
            notebook_path, wait_cell_id, wait_timeout, poll,
            False, server_url, token,
        )
    return 0


def _split_stdin(raw: str, delim: str) -> list[str]:
    """Split stdin text on lines exactly equal to ``delim``.

    Each chunk excludes the delimiter line and has no trailing newline
    (matching ``splitlines()`` semantics).  A single chunk with no
    delimiter is returned as a one-element list.
    """
    chunks: list[str] = []
    current: list[str] = []
    for line in raw.splitlines():
        if line == delim:
            chunks.append("\n".join(current))
            current = []
        else:
            current.append(line)
    chunks.append("\n".join(current))
    return chunks


def _reject_inline_substitution(flag: str, file_flag: str, value: str) -> None:
    """Refuse an inline cell-content value that bash command-substitutes.

    A raw backtick or ``$(`` in an inline ``--markdown``/``--code``/``--source``
    value means bash ran (or silently dropped) the fragment before nb-collab
    saw it — the 2026-06-14 QC0426 and 2026-06-24 zf1 sessions both lost a path
    fragment this way. Refuse loud and point at the substitution-free flags.
    """
    bad = "`" if "`" in value else "$(" if "$(" in value else None
    if bad is not None:
        sys.exit(
            f"error: {flag} value contains a raw '{bad}' — bash command-"
            f"substitutes it before nb-collab runs, silently dropping/expanding "
            f"the fragment. Pass the source via {file_flag} (verbatim UTF-8 file) "
            f"or '{flag} -' (stdin) instead."
        )


def _resolve_cells(parsed_cells: list[tuple[str, Any]]) -> list[tuple[str, str]]:
    """Resolve stdin / file source placeholders to concrete (kind, source) tuples.

    Walks ``parsed_cells`` left-to-right.  File reads happen up-front so
    a missing or non-UTF-8 file aborts before any websocket connect.
    Stdin is consumed once and split on ``STDIN_DELIM``; chunks are
    assigned to ``*_stdin`` placeholders in declared order.
    """
    stdin_indices = [i for i, (k, _) in enumerate(parsed_cells) if k.endswith("_stdin")]
    file_indices = [i for i, (k, _) in enumerate(parsed_cells) if k.endswith("_file")]

    file_contents: dict[int, str] = {}
    for i in file_indices:
        path_str = parsed_cells[i][1]
        path = Path(path_str)
        try:
            file_contents[i] = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            sys.exit(f"error: file not found: {path_str}")
        except PermissionError as e:
            sys.exit(f"error: permission denied reading {path_str}: {e}")
        except UnicodeDecodeError as e:
            sys.exit(f"error: file is not valid UTF-8: {path_str}: {e}")
        except OSError as e:
            sys.exit(f"error: failed to read {path_str} ({type(e).__name__}: {e})")

    stdin_chunks: list[str] = []
    if stdin_indices:
        if sys.stdin.isatty():
            sys.exit(
                f"error: stdin is a tty but {len(stdin_indices)} '-' flag(s) were given; "
                f"pipe a heredoc, file, or command output in."
            )
        raw = sys.stdin.read()
        stdin_chunks = _split_stdin(raw, STDIN_DELIM)
        if len(stdin_chunks) != len(stdin_indices):
            sys.exit(
                f"error: stdin chunk count ({len(stdin_chunks)}) does not match "
                f"'-' flag count ({len(stdin_indices)}); chunks are separated by a "
                f"line containing exactly '{STDIN_DELIM}'."
            )

    chunk_iter = iter(stdin_chunks)
    resolved: list[tuple[str, str]] = []
    for i, (kind, value) in enumerate(parsed_cells):
        if kind == "markdown":
            _reject_inline_substitution("--markdown", "--markdown-file", value)
            resolved.append(("markdown", value))
        elif kind == "code":
            _reject_inline_substitution("--code", "--code-file", value)
            resolved.append(("code", value))
        elif kind == "markdown_stdin":
            resolved.append(("markdown", next(chunk_iter)))
        elif kind == "code_stdin":
            resolved.append(("code", next(chunk_iter)))
        elif kind == "markdown_file":
            resolved.append(("markdown", file_contents[i]))
        elif kind == "code_file":
            resolved.append(("code", file_contents[i]))
        else:
            raise AssertionError(f"unknown cell kind: {kind}")
    return resolved


def _cmd_append(args: argparse.Namespace) -> int:
    if not args.cells:
        sys.exit("error: pass at least one --markdown, --code, --markdown-file, or --code-file")
    if args.follow and not args.wait:
        sys.exit("error: --follow applies only with --wait")
    cells = _resolve_cells(args.cells)

    # --summary/--eta validation runs here, before any websocket connect: a
    # missing markdown cell, a backtick in --summary, or a bad --eta duration
    # all fail loud with the notebook untouched.
    eta_minutes: int | None = None
    if args.summary is not None or args.eta is not None:
        if not any(kind == "markdown" for kind, _ in cells):
            sys.exit(
                "error: --summary/--eta require a markdown cell "
                "(--markdown/--markdown-file)"
            )
        if args.summary is not None and "`" in args.summary:
            sys.exit(
                "error: --summary must not contain a backtick "
                "(it would break the rendered markdown line)"
            )
        if args.eta is not None:
            try:
                eta_minutes = _parse_eta_minutes(args.eta)
            except ValueError as e:
                sys.exit(f"error: {e}")

    return asyncio.run(
        _append(
            args.notebook,
            cells,
            args.server_url,
            args.token,
            args.settle,
            args.execute,
            args.wait,
            args.follow,
            args.timeout,
            args.poll,
            args.summary,
            eta_minutes,
        )
    )


def _resolve_single_source(
    inline: str | None, source_file: str | None
) -> str:
    """Resolve a single ``--source`` / ``--source-file`` flag to text.

    ``inline == "-"`` means read all of stdin (one cell, no chunk
    delimiter). File errors abort before any websocket connect.
    """
    if inline is not None and source_file is not None:
        sys.exit("error: pass exactly one of --source / --source-file")
    if inline is None and source_file is None:
        sys.exit("error: pass exactly one of --source / --source-file")

    if source_file is not None:
        path = Path(source_file)
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            sys.exit(f"error: file not found: {source_file}")
        except PermissionError as e:
            sys.exit(f"error: permission denied reading {source_file}: {e}")
        except UnicodeDecodeError as e:
            sys.exit(f"error: file is not valid UTF-8: {source_file}: {e}")
        except OSError as e:
            sys.exit(f"error: failed to read {source_file} ({type(e).__name__}: {e})")

    assert inline is not None  # narrowed
    if inline == "-":
        if sys.stdin.isatty():
            sys.exit(
                "error: stdin is a tty but --source - was given; "
                "pipe a heredoc, file, or command output in."
            )
        return sys.stdin.read()
    _reject_inline_substitution("--source", "--source-file", inline)
    return inline


def _read_policy(client: NbModelClient) -> str:
    """Read ``nb.metadata.hera.policy`` with a safe ``append_only`` default."""
    hera_meta = client.get_notebook_metadata(HERA_TAG_KEY, None)
    if isinstance(hera_meta, dict):
        policy = hera_meta.get("policy")
        if isinstance(policy, str) and policy in ALL_POLICIES:
            return policy
    return POLICY_APPEND_ONLY


def _require_policy(client: NbModelClient, allowed: tuple[str, ...], op: str) -> str:
    policy = _read_policy(client)
    if policy not in allowed:
        sys.exit(
            f"error: notebook policy is '{policy}'; "
            f"{op} requires one of {list(allowed)}. "
            f"Set nb.metadata.hera.policy to enable."
        )
    return policy


def _clear_cell_output(client: NbModelClient, idx: int) -> None:
    """Clear ``outputs`` and reset ``execution_count`` for cell ``idx``.

    Mirrors the reset block inside ``NbModelClient.execute_cell`` — reaches
    into the YDoc layer because the public API doesn't expose these
    fields directly.
    """
    ycell = client._doc.ycells[idx]  # noqa: SLF001 — matches lib's own pattern
    with ycell.doc.transaction():
        if "outputs" in ycell:
            del ycell["outputs"][:]
        ycell["execution_count"] = None


async def _edit_cell(
    notebook_path: Path,
    cell_id: str,
    source: str,
    keep_outputs: bool,
    server_url: str | None,
    token: str | None,
    settle: float,
) -> int:
    if not notebook_path.exists():
        sys.exit(f"error: notebook does not exist: {notebook_path}")
    if not notebook_path.is_file() or notebook_path.suffix != ".ipynb":
        sys.exit(f"error: not an .ipynb file: {notebook_path}")
    _warn_if_legacy_format(notebook_path)

    server_url, token, root = _resolve_with_overrides(notebook_path, server_url, token)
    rel_path = _rel_path(notebook_path, root)

    try:
        ws_url = get_jupyter_notebook_websocket_url(server_url, rel_path, token)
    except Exception as e:
        sys.exit(f"error: failed to resolve collaboration room ({type(e).__name__}: {e})")

    try:
        async with NbModelClient(ws_url, path=rel_path, ws_max_body_size=WS_MAX_BODY_SIZE) as client:
            await client.wait_until_synced()
            _require_policy(client, EDIT_POLICIES, "edit-cell")

            cell, idx = _find_cell_by_id(client, cell_id)
            if cell is None:
                sys.exit(f"error: cell id not found: {cell_id}")

            kind = cell.get("cell_type", "?")
            print(f"connected: {server_url} path={rel_path} cells={len(client)}")
            print(f"  editing {kind} @ {idx} id={cell_id}")

            client.set_cell_source(idx, source)
            _stamp_cell_event(client, idx, "edited_at", _utc_now_iso())
            if not keep_outputs and kind == "code":
                _clear_cell_output(client, idx)
                print("  cleared outputs + execution_count")
            elif keep_outputs and kind == "code":
                print("  preserved outputs + execution_count")

            await asyncio.sleep(settle)
            print("done.")
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"error: edit-cell failed ({type(e).__name__}: {e})")
    return EXIT_OK


def _cmd_edit_cell(args: argparse.Namespace) -> int:
    source = _resolve_single_source(args.source, args.source_file)
    return asyncio.run(
        _edit_cell(
            args.notebook,
            args.cell_id,
            source,
            args.keep_outputs,
            args.server_url,
            args.token,
            args.settle,
        )
    )


def _find_kernel_for_path(server_url: str, token: str, rel_path: str) -> str | None:
    """Return the kernel id of the running session for ``rel_path``, or None.

    Find-only: never creates a session. ``interrupt`` uses this so it refuses
    cleanly when nothing is running rather than spinning up a kernel just to
    interrupt it.
    """
    try:
        with urllib.request.urlopen(
            f"{server_url}/api/sessions?token={token}", timeout=10
        ) as resp:
            sessions = json.loads(resp.read())
    except urllib.error.URLError as e:
        sys.exit(f"error: failed to list sessions ({type(e).__name__}: {e})")

    for s in sessions:
        nb = s.get("notebook") or {}
        if nb.get("path") == rel_path:
            kernel = s.get("kernel") or {}
            kid = kernel.get("id")
            if kid:
                return kid
    return None


def _find_or_create_kernel(server_url: str, token: str, rel_path: str) -> str:
    """Return the kernel id for ``rel_path``.

    Looks for an existing session whose ``notebook.path`` matches; if none
    is found, POSTs a new session to start a python3 kernel.
    """
    kid = _find_kernel_for_path(server_url, token, rel_path)
    if kid is not None:
        return kid

    # No session — create one.
    body = json.dumps(
        {
            "path": rel_path,
            "type": "notebook",
            "name": rel_path,
            "kernel": {"name": "python3"},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{server_url}/api/sessions?token={token}",
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            sess = json.loads(resp.read())
    except urllib.error.URLError as e:
        sys.exit(f"error: failed to create session for {rel_path} ({type(e).__name__}: {e})")
    return sess["kernel"]["id"]


def _kernel_connection_file(kernel_id: str) -> Path:
    return Path(jupyter_runtime_dir()) / f"kernel-{kernel_id}.json"


def _kernel_execution_state(server_url: str, token: str, kernel_id: str) -> str | None:
    """Return the kernel's execution_state (``busy``/``idle``/``starting``), or None."""
    try:
        with urllib.request.urlopen(
            f"{server_url}/api/kernels/{kernel_id}?token={token}", timeout=10
        ) as resp:
            info = json.loads(resp.read())
    except urllib.error.URLError:
        return None
    state = info.get("execution_state")
    return state if isinstance(state, str) else None


def _interrupt_kernel(server_url: str, token: str, kernel_id: str) -> None:
    """POST /api/kernels/<id>/interrupt — the REST equivalent of JupyterLab's
    Interrupt Kernel button (delivers a SIGINT-equivalent to the kernel)."""
    req = urllib.request.Request(
        f"{server_url}/api/kernels/{kernel_id}/interrupt?token={token}",
        data=b"",
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=10).close()
    except urllib.error.URLError as e:
        sys.exit(f"error: interrupt request failed ({type(e).__name__}: {e})")


def _cell_is_running(cell: dict[str, Any], kernel_state: str | None) -> bool:
    """Whether ``cell`` is the one the kernel is actively executing.

    The guard for ``interrupt --cell-id``: only a *currently running* cell is a
    valid interrupt target. Detection uses two signals that propagate reliably
    across YDoc clients (a fresh interrupt process is a different client than the
    one driving the cell):

    - the kernel's REST ``execution_state`` is ``busy`` (something is running),
    - the cell's ``execution_count`` is None (it has not completed — the same
      field ``nb-collab wait`` polls cross-client).

    The cell-level ``execution_state`` field is NOT used: it is set on the
    executing client's local doc and does not reliably reach other clients
    (verified on the Windows rig VM — a running cell read back as ``idle``).
    """
    return kernel_state == "busy" and cell.get("execution_count") is None


def _open_kernel_client(
    server_url: str, token: str, rel_path: str
) -> tuple[str, BlockingKernelClient]:
    """Resolve (creating if needed) the notebook's kernel and open a ready client.

    The caller owns the returned client and must ``stop_channels()`` it.
    """
    kernel_id = _find_or_create_kernel(server_url, token, rel_path)
    conn = _kernel_connection_file(kernel_id)
    if not conn.exists():
        sys.exit(
            f"error: kernel connection file not found at {conn}; "
            f"check JUPYTER_RUNTIME_DIR alignment between nb-collab and JupyterLab."
        )
    kc = BlockingKernelClient()
    kc.load_connection_file(str(conn))
    kc.start_channels()
    try:
        kc.wait_for_ready(timeout=DEFAULT_KERNEL_READY_TIMEOUT)
    except BaseException:
        kc.stop_channels()
        raise
    return kernel_id, kc


def _exec_on_kernel(
    client: NbModelClient, idx: int, kc: BlockingKernelClient, timeout: float
) -> dict[str, Any] | None:
    """Run cell ``idx`` on ``kc``; None means the client gave up waiting.

    On a clean return, stamps when nb-collab fired the run. recordTiming (if
    enabled on the server) independently stamps precise kernel start/end under
    cell.metadata.execution; this is the agent-side marker.
    """
    try:
        result = client.execute_cell(idx, kc, timeout=timeout)
    except TimeoutError:
        return None
    _stamp_cell_event(client, idx, "executed_at", _utc_now_iso())
    return result


def _print_exec_timeout(cell_id: str, timeout: float) -> None:
    """The client gave up waiting, but the kernel keeps running the cell. Its
    execution_count is now orphaned (it never lands), so the cell reads running
    forever and `nb-collab wait` hangs on it. Make this distinct from a failure
    (exit 1) and from completion (exit 0): loud, EXIT_TIMEOUT (2)."""
    print("status: TIMEOUT — kernel still running")
    print(f"timeout: {timeout:g}")
    print(_exec_timeout_message(cell_id, timeout), file=sys.stderr)


def _print_exec_report(client: NbModelClient, cell_id: str, result: dict[str, Any]) -> str:
    """Print status / execution_count / output tail for one run cell; return the status."""
    # Re-read the cell so the printed tail reflects the YDoc state
    # the operator will see (matches what `wait` emits).
    cell, _ = _find_cell_by_id(client, cell_id)
    status = result.get("status", "?")
    print(f"status: {status if status != 'ok' else 'done'}")
    print(f"execution_count: {_fmt_exec_count(result.get('execution_count'))}")
    tail = _format_output_tail((cell or {}).get("outputs", []) if cell else [])
    if tail:
        print("--- output ---")
        sys.stdout.write(tail)
        if not tail.endswith("\n"):
            print()
    return status


def _run_cell_on_open_client(
    client: NbModelClient, idx: int, cell_id: str, server_url: str, token: str,
    rel_path: str, timeout: float,
) -> int:
    """Execute cell ``idx`` against the notebook's live kernel and print the result.

    Shared by ``execute-cell`` and ``append --execute``: assumes ``client`` is
    already synced and the policy gate has passed. Opens and closes its own
    kernel client (exec-all holds one across a whole run instead). Returns
    EXIT_OK on a clean run, EXIT_ERROR on a cell error, EXIT_TIMEOUT if the
    client gives up while the kernel keeps running the cell (orphaned
    execution_count).
    """
    kernel_id, kc = _open_kernel_client(server_url, token, rel_path)
    print(f"  executing code @ {idx} id={cell_id} kernel={kernel_id}")
    try:
        result = _exec_on_kernel(client, idx, kc, timeout)
    finally:
        kc.stop_channels()

    if result is None:
        _print_exec_timeout(cell_id, timeout)
        return EXIT_TIMEOUT
    return EXIT_OK if _print_exec_report(client, cell_id, result) == "ok" else EXIT_ERROR


async def _execute_cell(
    notebook_path: Path,
    cell_id: str,
    timeout: float,
    server_url: str | None,
    token: str | None,
) -> int:
    if not notebook_path.exists():
        sys.exit(f"error: notebook does not exist: {notebook_path}")
    if not notebook_path.is_file() or notebook_path.suffix != ".ipynb":
        sys.exit(f"error: not an .ipynb file: {notebook_path}")
    _warn_if_legacy_format(notebook_path)

    server_url, token, root = _resolve_with_overrides(notebook_path, server_url, token)
    rel_path = _rel_path(notebook_path, root)

    try:
        ws_url = get_jupyter_notebook_websocket_url(server_url, rel_path, token)
    except Exception as e:
        sys.exit(f"error: failed to resolve collaboration room ({type(e).__name__}: {e})")

    try:
        async with NbModelClient(ws_url, path=rel_path, ws_max_body_size=WS_MAX_BODY_SIZE) as client:
            await client.wait_until_synced()
            _require_policy(client, EXECUTE_POLICIES, "execute-cell")

            cell, idx = _find_cell_by_id(client, cell_id)
            if cell is None:
                sys.exit(f"error: cell id not found: {cell_id}")
            if cell.get("cell_type") != "code":
                sys.exit(f"error: cell @ {idx} is not a code cell (type={cell.get('cell_type')!r})")

            print(f"connected: {server_url} path={rel_path} cells={len(client)}")
            return _run_cell_on_open_client(
                client, idx, cell_id, server_url, token, rel_path, timeout
            )
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"error: execute-cell failed ({type(e).__name__}: {e})")


def _cmd_execute_cell(args: argparse.Namespace) -> int:
    return asyncio.run(
        _execute_cell(
            args.notebook,
            args.cell_id,
            args.timeout,
            args.server_url,
            args.token,
        )
    )


def _cell_source_text(cell: dict[str, Any]) -> str:
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _code_cell_targets(client: NbModelClient) -> list[tuple[int, str]]:
    """Non-blank code cells in document order — exec-all's run list.

    Markdown/raw cells have nothing to execute, and a blank code cell only
    burns a kernel round-trip and an execution_count.
    """
    targets: list[tuple[int, str]] = []
    for idx in range(len(client)):
        cell = client[idx]
        if cell.get("cell_type") != "code":
            continue
        if not _cell_source_text(cell).strip():
            continue
        targets.append((idx, cell.get("id", "")))
    return targets


def _run_all_on_open_client(
    client: NbModelClient, targets: list[tuple[int, str]], server_url: str,
    token: str, rel_path: str, timeout: float,
) -> int:
    """Run every cell in ``targets`` on ONE kernel client, stopping at the first
    error — JupyterLab's Run All Cells semantics, no restart."""
    kernel_id, kc = _open_kernel_client(server_url, token, rel_path)
    print(f"  kernel={kernel_id} cells={len(targets)} timeout={timeout:g}s/cell")
    ran = 0
    try:
        for idx, cell_id in targets:
            started = time.monotonic()
            result = _exec_on_kernel(client, idx, kc, timeout)
            elapsed = time.monotonic() - started
            if result is None:
                print(f"  TIMEOUT @ {idx} id={cell_id} ({elapsed:.1f}s)")
                _print_exec_timeout(cell_id, timeout)
                print(f"exec-all: stopped at cell {ran + 1} of {len(targets)}")
                return EXIT_TIMEOUT
            if result.get("status") != "ok":
                print(f"  error @ {idx} id={cell_id} ({elapsed:.1f}s)")
                _print_exec_report(client, cell_id, result)
                print(f"exec-all: stopped at cell {ran + 1} of {len(targets)}")
                return EXIT_ERROR
            ran += 1
            print(f"  ok    @ {idx} id={cell_id} ({elapsed:.1f}s)")
    finally:
        kc.stop_channels()
    print(f"exec-all: {ran} cells ran")
    return EXIT_OK


async def _exec_all(
    notebook_path: Path,
    timeout: float,
    server_url: str | None,
    token: str | None,
) -> int:
    if not notebook_path.exists():
        sys.exit(f"error: notebook does not exist: {notebook_path}")
    if not notebook_path.is_file() or notebook_path.suffix != ".ipynb":
        sys.exit(f"error: not an .ipynb file: {notebook_path}")
    _warn_if_legacy_format(notebook_path)

    server_url, token, root = _resolve_with_overrides(notebook_path, server_url, token)
    rel_path = _rel_path(notebook_path, root)

    try:
        ws_url = get_jupyter_notebook_websocket_url(server_url, rel_path, token)
    except Exception as e:
        sys.exit(f"error: failed to resolve collaboration room ({type(e).__name__}: {e})")

    try:
        async with NbModelClient(ws_url, path=rel_path, ws_max_body_size=WS_MAX_BODY_SIZE) as client:
            await client.wait_until_synced()
            _require_policy(client, EXECUTE_POLICIES, "exec-all")

            print(f"connected: {server_url} path={rel_path} cells={len(client)}")
            targets = _code_cell_targets(client)
            if not targets:
                print("exec-all: 0 cells ran")
                return EXIT_OK
            return _run_all_on_open_client(
                client, targets, server_url, token, rel_path, timeout
            )
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"error: exec-all failed ({type(e).__name__}: {e})")


def _cmd_exec_all(args: argparse.Namespace) -> int:
    return asyncio.run(
        _exec_all(
            args.notebook,
            args.timeout,
            args.server_url,
            args.token,
        )
    )


async def _delete_cell(
    notebook_path: Path,
    cell_id: str,
    server_url: str | None,
    token: str | None,
    settle: float,
) -> int:
    if not notebook_path.exists():
        sys.exit(f"error: notebook does not exist: {notebook_path}")
    if not notebook_path.is_file() or notebook_path.suffix != ".ipynb":
        sys.exit(f"error: not an .ipynb file: {notebook_path}")
    _warn_if_legacy_format(notebook_path)

    server_url, token, root = _resolve_with_overrides(notebook_path, server_url, token)
    rel_path = _rel_path(notebook_path, root)

    try:
        ws_url = get_jupyter_notebook_websocket_url(server_url, rel_path, token)
    except Exception as e:
        sys.exit(f"error: failed to resolve collaboration room ({type(e).__name__}: {e})")

    try:
        async with NbModelClient(ws_url, path=rel_path, ws_max_body_size=WS_MAX_BODY_SIZE) as client:
            await client.wait_until_synced()
            _require_policy(client, DELETE_POLICIES, "delete-cell")

            cell, idx = _find_cell_by_id(client, cell_id)
            if cell is None:
                sys.exit(f"error: cell id not found: {cell_id}")
            kind = cell.get("cell_type", "?")

            print(f"connected: {server_url} path={rel_path} cells={len(client)}")
            print(f"  deleting {kind} @ {idx} id={cell_id}")
            client.delete_cell(idx)
            await asyncio.sleep(settle)
            print(f"done. cells now = {len(client)}")
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"error: delete-cell failed ({type(e).__name__}: {e})")
    return EXIT_OK


def _cmd_delete_cell(args: argparse.Namespace) -> int:
    return asyncio.run(
        _delete_cell(
            args.notebook,
            args.cell_id,
            args.server_url,
            args.token,
            args.settle,
        )
    )


def _find_cell_by_id(client: NbModelClient, cell_id: str) -> tuple[dict[str, Any] | None, int]:
    for idx in range(len(client)):
        cell = client[idx]
        if cell.get("id") == cell_id:
            return cell, idx
    return None, -1


def _format_output_tail(outputs: list[dict[str, Any]], max_chars: int = OUTPUT_TAIL_MAX_CHARS) -> str:
    chunks: list[str] = []
    for out in outputs:
        kind = out.get("output_type")
        if kind == "stream":
            chunks.append(out.get("text", ""))
        elif kind == "execute_result":
            data = out.get("data", {})
            text = data.get("text/plain", "")
            if text:
                chunks.append(text + "\n")
        elif kind == "error":
            tb = out.get("traceback") or []
            chunks.append("\n".join(tb) + "\n")
        elif kind == "display_data":
            data = out.get("data", {})
            text = data.get("text/plain", "")
            if text:
                chunks.append(text + "\n")
    chunks = _collapse_runs(chunks)
    joined = _ANSI_RE.sub("", "".join(chunks))
    if len(joined) > max_chars:
        joined = "...[truncated]...\n" + joined[-max_chars:]
    return joined


# A sweep progress bar persists one display_data output per update under the
# RTC notebook stack — hundreds to thousands of identical `<IPython.core...>`
# text/plain placeholders per measure cell. Collapse runs of identical chunks
# so the capped tail carries real signal, not repeated noise.
_COLLAPSE_RUN_MIN = 3


def _collapse_runs(chunks: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(chunks):
        j = i + 1
        while j < len(chunks) and chunks[j] == chunks[i]:
            j += 1
        run = j - i
        if run >= _COLLAPSE_RUN_MIN:
            out.append(chunks[i])
            out.append(f"[... ×{run} identical outputs collapsed ...]\n")
        else:
            out.extend(chunks[i:j])
        i = j
    return out


def _fmt_exec_count(value: Any) -> str:
    if value is None:
        return "None"
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return str(value)


def _timeout_message(cell_id: str, timeout: float, last_count: Any) -> str:
    """Loud, unambiguous stderr line for a `wait` timeout.

    The QC0426 session read a quiet stdout ``status: timeout`` as completion
    on a 19-min sweep that outran the internal cap. This line says, in plain
    words, that the cell did NOT finish.
    """
    return (
        f"nb-collab wait: TIMED OUT after {timeout:g}s — cell {cell_id} "
        f"is STILL RUNNING (execution_count unchanged at "
        f"{_fmt_exec_count(last_count)}). It did NOT finish. Re-run "
        f"`nb-collab wait` (raise --timeout for longer sweeps) or check "
        f"the live notebook."
    )


def _exec_timeout_message(cell_id: str, timeout: float) -> str:
    """Loud stderr line for an execute client-side timeout.

    The client gave up waiting but the kernel keeps running the cell, so its
    execution_count is orphaned (never lands). Distinct from a failure (exit 1)
    and from completion (exit 0): EXIT_TIMEOUT (2)."""
    return (
        f"nb-collab execute: client TIMED OUT after {timeout:g}s — the KERNEL "
        f"IS STILL RUNNING cell {cell_id}. NOT a failure, NOT completion. The "
        f"cell's execution_count is orphaned (it will read running indefinitely; "
        f"`nb-collab wait` hangs on it). Monitor completion via hera-watch / the "
        f"data dir, not cell state. For long runs, background execute with a "
        f"larger --timeout so the client survives to finalize the cell."
    )


def _emit_done(cell: dict[str, Any]) -> None:
    print("status: done")
    print(f"execution_count: {_fmt_exec_count(cell.get('execution_count'))}")
    tail = _format_output_tail(cell.get("outputs", []))
    if tail:
        print("--- output ---")
        sys.stdout.write(tail)
        if not tail.endswith("\n"):
            print()


async def _wait(
    notebook_path: Path,
    cell_id: str,
    timeout: float | None,
    poll: float,
    wait_for_rerun: bool,
    server_url: str | None,
    token: str | None,
) -> int:
    if not notebook_path.exists():
        print(f"status: error\nreason: notebook does not exist: {notebook_path}")
        return EXIT_ERROR
    if not notebook_path.is_file() or notebook_path.suffix != ".ipynb":
        print(f"status: error\nreason: not an .ipynb file: {notebook_path}")
        return EXIT_ERROR
    _warn_if_legacy_format(notebook_path)

    try:
        server_url, token, root = _resolve_with_overrides(notebook_path, server_url, token)
    except SystemExit as e:
        print(f"status: error\nreason: {e}")
        return EXIT_ERROR
    rel_path = _rel_path(notebook_path, root)

    try:
        ws_url = get_jupyter_notebook_websocket_url(server_url, rel_path, token)
    except Exception as e:
        print(f"status: error\nreason: failed to resolve collaboration room ({type(e).__name__}: {e})")
        return EXIT_ERROR

    try:
        async with NbModelClient(ws_url, path=rel_path, ws_max_body_size=WS_MAX_BODY_SIZE) as client:
            await client.wait_until_synced()

            initial_cell, _ = _find_cell_by_id(client, cell_id)
            if initial_cell is None:
                print(f"status: error\nreason: cell id not found: {cell_id}")
                return EXIT_ERROR

            baseline = initial_cell.get("execution_count")

            if not wait_for_rerun and baseline is not None:
                _emit_done(initial_cell)
                return EXIT_OK

            # --follow (timeout is None) lifts the deadline entirely so a
            # backgrounded wait can ride a multi-hour autonomous sweep to
            # completion without re-arming. A finite timeout still bounds the
            # foreground / medium-run case.
            deadline = None if timeout is None else time.monotonic() + timeout
            last_count = baseline
            while deadline is None or time.monotonic() < deadline:
                await asyncio.sleep(poll)
                cell, _ = _find_cell_by_id(client, cell_id)
                if cell is None:
                    print("status: deleted")
                    return EXIT_DELETED
                count = cell.get("execution_count")
                last_count = count
                if wait_for_rerun:
                    if count is not None and count != baseline:
                        _emit_done(cell)
                        return EXIT_OK
                else:
                    if count is not None:
                        _emit_done(cell)
                        return EXIT_OK

            # Make the timeout impossible to mistake for completion. The stdout
            # status itself is loud (the QC0426 session read a quiet
            # `status: timeout` as done on a sweep that outran the cap, twice),
            # backed by a loud stderr line; EXIT_TIMEOUT (2) is distinct from
            # the success (0) a real finish returns. (deadline is non-None here:
            # --follow never falls out of the loop.)
            assert timeout is not None
            print("status: TIMEOUT — cell did NOT finish")
            print(f"last_execution_count: {_fmt_exec_count(last_count)}")
            print(_timeout_message(cell_id, timeout, last_count), file=sys.stderr)
            return EXIT_TIMEOUT
    except Exception as e:
        print(f"status: error\nreason: wait failed ({type(e).__name__}: {e})")
        return EXIT_ERROR


def _cmd_wait(args: argparse.Namespace) -> int:
    # --follow lifts the deadline (no timeout) for backgrounded multi-hour
    # waits; otherwise the finite --timeout bounds the wait.
    timeout = None if args.follow else args.timeout
    return asyncio.run(
        _wait(
            args.notebook,
            args.cell_id,
            timeout,
            args.poll,
            args.wait_for_rerun,
            args.server_url,
            args.token,
        )
    )


async def _interrupt(
    notebook_path: Path,
    cell_id: str | None,
    confirm_timeout: float,
    poll: float,
    server_url: str | None,
    token: str | None,
) -> int:
    if not notebook_path.exists():
        sys.exit(f"error: notebook does not exist: {notebook_path}")
    if not notebook_path.is_file() or notebook_path.suffix != ".ipynb":
        sys.exit(f"error: not an .ipynb file: {notebook_path}")

    server_url, token, root = _resolve_with_overrides(notebook_path, server_url, token)
    rel_path = _rel_path(notebook_path, root)

    kernel_id = _find_kernel_for_path(server_url, token, rel_path)
    if kernel_id is None:
        sys.exit(
            f"error: no running kernel for {rel_path} — nothing to interrupt."
        )

    # Bare interrupt: stop whatever the kernel is running. No YDoc needed.
    if cell_id is None:
        state = _kernel_execution_state(server_url, token, kernel_id)
        print(f"kernel {kernel_id} execution_state={state}")
        _interrupt_kernel(server_url, token, kernel_id)
        print("status: interrupt-sent")
        return EXIT_OK

    # Guarded interrupt: only fire if cell_id is the cell currently executing.
    try:
        ws_url = get_jupyter_notebook_websocket_url(server_url, rel_path, token)
    except Exception as e:
        sys.exit(f"error: failed to resolve collaboration room ({type(e).__name__}: {e})")

    try:
        async with NbModelClient(ws_url, path=rel_path, ws_max_body_size=WS_MAX_BODY_SIZE) as client:
            await client.wait_until_synced()

            cell, idx = _find_cell_by_id(client, cell_id)
            if cell is None:
                sys.exit(f"error: cell id not found: {cell_id}")

            print(f"connected: {server_url} path={rel_path} cells={len(client)}")
            kstate = _kernel_execution_state(server_url, token, kernel_id)
            if not _cell_is_running(cell, kstate):
                print(
                    f"not interrupting: cell @ {idx} id={cell_id} is not executing "
                    f"(kernel={kstate}, execution_count={cell.get('execution_count')!r})."
                )
                return EXIT_NOT_RUNNING

            print(f"  cell @ {idx} id={cell_id} is running; interrupting kernel {kernel_id}")
            _interrupt_kernel(server_url, token, kernel_id)

            # Confirm the interrupt landed: poll until the cell completes (its
            # execution_count goes non-null — the same cross-client signal `wait`
            # uses). sweep absorbs the SIGINT at its next safe point, so this is
            # not instant — bounded by confirm_timeout.
            deadline = time.monotonic() + confirm_timeout
            while time.monotonic() < deadline:
                await asyncio.sleep(poll)
                cell, _ = _find_cell_by_id(client, cell_id)
                if cell is None:
                    print("status: deleted")
                    return EXIT_DELETED
                if cell.get("execution_count") is not None:
                    print("status: interrupted")
                    _emit_done(cell)
                    return EXIT_OK

            print("status: interrupt-sent (cell still running after confirm timeout)")
            return EXIT_TIMEOUT
    except SystemExit:
        raise
    except Exception as e:
        sys.exit(f"error: interrupt failed ({type(e).__name__}: {e})")


def _cmd_interrupt(args: argparse.Namespace) -> int:
    return asyncio.run(
        _interrupt(
            args.notebook,
            args.cell_id,
            args.confirm_timeout,
            args.poll,
            args.server_url,
            args.token,
        )
    )


def _make_append_cell_action(
    kind_inline: str, kind_stdin: str | None = None
) -> type[argparse.Action]:
    """Return an argparse Action that appends (kind, value) tuples to its dest.

    All six append-cell flags (--markdown, --code, --markdown-file,
    --code-file, plus the stdin variants of the first two) share the same
    dest ("cells") so cell order on the CLI is preserved across flag types.

    If ``kind_stdin`` is set and the supplied value is exactly ``"-"``,
    the tuple is tagged with ``kind_stdin`` and a ``None`` source — the
    actual source is filled in later by the stdin resolution pass.
    """

    class _AppendCellAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):  # noqa: ARG002
            items = getattr(namespace, self.dest, None)
            items = [] if items is None else list(items)
            if kind_stdin is not None and values == "-":
                items.append((kind_stdin, None))
            else:
                items.append((kind_inline, values))
            setattr(namespace, self.dest, items)

    _AppendCellAction.__name__ = f"AppendCell_{kind_inline}_Action"
    return _AppendCellAction


def _cell_id_arg(raw: str) -> str:
    r"""argparse type for cell-id positionals: strip surrounding whitespace.

    Ids are usually produced by a ``print()`` loop; on Windows that emits
    CRLF, and a bash ``$(...)`` capture keeps the ``\r`` on every line but the
    last, so ``for id in $ids`` hands over ``<id>\r``. Exact-match lookup then
    fails with ``cell id not found`` for all but the last cell.
    """
    cell_id = raw.strip()
    if not cell_id:
        raise argparse.ArgumentTypeError("cell id is empty")
    return cell_id


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="nb-collab", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    ap = sub.add_parser(
        "append",
        help="Append cells to a live notebook (notebook must be served by a running JupyterLab).",
        description=(
            "Appends markdown and/or code cells at the end of a JupyterLab-open notebook "
            "via the YDoc/RTC channel. Inserted cells are tagged metadata.hera (a dict "
            "carrying the version tag and an appended_at UTC timestamp) so they can be "
            "filtered and timed later. Re-running with the same args double-inserts."
        ),
    )
    ap.add_argument("notebook", type=Path, help="Path to .ipynb (absolute or relative to cwd).")
    ap.add_argument(
        "--markdown",
        action=_make_append_cell_action("markdown", "markdown_stdin"),
        dest="cells",
        default=[],
        metavar="TEXT",
        help=(
            "Append a markdown cell with this source. Pass '-' to read the cell "
            f"from stdin; multiple '-' flags consume successive chunks separated "
            f"by a line of '{STDIN_DELIM}'. Repeatable; order preserved across "
            "all --markdown/--code variants."
        ),
    )
    ap.add_argument(
        "--code",
        action=_make_append_cell_action("code", "code_stdin"),
        dest="cells",
        default=[],
        metavar="TEXT",
        help=(
            "Append an un-executed code cell with this source. Pass '-' to read "
            "the cell from stdin (see --markdown for chunk semantics). Repeatable; "
            "order preserved across all --markdown/--code variants."
        ),
    )
    ap.add_argument(
        "--markdown-file",
        action=_make_append_cell_action("markdown_file"),
        dest="cells",
        default=[],
        metavar="PATH",
        help="Append a markdown cell whose source is read from PATH (UTF-8). Repeatable; order-preserved.",
    )
    ap.add_argument(
        "--code-file",
        action=_make_append_cell_action("code_file"),
        dest="cells",
        default=[],
        metavar="PATH",
        help="Append an un-executed code cell whose source is read from PATH (UTF-8). Repeatable; order-preserved.",
    )
    ap.add_argument(
        "--summary",
        default=None,
        metavar="TEXT",
        help=(
            "One-line dense spec of the proposed measurement. Rendered into "
            "the FIRST appended markdown cell, right after its leading "
            "heading (or prepended if the cell has none) as a timestamped "
            "blockquote: '> **14:32** · <summary>' — the clock is "
            "server-local time at append; _/* in the text are escaped for "
            "rendering. Also stamped verbatim to metadata.hera.summary on "
            "that cell. Requires at least one markdown cell among the "
            "appended cells (--markdown/--markdown-file); must not contain "
            "a backtick. At most once."
        ),
    )
    ap.add_argument(
        "--eta",
        default=None,
        metavar="DURATION",
        help=(
            "Expected runtime for the proposed measurement — '40m', '2h', or "
            "'1h30m' (optional <N>h then optional <N>m, h before m; at least "
            "one required, total > 0; fractional values rejected). A bare "
            "number like '40' is REJECTED — add the m/h suffix. Rendered "
            "into the FIRST appended markdown cell's blockquote line (with "
            "--summary or alone) as '**ETA ~15:12** (≈40 min)' in "
            "server-local time, computed from the same append instant; "
            "crossing local midnight adds ' (+1d)' right after the clock. "
            "Also stamped as an ISO-8601 UTC "
            "instant to metadata.hera.eta_at on that cell, and echoed to "
            "stdout as 'eta: ~15:12 (≈40 min)'. Requires at least one "
            "markdown cell among the appended cells. At most once."
        ),
    )
    run_group = ap.add_mutually_exclusive_group()
    run_group.add_argument(
        "--execute",
        action="store_true",
        help=(
            "After appending, run the last appended code cell YOURSELF by the id "
            "this append just created (never nb['cells'][-1] off the stale on-disk "
            "file). Policy-gated like execute-cell (append_exec or edit_exec), "
            "checked before any cell lands. Exit code reflects the cell's status. "
            "Mutually exclusive with --wait."
        ),
    )
    run_group.add_argument(
        "--wait",
        action="store_true",
        help=(
            "After appending, block until the OPERATOR runs the last appended "
            "code cell (its execution_count flips non-null) — append + wait in "
            "one call, no cell id to capture by hand. Does NOT execute anything, "
            "so it is permitted on an append_only (E0) measure notebook. Pair "
            "with --follow to background a no-deadline wait. Mutually exclusive "
            "with --execute."
        ),
    )
    ap.add_argument(
        "--follow",
        action="store_true",
        help=(
            "With --wait: lift the deadline entirely (no timeout) for a "
            "backgrounded wait. Use with run_in_background so a foreground call "
            "cannot hang past the harness's ~600s shell cap."
        ),
    )
    ap.add_argument("--server-url", help="Override server URL (default: auto-discover).")
    ap.add_argument("--token", help="Override server token (default: auto-discover).")
    ap.add_argument(
        "--settle",
        type=float,
        default=0.5,
        help="Seconds to wait after appending before disconnecting. Default 0.5.",
    )
    ap.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_EXEC_TIMEOUT,
        help=f"Foreground deadline (seconds) for --execute (cell run) or --wait "
        f"(operator run). Default {DEFAULT_EXEC_TIMEOUT}. With --wait, prefer "
        f"--follow to background a no-deadline wait; a timeout is loud and "
        f"distinct (status: TIMEOUT, stderr line, exit 2).",
    )
    ap.add_argument(
        "--poll",
        type=float,
        default=DEFAULT_WAIT_POLL,
        help=f"With --wait: polling interval in seconds. Default {DEFAULT_WAIT_POLL}.",
    )
    ap.set_defaults(func=_cmd_append)

    ep = sub.add_parser(
        "edit-cell",
        help="Replace an existing cell's source (policy-gated; requires edit_no_exec or edit_exec).",
        description=(
            "Rewrites the source of the cell with the given id, leaving the cell's "
            "position and id unchanged. Clears outputs and execution_count by default "
            "so the cell visibly reads 'needs re-run'. Refuses if the notebook's "
            "nb.metadata.hera.policy is 'append_only' (or missing — missing defaults to "
            "append_only as a safety fallback)."
        ),
    )
    ep.add_argument("notebook", type=Path, help="Path to .ipynb (absolute or relative to cwd).")
    ep.add_argument("cell_id", type=_cell_id_arg, help="Stable YDoc cell id of the cell to edit (printed by `nb-collab append`).")
    src_group = ep.add_mutually_exclusive_group(required=True)
    src_group.add_argument(
        "--source",
        metavar="TEXT",
        help="New cell source. Pass '-' to read all of stdin as the source.",
    )
    src_group.add_argument(
        "--source-file",
        metavar="PATH",
        help="Read new cell source from PATH (UTF-8).",
    )
    ep.add_argument(
        "--keep-outputs",
        action="store_true",
        help=(
            "Preserve the cell's existing outputs and execution_count. "
            "Default is to clear both so the cell reads 'needs re-run'."
        ),
    )
    ep.add_argument("--server-url", help="Override server URL (default: auto-discover).")
    ep.add_argument("--token", help="Override server token (default: auto-discover).")
    ep.add_argument(
        "--settle",
        type=float,
        default=0.5,
        help="Seconds to wait after editing before disconnecting. Default 0.5.",
    )
    ep.set_defaults(func=_cmd_edit_cell)

    xp = sub.add_parser(
        "execute-cell",
        help="Run an existing code cell against the notebook's kernel (policy=append_exec or edit_exec).",
        description=(
            "Executes the code cell with the given id against the kernel JupyterLab "
            "has open for the notebook (or starts a python3 kernel if no session "
            "exists). Outputs and execution_count land in the YDoc and propagate "
            "to all open tabs. Refuses unless nb.metadata.hera.policy is "
            "'append_exec' (autonomous measure notebooks — execute but not edit/"
            "delete) or 'edit_exec' (iris scratch / ana notebooks)."
        ),
    )
    xp.add_argument("notebook", type=Path, help="Path to .ipynb (absolute or relative to cwd).")
    xp.add_argument("cell_id", type=_cell_id_arg, help="Stable YDoc cell id of the cell to execute.")
    xp.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_EXEC_TIMEOUT,
        help=f"Seconds to wait for the cell to finish. Default {DEFAULT_EXEC_TIMEOUT} "
        f"(sub-CC-Bash-cap). On timeout the kernel keeps running the cell "
        f"(execution_count orphaned); exit 2 (TIMEOUT), distinct from failure.",
    )
    xp.add_argument("--server-url", help="Override server URL (default: auto-discover).")
    xp.add_argument("--token", help="Override server token (default: auto-discover).")
    xp.set_defaults(func=_cmd_execute_cell)

    ap = sub.add_parser(
        "exec-all",
        help="Run every code cell in document order on one kernel (policy=append_exec or edit_exec).",
        description=(
            "JupyterLab's 'Run All Cells' minus the kernel restart: every non-blank "
            "code cell, in document order, over one kernel connection (the first cell "
            "binds the kernel, starting a python3 session if none is open). Stops at "
            "the first cell error — later cells are never started. Same policy gate as "
            "execute-cell: 'append_exec' or 'edit_exec'. This is for setup-class cells "
            "(imports, instrument bring-up); a sweep is never run this way — append it "
            "and execute it on its own. Exit codes: 0 all ran, 1 cell error, 2 timeout."
        ),
    )
    ap.add_argument("notebook", type=Path, help="Path to .ipynb (absolute or relative to cwd).")
    ap.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_EXEC_ALL_TIMEOUT,
        help=f"Per-cell seconds to wait. Default {DEFAULT_EXEC_ALL_TIMEOUT:g} — setup "
        f"cells, not sweeps. On timeout the kernel keeps running that cell and no "
        f"later cell starts; exit 2 (TIMEOUT), distinct from failure.",
    )
    ap.add_argument("--server-url", help="Override server URL (default: auto-discover).")
    ap.add_argument("--token", help="Override server token (default: auto-discover).")
    ap.set_defaults(func=_cmd_exec_all)

    dp = sub.add_parser(
        "delete-cell",
        help="Remove an existing cell by id (policy=edit_exec only).",
        description=(
            "Removes the cell with the given id from the live notebook. Refuses unless "
            "nb.metadata.hera.policy is 'edit_exec'. delete-cell is intentionally the "
            "narrowest policy bucket because deletion is irreversible from the tool "
            "side; the operator can still undo from JupyterLab itself. Note "
            "'append_exec' does NOT grant delete — it preserves the append-only record."
        ),
    )
    dp.add_argument("notebook", type=Path, help="Path to .ipynb (absolute or relative to cwd).")
    dp.add_argument("cell_id", type=_cell_id_arg, help="Stable YDoc cell id of the cell to delete.")
    dp.add_argument("--server-url", help="Override server URL (default: auto-discover).")
    dp.add_argument("--token", help="Override server token (default: auto-discover).")
    dp.add_argument(
        "--settle",
        type=float,
        default=0.5,
        help="Seconds to wait after deleting before disconnecting. Default 0.5.",
    )
    dp.set_defaults(func=_cmd_delete_cell)

    wp = sub.add_parser(
        "wait",
        help="Wait for a specific cell to finish executing.",
        description=(
            "Polls a JupyterLab-open notebook over the YDoc/RTC channel until the cell "
            "with the given id has a non-null execution_count. If the cell already has "
            "an execution_count when wait connects, returns success immediately (success "
            "and cell-error both count as 'done'). Use --wait-for-rerun to instead "
            "baseline the current count and wait for it to change. A timeout is loud and "
            "distinct (status: TIMEOUT, a stderr line, exit 2) so it can't read as "
            "completion; --follow lifts the deadline for backgrounded multi-hour waits. "
            "Exit codes: 0 done, 1 error, 2 timeout, 3 cell deleted."
        ),
    )
    wp.add_argument("notebook", type=Path, help="Path to .ipynb (absolute or relative to cwd).")
    wp.add_argument("cell_id", type=_cell_id_arg, help="Stable YDoc cell id to wait on (printed by `nb-collab append`).")
    wp.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_WAIT_TIMEOUT,
        help=f"Seconds to wait before giving up. Default {DEFAULT_WAIT_TIMEOUT:g} "
        f"(covers the start-gate and most medium sweeps). A foreground wait can "
        f"outlive the harness's ~600s shell cap — use --follow (backgrounded) "
        f"for multi-hour runs, or a smaller --timeout for a foreground gate.",
    )
    wp.add_argument(
        "--follow",
        action="store_true",
        help="Lift the deadline entirely (no timeout) — for a backgrounded wait "
        "on a multi-hour autonomous sweep. Use with run_in_background so a "
        "foreground call can't hang past the shell cap.",
    )
    wp.add_argument(
        "--poll",
        type=float,
        default=DEFAULT_WAIT_POLL,
        help=f"Polling interval in seconds. Default {DEFAULT_WAIT_POLL}.",
    )
    wp.add_argument(
        "--wait-for-rerun",
        action="store_true",
        help="Treat the current execution_count as a baseline and wait for it to change.",
    )
    wp.add_argument("--server-url", help="Override server URL (default: auto-discover).")
    wp.add_argument("--token", help="Override server token (default: auto-discover).")
    wp.set_defaults(func=_cmd_wait)

    ip = sub.add_parser(
        "interrupt",
        help="Interrupt the notebook's kernel (the abort lever for autonomous sweeps).",
        description=(
            "Sends an interrupt to the kernel JupyterLab has open for the notebook — "
            "the REST equivalent of the Interrupt Kernel button. This is the safe "
            "abort for a running measurement: sweep absorbs the interrupt at its next "
            "safe point (between measurements), marks the run interrupted, preserves "
            "partial data, and leaves instruments holding. NEVER restarts or shuts "
            "down the kernel. Ungated — a stop is always permitted regardless of "
            "notebook policy. Refuses (without creating one) if no kernel is running. "
            "With --cell-id, interrupts ONLY if that cell is the one currently "
            "executing (execution_state=running), then confirms it stopped; otherwise "
            "it touches nothing — so a finished cell + an operator-started cell can't "
            "be hit by a stale abort. Exit codes: 0 interrupted, 1 error, 2 confirm "
            "timeout, 3 cell deleted, 4 cell not running (no action)."
        ),
    )
    ip.add_argument("notebook", type=Path, help="Path to .ipynb (absolute or relative to cwd).")
    ip.add_argument(
        "--cell-id",
        default=None,
        help=(
            "Only interrupt if this cell is the one currently executing. Omit to "
            "interrupt whatever the kernel is running."
        ),
    )
    ip.add_argument(
        "--confirm-timeout",
        type=float,
        default=DEFAULT_INTERRUPT_CONFIRM_TIMEOUT,
        help=(
            "With --cell-id: seconds to wait for the cell to leave 'running' after "
            f"interrupting. Default {DEFAULT_INTERRUPT_CONFIRM_TIMEOUT}."
        ),
    )
    ip.add_argument(
        "--poll",
        type=float,
        default=DEFAULT_WAIT_POLL,
        help=f"Confirm-poll interval in seconds. Default {DEFAULT_WAIT_POLL}.",
    )
    ip.add_argument("--server-url", help="Override server URL (default: auto-discover).")
    ip.add_argument("--token", help="Override server token (default: auto-discover).")
    ip.set_defaults(func=_cmd_interrupt)

    return p


def main() -> int:
    if sys.platform == "win32":
        # Windows consoles default to cp1252; printed cell tails contain unicode.
        # newline="\n" keeps stdout from CRLF-translating printed cell ids: bash
        # $(...) strips only the final terminator, so captured ids keep a \r.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = _build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
