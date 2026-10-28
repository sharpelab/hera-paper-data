# nb-collab

`nb-collab` lets a Claude Code session (or any external Python process) append cells to a notebook that's open in JupyterLab — **live**, with no reload prompt and no clobbering of in-flight human edits. It's the v0 hand-off mechanism for HERA: Claude proposes a suggestion (markdown ± code), the cells appear in Aaron's open notebook, Aaron decides whether to run.

There's also a `wait` subcommand for blocking until a specific cell finishes executing, so HERA can hand off and resume in a single CC turn instead of pinging the human.

## How it works (one paragraph)

JupyterLab with the `jupyter-collaboration` extension serves notebooks through a server-side YDoc (CRDT) room. The on-disk file is downstream of the room, not the source of truth. `nb-collab append` connects to the room via the YDoc websocket protocol (using `jupyter_nbmodel_client`), inserts cells into the shared document model, and disconnects. Any browser tab open on the same notebook sees the cells appear within ~100 ms, no reload prompt. The server flushes the room to disk shortly after.

## Preconditions

- **JupyterLab running with `--collaborative`.** The measurement-env launcher does this automatically (`src/gui/toploader_launcher.py`). If you're starting JupyterLab by hand, pass `--collaborative` or live cell append silently won't surface in the browser.
- **jupyter-collaboration ≥ 4.x.** Pinned in `pyproject.toml` as `>=4.3,<5`. Older 3.x line *silently no-syncs* against JupyterLab 4.5+ — the cells land on disk via an out-of-band path but never appear live in the browser. Don't downgrade.
- **jupyter-nbmodel-client.** Pinned `>=0.14,<0.15`.
- **Notebook path under the running server's `root_dir`.** `nb-collab` auto-discovers the server via `jupyter_server.serverapp.list_running_servers()` and finds the one whose `root_dir` contains your notebook path.

## CLI

```
nb-collab append <notebook.ipynb> [--markdown TEXT ...] [--code TEXT ...] \
                                  [--markdown-file PATH ...] [--code-file PATH ...] \
                                  [--summary TEXT] [--eta DURATION] \
                                  [--execute | --wait [--follow]] [--timeout SECONDS] [--poll SECONDS] \
                                  [--server-url URL] [--token TOKEN] \
                                  [--settle SECONDS]
```

At least one `--markdown`, `--code`, `--markdown-file`, or `--code-file` required. All four flags repeat and share one ordered list, so cells land in CLI flag order regardless of type. Multiple flags in one call all land in one websocket session. `--execute` then runs the last appended code cell by the id just created (not the stale on-disk `[-1]`), policy-gated like `execute-cell`.

`--execute` and `--wait` are mutually exclusive: `--execute` runs the cell *yourself*, `--wait` appends and then blocks until the *operator* runs the last appended code cell (its `execution_count` flips non-null) — append + wait in one call, with no cell id to capture by hand. `--wait` executes nothing and is **not** policy-gated (appending is never gated and the wait is read-only), so it is the one auto-resume path available on an `append_only` notebook. It reuses the `wait` subcommand's mechanics: `--follow` lifts the deadline for a backgrounded no-deadline wait (`run_in_background` only — a foreground wait can outlive the ~600s shell cap), and a timeout is loud and distinct (`status: TIMEOUT`, a stderr line, exit 2). `--timeout` (default 570s) bounds a foreground `--execute` run or `--wait`; `--poll` (default 1.0s) is the `--wait` poll interval.

### Pass shell-hostile source via a file (not inline)

Inline `--markdown "..."`/`--code "..."` text is a shell argument: bash applies backtick and `$(...)` **command substitution to the content before nb-collab runs**, so a backtick-wrapped path (`` `hera/models/aba_trilayer` ``) or a `$(...)` fragment silently disappears or expands (this dropped a markdown path fragment in the 2026-06-14 QC0426 session). Two substitution-free paths:

- `--markdown-file PATH` / `--code-file PATH` (append) and `--source-file PATH` (edit-cell) read the cell source **verbatim from a UTF-8 file** — no quoting, no substitution. This is the bulletproof path; prefer it for any source containing a backtick, `$`, or quotes.
- `--markdown -` / `--code -` / `--source -` read from **stdin** (split on a line of `---|` for multiple `-` flags), which also escapes shell substitution if you pipe a heredoc.

File reads happen up-front, so a missing or non-UTF-8 file aborts before any websocket connect.

### Examples

```bash
# One markdown cell.
nb-collab append session.ipynb --markdown "## HERA — quick note
The phase channel is showing a complex region near (Vbg=0.4, Vtg=-0.3); worth a phase check."

# Coupled suggestion: prose + un-executed code.
nb-collab append session.ipynb \
  --markdown "## HERA suggestion — zoom on candidate pocket
Tightening around the low-resistance region from the last sweep. Run if it looks right." \
  --code "sweep(k_bg.volt, 0.3, 0.7, 0.01, k_tg.volt, -0.5, -0.1, 0.01)"

# Two markdown cells in one call (e.g., observation + decision).
nb-collab append session.ipynb \
  --markdown "## What I see..." \
  --markdown "## Suggested next step..."
```

