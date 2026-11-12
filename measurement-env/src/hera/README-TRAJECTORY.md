# Hera Trajectory Engine

`hera-trajectory` is a high-fidelity CAS (Content-Addressable Storage) agent replay and trajectory branching engine. 

While `hera-replay` currently handles evaluating headless agents against static, hand-curated "cut" fixtures (offline benchmark driving), `hera-trajectory` provides the low-level state tracking and branching primitives. Eventually, `hera-trajectory` will merge with and subsume `hera-replay` so that both live session tracing and historical session playback (benchmarking) run on this unified CAS engine.

## Core Concepts

- **Source of Truth:** A causal event graph `(S) -[a]-> (S')` stored in `.replay/graph.json`. The event log is the model-agnostic source of truth; agent hooks are simply adapters that append events and trigger snapshots.
- **CAS Blob Store:** Files are securely hashed (SHA-256) and stored in `.replay/cache/`. This prevents duplication and provides instant sub-millisecond rollback fidelity.
- **Manifests:** Every snapshot generates a JSON manifest mapping workspace relative paths to their data blobs and permissions.
- **Forking:** Trajectories can be branched at any historical event ID into a fully isolated directory, complete with its own functioning `.replay` repository history for continued independent execution.

## Quickstart

```bash
# Set an alias or use the uv runner
alias hera-trajectory="uv run hera-trajectory"

# Initialize a workspace
cd my_workspace
hera-trajectory init

# Log an event
hera-trajectory log-event --action '{"type": "UserPromptSubmit", "prompt": "Initial setup"}'

# View the causal graph
hera-trajectory status

# Fork a past state into a new workspace branch
hera-trajectory fork <event_id> ../my_workspace_branch_A

# Rollback the current workspace to a past state
hera-trajectory rollback <event_id>
```

## Comparison to `hera-replay`

| Feature | `hera-replay` (Current Benchmark Driver) | `hera-trajectory` (New Unified Engine) |
|---|---|---|
| **Primary Use Case** | Offline benchmarking and A/B evaluations on static fixture cuts. | Live continuous session tracking, trajectory exploration, and (eventually) historical playback. |
| **State Capture** | Manual YAML allowlists (`frontiers/*.md`) specifying which files to keep/crop. | Automated Content-Addressable Storage (CAS) tracking all workspace files natively via `.gitignore`. |
| **History Model** | Single static "cut" state per run. | Full causal event tree (`graph.json`) tracking `Prompt -> Tool Use -> Result` transitions. |
| **Rollback & Time Travel** | Not supported. | Millisecond-accurate file state rollbacks via hash manifests. |
| **Branching** | Re-runs the same fixture in parallel `workdir` copies. | Natively forks isolated workspaces at any node in the causal tree (with full history attached). |
| **Storage** | Hardlinks/copies full files per evaluation run. | Deduplicated SHA-256 CAS blob store. |

## Running Tests

A comprehensive `pytest` suite guarantees the fidelity of the CAS engine, `.gitignore` logic, and rollbacks.
```bash
PYTHONPATH=src .venv/bin/pytest tests/hera/test_trajectory.py
```
