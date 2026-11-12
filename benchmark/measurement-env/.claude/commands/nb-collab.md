# nb-collab — append cells to a live JupyterLab notebook

Drop markdown and/or code cells into a notebook the user has open in
JupyterLab. Cells appear within ~100ms with no reload prompt; code lands
un-executed. Source at `src/tools/nb_collab.py`; installed as the
`nb-collab` console script via `uv sync`. Full reference at
`hera/nb-collab/README.md`.

## When to use

When the user has a JupyterLab tab open and you want to *suggest* a cell
they can review and run — a code snippet to try, a markdown note, or a
paired observation+code. The user keeps full control: they decide whether
to execute anything.

Don't reach for this when the user wants to read a notebook (use `nb`),
or wants a fresh `.ipynb` written to disk (write the file directly).

## Preconditions

- JupyterLab running with `--collaborative`. The measurement-env launcher
  passes this automatically; manual `jupyter lab` invocations need the flag.
- Notebook path under the running server's `root_dir`. `nb-collab`
  auto-discovers via `jupyter_server.serverapp.list_running_servers()`.
- Anyone with the notebook tab open sees your cells appear live.

## Usage

Subcommands: `append`, `edit-cell`, `execute-cell`, `delete-cell`, `wait`
(the latter four are policy-gated; see `hera/nb-collab/README.md`).

```bash
nb-collab append <notebook.ipynb> [--markdown TEXT ...] [--code TEXT ...] \
                                  [--markdown-file PATH ...] [--code-file PATH ...]
```

`--markdown`, `--code`, `--markdown-file`, and `--code-file` are all
repeatable and share one ordered list, so **cells land in CLI flag order**
— `--markdown A --code B --markdown C` produces A, B, C in the notebook,
not A, C, B.

### Prefer the file-based flags for anything with special characters

Inline `--markdown "..."` / `--code "..."` source passes through the shell.
Backticks and `$(...)` in the text get **command-substituted by bash before
nb-collab ever sees them** — a backtick-wrapped path like
`` `hera/models/aba_trilayer` `` silently vanishes (this bit the
2026-06-14 QC0426 session). The bulletproof path is to write the cell
source to a file and use `--markdown-file` / `--code-file` (append) or
`--source-file` (edit-cell); the file is read verbatim, UTF-8, with **no
shell quoting or substitution**.

```bash
# Verbatim source — survives backticks, $(...), quotes, heredoc markers.
printf '%s\n' '## HERA — note: see `hera/models/aba_trilayer`' > /tmp/cell.md
nb-collab append session.ipynb --markdown-file /tmp/cell.md
```

`-` as the inline value reads one cell from stdin (no shell substitution
either); use it for piped heredocs. Rule of thumb: if the source contains
a backtick, `$`, or quotes, use a file.

```bash
# Single markdown note.
nb-collab append session.ipynb --markdown "## Note
Resistance jumped between sweeps 3 and 4 — worth a phase check."

# Paired suggestion: prose + un-executed code.
nb-collab append session.ipynb \
  --markdown "## Suggestion — narrow on the candidate pocket
Tightening around the low-resistance region. Run if it looks right." \
  --code "sweep(k_bg.volt, 0.3, 0.7, 0.01, k_tg.volt, -0.5, -0.1, 0.01)"

# Interleaved md/code/md/code (order preserved).
nb-collab append session.ipynb \
  --markdown "### Step 1" --code "do_step(1)" \
  --markdown "### Step 2" --code "do_step(2)"
```

Every inserted cell is tagged `metadata.hera` (a dict carrying a `v` version
tag plus an `appended_at` UTC timestamp) so it can be filtered or
batch-deleted later.

`--execute` runs the last appended code cell in the same session, by the id
just created — not the stale on-disk `[-1]`. Policy-gated like `execute-cell`,
checked before any cell lands; `--timeout` (default 570s) bounds the run.

`--wait` (mutually exclusive with `--execute`) appends, then blocks until the
*operator* runs the last appended code cell — append + wait in one call, no
cell id to capture by hand. It executes nothing and is **not** policy-gated, so
it works on an `append_only` notebook. Pair with `--follow` (background it) for
a no-deadline wait; reuses the `wait` subcommand's loud TIMEOUT contract.

## Defaults and gotchas

- **Append-only.** No mid-document insertion, no edits, no deletes, no
  execution (unless `--execute` under an exec policy). Deliberate — keeps you
  advisory and leaves the human in control.
- **Not idempotent.** Re-running the same invocation appends the same
  cells again. Each call = one append set.
- **Atomic per invocation.** All flags in one call land together or none
  do (single websocket session).
- **Code cells are un-executed.** No `execution_count`, no outputs.
- **Closed-tab still works.** YDoc rooms outlive tab close for ~60s
  (`document_cleanup_delay`); cells appear when the user reopens.
- **Version skew is the silent failure.** If cells land on disk but not
  in the live tab, jupyter-collaboration is probably on the 3.x line
  against JupyterLab ≥4.5. See `hera/nb-collab/PLAN.md`.

## Don't

- Don't loop or auto-re-invoke. Each call is human-mediated.
- Don't append code with side effects without a markdown cell above
  explaining what it does and why. A bare `sweep(...)` is opaque.
- Don't try to delete or rewrite earlier cells — no API, by design.
  Existing content is the user's.
- Don't batch unrelated suggestions into one invocation. One coherent
  suggestion per call (observation + sweep, sweep + plot helper).
- Don't ask the user to "run cell 17." Let them notice the new cell and
  decide. Anything they need to know to run it safely belongs in the
  markdown above.