Output on success looks like:
```
connected: http://127.0.0.1:8899 path=session.ipynb cells=12
  appended markdown @ 12 id=a3f2b1d8
  appended code @ 13 id=8c4e1f9a
done. cells now = 14
```

The `id=…` is the stable YDoc cell id — pass it to `nb-collab wait` to block on the cell.

### `--summary` / `--eta`

Optional, at most once each. When either is passed, a rendered blockquote
line lands in the **first appended markdown cell**, right after its leading
heading (or prepended if the cell has none):

```
> **14:32** · check the low-resistance pocket at (0.4, -0.3) · **ETA ~15:12** (≈40 min)
```

`14:32` is server-local append time; `~15:12` is that plus `--eta`'s
duration (`≈40 min` under an hour, `≈1h30m`/`≈2h` at or above); a day
rollover adds ` (+1d)` right after the clock, inside the bold. Each clause
drops out when its flag is absent. Summary text is markdown-escaped for
rendering (`_`/`*`/`\`), stamped raw. `--eta` accepts `40m`, `2h`, `1h30m`
— h before m, at least one required; a bare `40` is rejected (add the
suffix).

Both require at least one markdown cell among the appended cells
(`--markdown`/`--markdown-file`) — validated before any websocket connect,
alongside a no-backtick check on `--summary` and duration parsing on
`--eta`. The same cell also gets stamped
`metadata.hera.summary` (raw text) and/or `metadata.hera.eta_at` (ISO-8601
UTC instant), in addition to the `appended_at` every appended cell gets.
`--eta` additionally echoes to stdout after the `appended …` lines:
`eta: ~15:12 (≈40 min)`.

Neither flag changes anything when omitted.

```
nb-collab wait <notebook.ipynb> <cell-id> [--timeout SECONDS] [--poll SECONDS] \
                                          [--wait-for-rerun] \
                                          [--server-url URL] [--token TOKEN]
```

Default timeout is 570s (sub-CC-Bash-cap). Default poll interval is 1.0s.

**Default semantics.** Connect to the live notebook over RTC, find the cell by id, and:
- if it already has an `execution_count`, return immediately ("done").
- otherwise poll until `execution_count` becomes non-null.

**`--wait-for-rerun`.** Take whatever the cell's current `execution_count` is as a baseline (could be `null` or a number) and wait for it to *change* to a different non-null value. Use this when you want to confirm the cell ran *this turn*, not just at some point in the past.

**Exit codes**
| code | meaning |
|---|---|
| 0 | done — cell finished (success *or* uncaught error both count) |
| 1 | error — couldn't connect, notebook missing, cell id not found, etc. |
| 2 | timeout — deadline elapsed without completion |
| 3 | deleted — cell id disappeared from the notebook while polling |

**Output on stdout** (parseable line-prefixed):
```
status: done
execution_count: 7
--- output ---
hello
ok
```

For timeout: `status: timeout` + `last_execution_count: …` on stdout, **plus a loud `nb-collab wait: TIMED OUT after Ns — cell … is STILL RUNNING … did NOT finish` line on stderr**, and exit code 2. The stderr line + nonzero exit are there so a timeout can't be read as completion — the 2026-06-14 QC0426 session mistook a quiet `status: timeout` for a finished cell on a 19-min sweep that outran the default timeout. If your sweep can run longer than the default (570s), raise `--timeout`. For deletion: `status: deleted` (exit 3). For errors: `status: error` + `reason: …` (exit 1).

`execute-cell` / `append --execute` mirror this contract: if the client times out while the kernel keeps running the cell, they emit `status: TIMEOUT — kernel still running` + a loud stderr line and exit **2** (not exit 1) — the cell's `execution_count` is orphaned and won't update, so `nb-collab wait` would hang on it. Monitor completion via the data dir / hera-watch, not cell state; for long runs, background the execute with a `--timeout` above the run so the client survives to finalize the cell.

## What it does

- **Appends to the end of the notebook.** No mid-document insertion in v0.
- **Markdown and code cells.** Mixed in a single invocation if you want; cells are appended in the order their flags appear on the CLI (e.g. `--markdown A --code B --markdown C` lands as A, B, C).
- **Code cells land un-executed.** No `execution_count`, no outputs. Aaron decides what runs.
- **Tags every inserted cell with `metadata.hera`** — a dict `{"v": "v0", "appended_at": "<UTC ISO-8601>"}`. Filter or batch-delete later by the presence of the `hera` key; `appended_at` records when the cell landed (edit-cell adds `edited_at`, execute-cell adds `executed_at`). Older notebooks may still carry the legacy bare string `"v0"`; a later stamp upgrades it to the dict form in place.
- **Atomic within one invocation.** Single websocket session; either everything lands or nothing does.
- **Live in any open browser tab.** YDoc broadcasts to all connected clients; cells appear within ~100 ms with no reload prompt and no "file changed on disk" dialog.
- **Persists to disk.** YDoc room flushes shortly after via the server's normal save path.

## What it does NOT do (and why)

- **No edit existing cells.** Would risk clobbering Aaron's in-flight edits; breaks the HITL boundary.
- **No delete cells.** Same.
- **No execute cells.** Aaron runs cells. That's the v0 protocol — keeps Claude strictly advisory.
- **No mid-notebook / anchor-based insert.** v0 is end-only. Adding `--after-anchor "## Suggestions"` is plausible later but deliberately omitted now to avoid over-design.
- **Not idempotent.** Re-running the same `nb-collab append` invocation appends the cells *again*. Each call = one append set.
- **No notebook creation.** Aaron creates session notebooks; `nb-collab` only appends to existing ones.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| `no running JupyterLab server has X under its root_dir` | Launcher not running, or notebook path is outside the served tree | Start the launcher (`uv run measurement-env`) or move/symlink the notebook into the served tree |
| `notebook does not exist` | Wrong path | — |
| `not an .ipynb file` | Wrong extension | — |
| `--server-url/--token did not match any running server` | Override args don't match `list_running_servers()` | Drop the overrides and let auto-discovery work, or check `jupyter server list` |
| `failed to resolve collaboration room` | jupyter-collaboration not installed, or wrong version, or notebook path not in contents API | Verify `pyproject.toml` deps, verify `--collaborative` is on, verify path |
| Cells appear in disk but not in open tab | jupyter-collaboration is on the 3.x line, OR JupyterLab was started without `--collaborative` | Bump to ≥4.x; verify launcher flag |
| Cells appear in tab on reopen but not live | Same as above, OR browser cache is stale (try hard reload) | — |
| Append against a closed-tab notebook silently works | Expected — YDoc room survives `document_cleanup_delay` (default 60 s); cells appear when the notebook is reopened | Treat as feature; if it bothers you, reduce `--YDocExtension.document_cleanup_delay` server-side |

## Discipline for HERA agents using `nb-collab`

These are conventions for the *content* the agent puts into cells. The CLI doesn't enforce them; treat them as house rules.

- **Lead every markdown cell with a recognizable HERA prefix** (e.g. `## HERA — <title>` or `## HERA suggestion — <title>`). The `metadata.hera` dict is invisible in the rendered notebook; the prefix is what Aaron sees while scrolling.
- **Don't append code with side effects without explaining it in markdown above.** A `sweep(...)` call alone is opaque; pair it with a one-line "what this does and why" cell.
- **One coherent suggestion per invocation.** Multiple cells in one call are fine if they belong together (observation + sweep, or sweep + plot helper). Don't batch unrelated suggestions.
- **Don't loop or re-invoke without a human nudge.** Each `nb-collab append` is human-mediated. Re-running the same suggestion double-inserts.
- **The cells are un-executed by design.** Don't ask Aaron to "run cell 17"; let him notice the new cell and decide. If the cell needs explanation to be safe to run, put that explanation in markdown above.
- **You are not editing the notebook — you are *adding* to it.** Treat existing content as Aaron's. Never propose to delete or rewrite earlier cells via this tool (and there's no API to do so anyway).

