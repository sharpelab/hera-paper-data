"""hera-trajectory — offline/live agent replay and trajectory forking engine.

Implements a Content-Addressable Storage (CAS) for file snapshotting, enabling arbitrary
rollback and trajectory branching/forking for LLM agents. Tracks a causal graph of states:
(S) -[a]-> (S') where S represents a filesystem state and 'a' is an action (prompt, tool call, etc.).
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_IGNORE = {
    ".replay",
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    ".ipynb_checkpoints",
    ".DS_Store",
    "*.pyc",
    "*.pyo",
    "*.pyd",
}


class ReplayEngine:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir.resolve()
        self.replay_dir = self.workspace_dir / ".replay"
        self.cache_dir = self.replay_dir / "cache"
        self.graph_path = self.replay_dir / "graph.json"

    def is_initialized(self) -> bool:
        return self.replay_dir.is_dir() and self.graph_path.is_file()

    def init(self) -> None:
        """Initialize the replay repository."""
        self.replay_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        if not self.graph_path.is_file():
            self.graph_path.write_text(json.dumps({"events": []}, indent=2), encoding="utf-8")

    def _get_ignore_patterns(self) -> list[str]:
        """Collect patterns to ignore during snapshotting from default and .gitignore."""
        patterns = list(DEFAULT_IGNORE)
        gitignore = self.workspace_dir / ".gitignore"
        if gitignore.is_file():
            try:
                for line in gitignore.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
            except Exception:
                pass
        return patterns

    def _should_ignore(self, rel_path: str, is_dir: bool, patterns: list[str]) -> bool:
        """Check if a path matches any ignore pattern."""
        # Normalize slashes
        path_str = rel_path.replace(os.sep, "/")
        if is_dir and not path_str.endswith("/"):
            path_str += "/"

        parts = path_str.strip("/").split("/")

        for pattern in patterns:
            pat = pattern.replace(os.sep, "/")
            is_dir_pattern = pat.endswith("/")
            is_anchored = pat.startswith("/")
            
            clean_pat = pat.strip("/")

            if is_anchored:
                # Matches only from the root
                if is_dir_pattern:
                    if path_str.startswith(clean_pat + "/") or path_str == clean_pat + "/":
                        return True
                else:
                    # Check if the whole path matches the pattern
                    if fnmatch.fnmatch(path_str, clean_pat) or fnmatch.fnmatch(path_str.rstrip("/"), clean_pat):
                        return True
            else:
                # Matches at any level
                if is_dir_pattern:
                    if clean_pat in parts:
                        idx = parts.index(clean_pat)
                        if idx < len(parts) - 1 or is_dir:
                            return True
                else:
                    # Non-directory pattern matches any part or full filename
                    for part in parts:
                        if fnmatch.fnmatch(part, clean_pat):
                            return True
                    if fnmatch.fnmatch(path_str, clean_pat) or fnmatch.fnmatch(path_str.rstrip("/"), clean_pat):
                        return True
        return False

    def _hash_file(self, file_path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _hash_data(self, data: bytes) -> str:
        """Compute SHA-256 hash of bytes."""
        return hashlib.sha256(data).hexdigest()

    def _add_blob(self, file_path: Path) -> str:
        """Add a file to the CAS cache, returning its hash."""
        file_hash = self._hash_file(file_path)
        part1 = file_hash[:2]
        part2 = file_hash[2:]
        bucket = self.cache_dir / part1
        bucket.mkdir(exist_ok=True)
        dest = bucket / part2
        if not dest.exists():
            shutil.copy2(file_path, dest)
        return file_hash

    def _add_manifest_blob(self, manifest_data: bytes) -> str:
        """Add a serialized JSON manifest to the CAS cache."""
        manifest_hash = self._hash_data(manifest_data)
        part1 = manifest_hash[:2]
        part2 = manifest_hash[2:]
        bucket = self.cache_dir / part1
        bucket.mkdir(exist_ok=True)
        dest = bucket / part2
        if not dest.exists():
            dest.write_bytes(manifest_data)
        return manifest_hash

    def _get_blob_path(self, file_hash: str) -> Path:
        """Get the path to a cached blob."""
        return self.cache_dir / file_hash[:2] / file_hash[2:]

    def snapshot(self) -> str:
        """Create a snapshot manifest of the workspace. Return its hash."""
        if not self.is_initialized():
            self.init()

        ignore_patterns = self._get_ignore_patterns()
        manifest_files = {}

        for root, dirs, files in os.walk(self.workspace_dir):
            root_path = Path(root)
            rel_root = root_path.relative_to(self.workspace_dir)

            # Skip ignored directories entirely during traversal
            if rel_root != Path("."):
                if self._should_ignore(str(rel_root), is_dir=True, patterns=ignore_patterns):
                    dirs[:] = []
                    continue

            # In-place modify dirs to skip walking ignored directories
            filtered_dirs = []
            for d in dirs:
                rel_dir = rel_root / d
                if not self._should_ignore(str(rel_dir), is_dir=True, patterns=ignore_patterns):
                    filtered_dirs.append(d)
            dirs[:] = filtered_dirs

            for file in files:
                rel_file = rel_root / file
                rel_str = str(rel_file)
                if self._should_ignore(rel_str, is_dir=False, patterns=ignore_patterns):
                    continue

                full_path = root_path / file
                if not full_path.is_file() or full_path.is_symlink():
                    continue

                try:
                    file_hash = self._add_blob(full_path)
                    is_exe = os.access(full_path, os.X_OK)
                    manifest_files[rel_str.replace(os.sep, "/")] = {
                        "hash": file_hash,
                        "size": full_path.stat().st_size,
                        "is_executable": is_exe,
                    }
                except Exception as e:
                    # Non-fatal error for unreadable files during snapshotting
                    print(f"Warning: skipped snapshotting file {rel_file} due to: {e}", file=sys.stderr)

        manifest = {
            "version": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files": manifest_files,
        }
        manifest_bytes = json.dumps(manifest, sort_keys=True, indent=2).encode("utf-8")
        return self._add_manifest_blob(manifest_bytes)

    def load_manifest(self, snapshot_id: str) -> dict:
        """Load and parse a snapshot manifest by its ID."""
        path = self._get_blob_path(snapshot_id)
        if not path.is_file():
            raise FileNotFoundError(f"Snapshot manifest {snapshot_id} not found in cache.")
        return json.loads(path.read_text(encoding="utf-8"))

    def log_event(self, action: str | dict, parent_id: str | None = None, metadata: dict | None = None) -> str:
        """Record an action transition, snapshot the workspace state, and log the event."""
        if not self.is_initialized():
            self.init()

        snapshot_id = self.snapshot()
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        
        # Load existing graph
        graph = json.loads(self.graph_path.read_text(encoding="utf-8"))
        
        # Validate parent
        if parent_id is not None:
            parent_exists = any(e["id"] == parent_id for e in graph["events"])
            if not parent_exists:
                raise ValueError(f"Parent event ID '{parent_id}' does not exist in the causal graph.")
        elif graph["events"]:
            # Default parent to the last logged event if not specified
            parent_id = graph["events"][-1]["id"]

        new_event = {
            "id": event_id,
            "parent_id": parent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "snapshot_id": snapshot_id,
            "metadata": metadata or {},
        }
        graph["events"].append(new_event)
        self.graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")
        return event_id

    def restore_workspace(self, snapshot_id: str, target_dir: Path | None = None) -> None:
        """Restore workspace (or target_dir) to the exact state represented by snapshot_id."""
        target_dir = (target_dir or self.workspace_dir).resolve()
        manifest = self.load_manifest(snapshot_id)
        files_to_restore = manifest.get("files", {})

        # 1. Delete files not present in the snapshot
        ignore_patterns = self._get_ignore_patterns()
        
        for root, dirs, files in os.walk(target_dir):
            root_path = Path(root)
            rel_root = root_path.relative_to(target_dir)

            if rel_root != Path("."):
                # Avoid cleaning up files in ignored folders (like .replay, .venv, etc.)
                if self._should_ignore(str(rel_root), is_dir=True, patterns=ignore_patterns):
                    dirs[:] = []
                    continue

            # Modify dirs to avoid scanning ignored subdirectories
            dirs[:] = [d for d in dirs if not self._should_ignore(str(rel_root / d), is_dir=True, patterns=ignore_patterns)]

            for file in files:
                rel_file = rel_root / file
                rel_str = str(rel_file).replace(os.sep, "/")
                if self._should_ignore(rel_str, is_dir=False, patterns=ignore_patterns):
                    continue

                if rel_str not in files_to_restore:
                    full_path = root_path / file
                    try:
                        full_path.unlink()
                    except OSError as e:
                        print(f"Warning: could not delete unmanifested file {rel_file}: {e}", file=sys.stderr)

        # 2. Restore/Update files
        for rel_str, file_meta in files_to_restore.items():
            dest_path = target_dir / rel_str
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            blob_path = self._get_blob_path(file_meta["hash"])
            if not blob_path.is_file():
                raise FileNotFoundError(f"Missing data block for {rel_str} (hash: {file_meta['hash']})")

            # Copy file from cache to target
            shutil.copy2(blob_path, dest_path)

            # Restore executable flag
            if file_meta.get("is_executable"):
                try:
                    os.chmod(dest_path, dest_path.stat().st_mode | 0o111)
                except OSError:
                    pass
            else:
                try:
                    os.chmod(dest_path, dest_path.stat().st_mode & ~0o111)
                except OSError:
                    pass

    def rollback(self, event_id: str) -> None:
        """Rollback the main workspace directory to the snapshot associated with event_id."""
        if not self.is_initialized():
            raise ValueError("Replay repository not initialized.")

        graph = json.loads(self.graph_path.read_text(encoding="utf-8"))
        event = next((e for e in graph["events"] if e["id"] == event_id), None)
        if not event:
            raise ValueError(f"Event ID '{event_id}' not found in the causal graph.")

        self.restore_workspace(event["snapshot_id"])

    def fork(self, event_id: str, dest_dir: Path) -> None:
        """Fork workspace state at event_id to an isolated dest_dir (soft copy)."""
        if not self.is_initialized():
            raise ValueError("Replay repository not initialized.")

        graph = json.loads(self.graph_path.read_text(encoding="utf-8"))
        event = next((e for e in graph["events"] if e["id"] == event_id), None)
        if not event:
            raise ValueError(f"Event ID '{event_id}' not found in the causal graph.")

        dest_dir = dest_dir.resolve()
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Restore snapshot to the destination folder
        self.restore_workspace(event["snapshot_id"], target_dir=dest_dir)

        # Copy .replay metadata to the fork so it retains history and has access to blobs!
        dest_replay = dest_dir / ".replay"
        shutil.copytree(self.replay_dir, dest_replay, dirs_exist_ok=True)

    def get_event_tree_str(self) -> str:
        """Return a string-based tree diagram of the causal graph events."""
        if not self.is_initialized():
            return "(Uninitialized Replay Engine)"

        graph = json.loads(self.graph_path.read_text(encoding="utf-8"))
        events = graph.get("events", [])
        if not events:
            return "(No events logged)"

        # Group events by parent
        by_parent: dict[str | None, list[dict]] = {}
        for e in events:
            parent = e.get("parent_id")
            by_parent.setdefault(parent, []).append(e)

        # Find roots (typically parent is None or missing from events list)
        event_ids = {e["id"] for e in events}
        roots = [e for e in events if e.get("parent_id") not in event_ids]

        lines = []

        def render_node(node: dict, prefix: str = "", is_last: bool = True) -> None:
            connector = "└── " if is_last else "├── "
            action_snippet = str(node["action"])
            if len(action_snippet) > 50:
                action_snippet = action_snippet[:47] + "..."
            
            # Format display line
            lines.append(f"{prefix}{connector}{node['id']} [{node['timestamp'][:19]}] - {action_snippet}")
            
            # Child prefix
            new_prefix = prefix + ("    " if is_last else "│   ")
            children = by_parent.get(node["id"], [])
            for idx, child in enumerate(children):
                render_node(child, new_prefix, idx == len(children) - 1)

        for idx, root in enumerate(roots):
            render_node(root, is_last=(idx == len(roots) - 1))

        return "\n".join(lines)

    def diff_events(self, id1: str, id2: str) -> dict[str, list[str]]:
        """Compute file-level changes between two event snapshots."""
        if not self.is_initialized():
            raise ValueError("Replay repository not initialized.")

        graph = json.loads(self.graph_path.read_text(encoding="utf-8"))
        evt1 = next((e for e in graph["events"] if e["id"] == id1), None)
        evt2 = next((e for e in graph["events"] if e["id"] == id2), None)
        if not evt1 or not evt2:
            raise ValueError("One or both event IDs not found.")

        m1 = self.load_manifest(evt1["snapshot_id"]).get("files", {})
        m2 = self.load_manifest(evt2["snapshot_id"]).get("files", {})

        added = []
        removed = []
        modified = []

        for path, meta2 in m2.items():
            if path not in m1:
                added.append(path)
            elif m1[path]["hash"] != meta2["hash"]:
                modified.append(path)

        for path in m1:
            if path not in m2:
                removed.append(path)

        return {
            "added": sorted(added),
            "removed": sorted(removed),
            "modified": sorted(modified),
        }


# --------------------------------------------------------------------- #
# CLI Subcommands & Main Entrypoint
# --------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="hera-trajectory — high-fidelity CAS agent replay & trajectory branching engine."
    )
    parser.add_argument(
        "--dir", "-C", default=".", help="Root directory of the workspace (default: current directory)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # init
    subparsers.add_parser("init", help="Initialize the trajectory/replay repository in the workspace.")

    # status
    subparsers.add_parser("status", help="Print the causal event graph of agent trajectories.")

    # snapshot
    subparsers.add_parser("snapshot", help="Force a manual snapshot of the current workspace.")

    # log-event
    log_parser = subparsers.add_parser("log-event", help="Log a transition event and capture a workspace snapshot.")
    log_parser.add_argument("--action", required=True, help="Description or JSON string representing the action.")
    log_parser.add_argument("--parent", default=None, help="ID of the parent event (defaults to last event).")
    log_parser.add_argument("--meta", default=None, help="Optional JSON string of custom metadata.")

    # rollback
    rollback_parser = subparsers.add_parser("rollback", help="Rollback workspace to a target event's file state.")
    rollback_parser.add_argument("event_id", help="Event ID to rollback to.")

    # fork
    fork_parser = subparsers.add_parser("fork", help="Fork trajectory state into an isolated new directory.")
    fork_parser.add_argument("event_id", help="Event ID to fork from.")
    fork_parser.add_argument("dest_dir", help="Destination path for the isolated fork.")

    # diff
    diff_parser = subparsers.add_parser("diff", help="Diff the file-level states of two events.")
    diff_parser.add_argument("id1", help="First event ID.")
    diff_parser.add_argument("id2", help="Second event ID.")

    # replay (Phase 1: checkpoint-based single-turn; Phase 2: trajectory-event replay)
    replay_parser = subparsers.add_parser(
        "replay",
        help="Replay a measurement session from a checkpoint (Phase 1) "
             "or trajectory event (Phase 2)."
    )
    replay_parser.add_argument("--checkpoint", type=Path, default=None,
                               help="Checkpoint directory (default: cwd). Must contain "
                                    "frontiers/ and a measure notebook.")
    replay_parser.add_argument("--run-from",
                               help="Event ID to fork from for multi-turn replay "
                                    "(Phase 2, future)")
    replay_parser.add_argument("--frontier", default=None,
                               help="Frontier slug (default: the only one, if unambiguous)")
    replay_parser.add_argument("--config", default=None,
                               help="Config label for the run dir")
    replay_parser.add_argument("--brief", default=None,
                               help="Brief variant under briefs/<slug>/")
    replay_parser.add_argument("--ref", action="append", default=None,
                               help="Git committish to pin recipes + hera.analysis to "
                                    "for A/B-across-commits; repeat per side (--ref A --ref B)")
    replay_parser.add_argument("--worktree-root", default=None,
                               help="Pool dir for per-commit worktrees "
                                    "(default: $TMPDIR/hera-replay-worktrees)")
    replay_parser.add_argument("--max-parallel", type=int, default=1,
                               help="Max concurrent workers; default 1 = serial")
    replay_parser.add_argument("--model", default=None,
                               help="Model for claude -p")
    replay_parser.add_argument("--samples", type=int, default=1,
                               help="Number of independent samples per config")
    replay_parser.add_argument("--no-recipes", dest="recipes", action="store_false",
                               default=True,
                               help="Ablate recipe-corpus access")
    replay_parser.add_argument("--dry-run", action="store_true",
                               help="Build workdir + leak-check + prompt, do not invoke claude")
    replay_parser.add_argument("--timeout", type=int, default=600,
                               help="claude -p timeout (s)")
    replay_parser.add_argument("--agent", default="claude",
                               help="Agent harness (Phase 2; currently only claude)")
 
    args = parser.parse_args(argv)
    workspace = Path(args.dir)
    engine = ReplayEngine(workspace)
 
    try:
        if args.command == "init":
            engine.init()
            print(f"Initialized hera-trajectory repository under {engine.workspace_dir}")
            return 0
 
        if args.command == "status":
            if not engine.is_initialized():
                print("Error: hera-trajectory is not initialized in this directory.", file=sys.stderr)
                return 1
            print(engine.get_event_tree_str())
            return 0
 
        if args.command == "snapshot":
            if not engine.is_initialized():
                engine.init()
            snap_id = engine.snapshot()
            print(f"Created snapshot: {snap_id}")
            return 0
 
        if args.command == "log-event":
            # Attempt to parse action as JSON, fall back to string
            action_data = args.action
            try:
                action_data = json.loads(args.action)
            except json.JSONDecodeError:
                pass
 
            meta_data = None
            if args.meta:
                try:
                    meta_data = json.loads(args.meta)
                except json.JSONDecodeError:
                    print("Error: --meta must be a valid JSON string.", file=sys.stderr)
                    return 1
 
            event_id = engine.log_event(action_data, parent_id=args.parent, metadata=meta_data)
            print(f"Logged event {event_id}")
            return 0
 
        if args.command == "rollback":
            print(f"Rolling back workspace to state at {args.event_id}...")
            engine.rollback(args.event_id)
            print("Rollback complete.")
            return 0
 
        if args.command == "fork":
            dest = Path(args.dest_dir)
            print(f"Forking state at {args.event_id} into isolated workspace at {dest}...")
            engine.fork(args.event_id, dest)
            print(f"Fork complete. Isolated workspace initialized at {dest.resolve()}")
            return 0
 
        if args.command == "diff":
            changes = engine.diff_events(args.id1, args.id2)
            print(f"Changes from {args.id1} -> {args.id2}:")
            if not any(changes.values()):
                print("  No changes detected.")
                return 0
            for change_type, paths in changes.items():
                if paths:
                    print(f"  {change_type.capitalize()}:")
                    for p in paths:
                        print(f"    - {p}")
            return 0
 
        if args.command == "replay":
            if args.run_from:
                # Phase 2: trajectory-event replay (future)
                target_dest = Path(args.dest) if hasattr(args, 'dest') and args.dest else \
                    Path(tempfile.gettempdir()) / f"hera_replay_{args.run_from}_{int(datetime.now().timestamp())}"
                print(f"Starting replay from event {args.run_from} using agent '{args.agent}'")
                print(f"Forking trajectory into isolated workspace at {target_dest.resolve()}...")
                engine.fork(args.run_from, target_dest)
                print(f"Isolated workspace ready. (Multi-turn agent execution — Phase 2, future).")
                return 0

            # Phase 1: checkpoint-based single-turn replay
            from hera.benchmark import BenchmarkRunner
            checkpoint = (args.checkpoint or Path.cwd()).resolve()
            if not checkpoint.is_dir():
                print(f"Error: checkpoint directory not found: {checkpoint}", file=sys.stderr)
                return 1
            driver_repo = Path(__file__).resolve().parents[2]
            runner = BenchmarkRunner(checkpoint, driver_repo)
            slug, fm = runner._resolve_frontier(args.frontier)
            brief_text = runner._load_brief(slug, args.brief) if args.brief else None

            if args.ref:
                wt_root = Path(args.worktree_root) if args.worktree_root else \
                    Path(tempfile.gettempdir()) / "hera-replay-worktrees"
                return runner.run_ab(
                    slug=slug, fm=fm, refs=args.ref, worktree_root=wt_root,
                    max_parallel=args.max_parallel, brief_text=brief_text,
                    recipes=args.recipes, model=args.model, samples=args.samples,
                    timeout=args.timeout,
                )
            return runner.run_single(
                slug=slug, fm=fm, config=args.config, brief_text=brief_text,
                recipes=args.recipes, model=args.model, samples=args.samples,
                timeout=args.timeout, dry_run=args.dry_run,
            )

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
