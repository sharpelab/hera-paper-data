import json
import shutil
import sys
from pathlib import Path

import pytest

from hera.trajectory import ReplayEngine, main


@pytest.fixture
def temp_workspace(tmp_path) -> Path:
    """Create a clean temporary workspace directory."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def engine(temp_workspace) -> ReplayEngine:
    return ReplayEngine(temp_workspace)


def test_init_creates_directories_and_graph(engine) -> None:
    assert not engine.is_initialized()
    engine.init()
    assert engine.is_initialized()
    assert engine.replay_dir.is_dir()
    assert engine.cache_dir.is_dir()
    assert engine.graph_path.is_file()

    # Verify graph structure
    graph = json.loads(engine.graph_path.read_text(encoding="utf-8"))
    assert "events" in graph
    assert isinstance(graph["events"], list)


def test_ignore_filtering(engine) -> None:
    engine.init()

    # Create ignored patterns and some files
    patterns = engine._get_ignore_patterns()
    assert ".git" in patterns
    assert ".replay" in patterns

    # Test path ignoring
    assert engine._should_ignore(".git", is_dir=True, patterns=patterns)
    assert engine._should_ignore(".git/config", is_dir=False, patterns=patterns)
    assert engine._should_ignore(".replay/graph.json", is_dir=False, patterns=patterns)
    assert engine._should_ignore(".venv/bin/python", is_dir=False, patterns=patterns)
    assert not engine._should_ignore("src/core/config.py", is_dir=False, patterns=patterns)


def test_custom_gitignore_patterns(engine) -> None:
    engine.init()
    
    # Write custom .gitignore
    gitignore = engine.workspace_dir / ".gitignore"
    gitignore.write_text("*.log\n/build/\ntemp_*\n", encoding="utf-8")

    patterns = engine._get_ignore_patterns()
    assert "*.log" in patterns
    assert "/build/" in patterns
    assert "temp_*" in patterns

    assert engine._should_ignore("error.log", is_dir=False, patterns=patterns)
    assert engine._should_ignore("build/output.bin", is_dir=False, patterns=patterns)
    assert engine._should_ignore("temp_file.txt", is_dir=False, patterns=patterns)
    assert not engine._should_ignore("src/error.py", is_dir=False, patterns=patterns)


def test_snapshot_and_manifest_fidelity(engine) -> None:
    engine.init()

    # Create dummy files in workspace
    file1 = engine.workspace_dir / "file1.txt"
    file1.write_text("Hello World", encoding="utf-8")

    subdir = engine.workspace_dir / "subdir"
    subdir.mkdir()
    file2 = subdir / "file2.py"
    file2.write_text("print('Hera')", encoding="utf-8")

    # Create an ignored file
    ignored_dir = engine.workspace_dir / ".venv"
    ignored_dir.mkdir()
    ignored_file = ignored_dir / "lib.py"
    ignored_file.write_text("ignored_code", encoding="utf-8")

    snapshot_id = engine.snapshot()
    assert snapshot_id is not None

    # Load and verify manifest
    manifest = engine.load_manifest(snapshot_id)
    assert "files" in manifest
    files = manifest["files"]

    assert "file1.txt" in files
    assert files["file1.txt"]["size"] == len("Hello World")
    assert "subdir/file2.py" in files
    assert files["subdir/file2.py"]["size"] == len("print('Hera')")

    # Ensure ignored files/directories are completely absent from manifest
    assert ".venv/lib.py" not in files


def test_log_event_and_causal_graph(engine) -> None:
    engine.init()

    file_a = engine.workspace_dir / "a.txt"
    file_a.write_text("State A", encoding="utf-8")

    # Log initial root event
    evt1 = engine.log_event(action="Initial prompt", metadata={"user": "Zack"})
    assert evt1 is not None

    # Modify file and log second event
    file_a.write_text("State B", encoding="utf-8")
    evt2 = engine.log_event(action="First agent tool call", parent_id=evt1)
    
    # Read graph
    graph = json.loads(engine.graph_path.read_text(encoding="utf-8"))
    events = graph["events"]
    assert len(events) == 2
    
    assert events[0]["id"] == evt1
    assert events[0]["parent_id"] is None
    assert events[0]["action"] == "Initial prompt"
    assert events[0]["metadata"] == {"user": "Zack"}

    assert events[1]["id"] == evt2
    assert events[1]["parent_id"] == evt1
    assert events[1]["action"] == "First agent tool call"


def test_rollback_restores_exact_state(engine) -> None:
    engine.init()

    # State 1: original files
    f1 = engine.workspace_dir / "f1.txt"
    f1.write_text("First version of F1", encoding="utf-8")
    evt1 = engine.log_event(action="State 1")

    # State 2: modified f1, added f2
    f1.write_text("Second version of F1", encoding="utf-8")
    f2 = engine.workspace_dir / "f2.txt"
    f2.write_text("This is F2", encoding="utf-8")
    evt2 = engine.log_event(action="State 2")

    # Rollback to State 1
    engine.rollback(evt1)

    # Check that f1 has been reverted and f2 has been deleted!
    assert f1.read_text(encoding="utf-8") == "First version of F1"
    assert not f2.exists()

    # Rollback to State 2
    engine.rollback(evt2)
    assert f1.read_text(encoding="utf-8") == "Second version of F1"
    assert f2.is_file()
    assert f2.read_text(encoding="utf-8") == "This is F2"


def test_fork_creates_isolated_workspace(engine, tmp_path) -> None:
    engine.init()

    # Setup initial state
    f1 = engine.workspace_dir / "f1.txt"
    f1.write_text("F1 initial text", encoding="utf-8")
    evt_id = engine.log_event(action="Initial Setup")

    # Fork to a new isolated directory
    fork_dir = tmp_path / "forked_workspace"
    engine.fork(evt_id, fork_dir)

    # Verify files exist in the fork
    fork_f1 = fork_dir / "f1.txt"
    assert fork_f1.is_file()
    assert fork_f1.read_text(encoding="utf-8") == "F1 initial text"

    # Verify that the fork has its own fully operational .replay repository copy
    fork_engine = ReplayEngine(fork_dir)
    assert fork_engine.is_initialized()
    assert len(json.loads(fork_engine.graph_path.read_text(encoding="utf-8"))["events"]) == 1


def test_diff_events(engine) -> None:
    engine.init()

    f1 = engine.workspace_dir / "f1.txt"
    f1.write_text("F1 v1", encoding="utf-8")
    evt1 = engine.log_event("evt1")

    # Create additions, modifications, deletions
    f1.write_text("F1 v2", encoding="utf-8")  # modified

    f2 = engine.workspace_dir / "f2.txt"
    f2.write_text("F2 content", encoding="utf-8")  # added

    evt2 = engine.log_event("evt2")

    changes = engine.diff_events(evt1, evt2)
    assert changes["added"] == ["f2.txt"]
    assert changes["modified"] == ["f1.txt"]
    assert changes["removed"] == []

    # Diff in reverse (2 -> 1)
    rev_changes = engine.diff_events(evt2, evt1)
    assert rev_changes["added"] == []
    assert rev_changes["modified"] == ["f1.txt"]
    assert rev_changes["removed"] == ["f2.txt"]


def test_cli_subcommands(engine, capsys) -> None:
    # Test CLI init
    rc = main(["--dir", str(engine.workspace_dir), "init"])
    assert rc == 0
    assert engine.is_initialized()

    # Test manual snapshot CLI
    rc = main(["--dir", str(engine.workspace_dir), "snapshot"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Created snapshot:" in captured.out

    # Test log-event CLI
    rc = main([
        "--dir", str(engine.workspace_dir),
        "log-event",
        "--action", "Testing Action",
        "--meta", '{"test": true}'
    ])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Logged event evt_" in captured.out

    # Get the actual event ID to test benchmark
    import json
    graph = json.loads(engine.graph_path.read_text(encoding="utf-8"))
    evt_id = graph["events"][-1]["id"]

    # Test benchmark CLI
    rc = main([
        "--dir", str(engine.workspace_dir),
        "replay",
        "--run-from", evt_id,
        "--agent", "codex"
    ])
    assert rc == 0
    captured = capsys.readouterr()
    assert "Isolated workspace ready" in captured.out