## Pointers

- **Source:** `src/tools/nb_collab.py` (~165 lines). Async client wrapping `jupyter_nbmodel_client` via `asyncio.run()`.
- **Verification record:** `hera/nb-collab/PLAN.md` — the probe-by-probe verification of RTC behavior. Includes server-side YDoc broadcast confirmation, browser-tab sync gate, append + edit coexistence, closed-tab append behavior, the JupyterLab 4.5 + collab 3.x version-skew failure mode that took two hours to diagnose. Read this if `nb-collab` ever stops working.
- **Wire protocol:** Yjs websocket (CRDT) via the `jupyter-collaboration` server extension's `/api/collaboration/room/<id>` endpoint. The `jupyter_nbmodel_client` library handles the protocol; if it's ever abandoned, `pycrdt-websocket` + `jupyter_ydoc` is the lower-level fallback.
- **Launcher integration:** `src/gui/toploader_launcher.py` (around line 501) passes `--collaborative` to the JupyterLab subprocess.
- **Version pins:** `pyproject.toml` has `jupyterlab>=4.5,<4.6`, `jupyter-collaboration>=4.3,<5`, `jupyter-nbmodel-client>=0.14,<0.15`. The collab/JupyterLab pair is the surface that breaks together; if you bump one, verify the other still works (re-run PLAN.md probes).
