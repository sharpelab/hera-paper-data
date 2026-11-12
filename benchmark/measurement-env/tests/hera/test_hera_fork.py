from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FRONTIER = Path(__file__).resolve().parents[2] / "hera/evaluations/frontier"
sys.path.insert(0, str(FRONTIER))

from hera_fork import fork  # noqa: E402


@pytest.fixture
def session_dir(tmp_path: Path) -> Path:
    session = tmp_path / "session"
    session.mkdir()

    notebook = json.dumps({"cells": [{}]})
    (session / "test_measure.ipynb").write_text(notebook)
    (session / "test_ana.ipynb").write_text(notebook)

    (session / "future_context.md").write_text("context")
    (session / "prepare.sh").write_text("#!/bin/sh\n")
    (session / "ignored.txt").write_text("not session context")
    (session / "session_notes.md").write_text("uncut notes")
    (session / "hera_scratch").mkdir()
    (session / "hera_scratch" / "scratch.md").write_text("uncut scratch")
    (session / "data" / "0").mkdir(parents=True)

    return session


def make_fork(session_dir: Path, tmp_path: Path, **kwargs) -> tuple[Path, dict]:
    dest = tmp_path / "fork"
    fork(session_dir, 0, 0, 0, dest=dest, fork_id="test", **kwargs)
    manifest = json.loads((dest / "fork.json").read_text())
    return dest, manifest


def test_default_discovers_context_files_but_excludes_uncut_notes(
    session_dir: Path, tmp_path: Path
):
    dest, manifest = make_fork(session_dir, tmp_path)

    assert (dest / "future_context.md").read_text() == "context"
    assert (dest / "prepare.sh").read_text() == "#!/bin/sh\n"
    assert not (dest / "ignored.txt").exists()
    assert not (dest / "session_notes.md").exists()
    assert not (dest / "hera_scratch").exists()
    assert manifest["md_files"] == ["future_context.md", "prepare.sh"]
    assert manifest["notes_files"] == []


def test_include_notes_restores_both_excluded_note_paths(
    session_dir: Path, tmp_path: Path
):
    dest, manifest = make_fork(session_dir, tmp_path, include_notes=True)

    assert (dest / "session_notes.md").read_text() == "uncut notes"
    assert (dest / "hera_scratch" / "scratch.md").read_text() == "uncut scratch"
    assert manifest["notes_files"] == ["hera_scratch", "session_notes.md"]


def test_note_and_context_flags_are_independent(session_dir: Path, tmp_path: Path):
    dest, manifest = make_fork(
        session_dir, tmp_path, include_md=False, include_notes=True
    )

    assert not (dest / "future_context.md").exists()
    assert not (dest / "prepare.sh").exists()
    assert (dest / "session_notes.md").is_file()
    assert (dest / "hera_scratch").is_dir()
    assert manifest["md_files"] == []
    assert manifest["notes_files"] == ["hera_scratch", "session_notes.md"]


def test_device_card_drops_post_frontier_sections_before_leak_scan(
    session_dir: Path, tmp_path: Path
):
    (session_dir / "device_card.md").write_text(
        "# Device\n\n## Prior — ESTABLISHED 2026-06-19 (run 0)\nkeep\n\n"
        "## Future — ESTABLISHED 2026-06-20 (run 2)\nsecret result\n\n"
        "## Static\nkeep too\n"
    )

    dest, manifest = make_fork(
        session_dir, tmp_path, leak_terms=["secret result"]
    )

    card = (dest / "device_card.md").read_text()
    assert "Prior" in card and "Static" in card
    assert "Future" not in card and "secret result" not in card
    assert manifest["device_card_sections_dropped"] == [
        "Future — ESTABLISHED 2026-06-20 (run 2)"
    ]


def test_leak_terms_scan_regular_markdown(session_dir: Path, tmp_path: Path):
    from hera_fork import LeakError

    (session_dir / "future_context.md").write_text("post-cut secret")

    with pytest.raises(LeakError, match="post-cut secret"):
        make_fork(session_dir, tmp_path, leak_terms=["post-cut secret"])


def test_timestamp_cut_slices_notes_and_filters_scratch(tmp_path: Path):
    from hera_fork import LeakError

    session = tmp_path / "session_with_ts"
    session.mkdir()

    m_nb = {
        "cells": [
            {
                "metadata": {
                    "hera": {
                        "executed_at": "2026-06-20T04:30:00+00:00",
                        "appended_at": "2026-06-20T04:20:00+00:00",
                    }
                }
            }
        ]
    }
    a_nb = {
        "cells": [
            {
                "metadata": {
                    "hera": {
                        "appended_at": "2026-06-20T04:35:00+00:00",
                    }
                }
            }
        ]
    }
    (session / "test_measure.ipynb").write_text(json.dumps(m_nb))
    (session / "test_ana.ipynb").write_text(json.dumps(a_nb))

    raw_notes = (
        "# Notes\n"
        "- TOOLING — good\n"
        "- STEP 1 — done\n"
        "- TIMING — field sweeps run 8.7 s/pt\n"
        "- RECIPE FIX / sdh — next\n"
    )
    (session / "session_notes.md").write_text(raw_notes)

    scratch = session / "hera_scratch"
    scratch.mkdir()
    (scratch / "early.py").write_text("early code")
    (scratch / "late.py").write_text("late code")

    transcripts = session / "transcripts"
    transcripts.mkdir()
    t_lines = [
        json.dumps({
            "type": "assistant",
            "timestamp": "2026-06-20T04:25:00Z",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Write", "input": {"file_path": "/path/hera_scratch/early.py"}}
                ]
            }
        }),
        json.dumps({
            "type": "assistant",
            "timestamp": "2026-06-20T04:50:00Z",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Write", "input": {"file_path": "/path/hera_scratch/late.py"}}
                ]
            }
        }),
    ]
    (transcripts / "session.jsonl").write_text("\n".join(t_lines) + "\n")

    dest = tmp_path / "fork_ts"
    fork(session, 0, 0, 0, include_notes=True, leak_terms=["field sweeps"], dest=dest, fork_id="ts_test")
    manifest = json.loads((dest / "fork.json").read_text())

    assert manifest["notes_cut_at"] == "2026-06-20T04:35:00+00:00"
    assert manifest["notes_lines_kept"] == 3
    notes = (dest / "session_notes.md").read_text()
    assert "- STEP 1 — done" in notes
    assert "- TIMING" not in notes

    assert (dest / "hera_scratch" / "early.py").exists()
    assert not (dest / "hera_scratch" / "late.py").exists()
    assert manifest["scratch_files_kept"] == ["early.py"]
    assert manifest["scratch_files_excluded"] == ["late.py"]

    # Transcripts truncated to 1 line
    t_dest = (dest / "transcripts" / "session.jsonl").read_text().splitlines()
    assert len(t_dest) == 1
    assert "early.py" in t_dest[0]

    # Leak term test: if we include a term present in early notes, it fails
    dest_leak = tmp_path / "fork_leak"
    with pytest.raises(LeakError, match="STEP 1"):
        fork(session, 0, 0, 0, include_notes=True, leak_terms=["STEP 1"], dest=dest_leak, fork_id="leak_test")
