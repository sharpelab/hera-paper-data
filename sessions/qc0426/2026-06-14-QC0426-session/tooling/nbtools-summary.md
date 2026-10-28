# nb / nb-collab triage R3 — three notebook-tooling fixes

DRAFT branch: `subtask/triage-r3-nbtools` (based on `hera`). Not merged, not pushed.

Source friction: the 2026-06-14 QC0426/VTI live session surfaced three
notebook-tooling pain points (T-4, T-5, T-3). Fixes below, one commit per item.

## Commits

| SHA | Item | Title |
|---|---|---|
| `829b858` | T-4 | `[fix][hera] nb cells --outputs: render error tracebacks` |
| `eb0c618` | T-3 | `[fix][hera] nb-collab wait: loud timeout, distinct exit` |
| `c61a59c` | T-5 | `[docs][hera] nb-collab: steer shell-hostile source to file/stdin` |

## T-4 — `nb cells --outputs` dropped error tracebacks

**Found.** `_print_output` in `nb.py` handled `stream`, `image/png`,
`text/plain`, and a mime-list fallback, but error outputs
(`output_type == "error"`) carry no `data` key — they hold `ename`,
`evalue`, `traceback`. They fell straight through to `[error: no data]`,
dropping the whole traceback. The 2026-06-14 agent hand-parsed raw
`.ipynb` JSON 3× to recover tracebacks this swallowed.

**Changed.**
- `src/tools/nb.py:66-71` — added `_ANSI_RE` + `_strip_ansi()` helper.
- `src/tools/nb.py:208-224` — added an `otype == "error"` branch in
  `_print_output` (sits before the `data`/stream paths). Prints
  `[error] ename: evalue` plus the ANSI-stripped traceback. Defensive
  against a string-vs-list `traceback` and missing `ename`/`evalue`
  (falls back to `[error]` + trace body).

**Verified.** Functional check (`_print_output` on a real error output with
ANSI codes) renders the clean header + stripped traceback, no
`[error: no data]`.

## T-5 — backtick-wrapped slash-paths eaten by shell substitution

**Found (the real root cause).** This is NOT a bug in the shim or the CLI
arg parsing. `tools/nb-collab` is a thin bash shim (`exec uv run ... "$@"`)
— it forwards args faithfully. The breakage is one layer up: the agent
invoked `nb-collab append ... --markdown "...text with \`backticks\`..."`,
and **bash applies backtick / `$(...)` command substitution to the
double-quoted argument before nb-collab ever sees it**. A backtick-wrapped
path like `` `hera/models/aba_trilayer` `` is read by bash as "run the
command `hera/models/aba_trilayer`", which yields empty / errors and the
fragment vanishes. It's "intermittent" only because it depends on whether
the backtick content happens to be a runnable command and on shell quoting
state — other backtick paths in the same session survived by luck.

The substitution-free paths **already exist in the CLI**:
`--markdown-file`/`--code-file` on `append`, `--source-file` on
`edit-cell`, and `-` (stdin). `_resolve_cells` /
`_resolve_single_source` read files verbatim (UTF-8) before any websocket
connect. They were simply **undocumented** — the skill doc claimed "single
subcommand: append" and never mentioned the file flags — so the agent
reached for inline quoting and hit the shell.

**Changed (docs + tests; no CLI code change needed — the flags were
already correct and bulletproof).**
- `.claude/commands/nb-collab.md` — documented `--markdown-file`/`--code-file`,
  added a "prefer file-based flags for special characters" section
  explaining the shell-substitution trap with the exact lost fragment as
  the example; fixed two stale claims ("single subcommand"; the
  `metadata.hera = "v0"` string form, now the dict form).
- `hera/nb-collab/README.md` — added a "Pass shell-hostile source via a
  file (not inline)" subsection to the CLI docs; updated the `append`
  synopsis to list the file flags.
- `tests/test_nb_collab.py` — added `_SHELL_HOSTILE_SRC` fixture (backtick
  path + `$(...)` + quotes) and two regression tests proving it round-trips
  byte-for-byte through `--code-file` (`_resolve_cells`,
  `test_resolve_file_preserves_shell_hostile_chars_verbatim`) and
  `--source-file` (`_resolve_single_source`,
  `test_resolve_single_source_file_preserves_shell_hostile_chars`),
  asserting `` `hera/models/aba_trilayer` `` survives.

**Bulletproofness.** The file path never touches a shell: argparse gets a
path string, `Path.read_text(encoding="utf-8")` reads bytes verbatim, and
the content goes straight into the YDoc cell. The only failure modes are
missing-file / non-UTF-8 / permission, all of which abort with a clear
error *before* any websocket connect (already tested). Tests confirm
backticks/`$(...)`/quotes are preserved exactly.

## T-3 — `nb-collab wait` silent ~10-min timeout

**Found.** `_wait` printed `status: timeout` + `last_execution_count:` to
**stdout** and returned `EXIT_TIMEOUT` (2) — the exit code was already
distinct from success (0), but nothing on a loud channel said the cell
hadn't finished, and `status:` is a stdout line that reads like the
`status: done` of a real finish. The 2026-06-14 agent read it as
completion on a 19-min sweep that outran the default 570s timeout. (Note:
the internal default is 570s, ~9.5 min, matching the "~10-minute" report.)

**Changed.**
- `src/tools/nb_collab.py:714-728` — added `_timeout_message(cell_id,
  timeout, last_count)` helper building a plain-language line:
  `nb-collab wait: TIMED OUT after Ns — cell <id> is STILL RUNNING
  (execution_count unchanged at <n>). It did NOT finish. Re-run ... (raise
  --timeout for longer sweeps) ...`.
- `src/tools/nb_collab.py:~800` — `_wait` now also prints
  `_timeout_message(...)` to **stderr** on timeout (stdout lines kept for
  backward compat; exit code unchanged at `EXIT_TIMEOUT=2`).
- A `--timeout` flag already existed (default `DEFAULT_WAIT_TIMEOUT=570`);
  the message surfaces its value and points at raising it.
- `hera/nb-collab/README.md` — documented the loud stderr line + exit-2
  semantics in the `wait` section.
- `tests/test_nb_collab.py` — 4 tests: message is loud + names the
  running state, surfaces the timeout value (`570s`/`60s`), includes
  `last_execution_count`, and the `--timeout` flag default/override parse.

## Tests added

All under `tests/`, run with `menv python -m pytest tests/test_nb.py
tests/test_nb_collab.py` → **75 passed** (was 63).

- `tests/test_nb.py` (new, 6 tests) — T-4: ANSI strip; error output renders
  ename/evalue + traceback; no-traceback header; string-traceback;
  missing-ename fallback; stream-output-unaffected regression guard.
- `tests/test_nb_collab.py` (+6 tests) — T-5: 2 verbatim file-roundtrip
  tests; T-3: 4 timeout-message / flag tests.

## Punted / backlogged

- **No CLI code change for T-5.** The file flags were already implemented
  and correct; the only gap was discoverability (docs). I did not add a
  shell-side guard (e.g. the shim rejecting backticks) — that would be
  fragile and the file path fully solves it. If we want belt-and-suspenders
  later, the cleanest move is to have HERA agent prompts always write cell
  source to a temp file and use `--*-file`; that's a prompt change, out of
  scope here. Backlog candidate.
- **Skill-doc "Append-only" gotcha** left as-is. `edit-cell`/`execute-cell`/
  `delete-cell` exist but are policy-gated to non-default policies, so the
  default-posture framing in the skill doc is still accurate enough; a full
  rewrite of that section is a separate docs task.
- **stdin path for edit-cell/append** is documented but I did not add new
  stdin tests beyond what already existed (the existing suite covers stdin
  verbatim roundtrip).

## Net line delta

`git diff hera..HEAD --stat`: **+226 / -9 = +217 net lines** across 6 files
(2 source, 2 test, 2 docs).

## Caveats

- Could not run the global `nb`/`nb-collab` shims end-to-end in the
  worktree: they hard-point at `~/measurement_env` (the rig path), which
  doesn't exist on the dev box and recursed `uv run`. Ran everything via
  `uv run --no-sync --project . python -m tools.nb[_collab]` and pytest
  instead — equivalent code path.
- Required `git submodule update --init lib/measureme lib/measurebot` +
  `uv sync` in the worktree to get pytest/jupyter deps (submodules weren't
  checked out). Those changes are not part of any commit.
- The prompt referenced `src/hera/nb.py`; the actual modules are
  `src/tools/nb.py` and `src/tools/nb_collab.py` (shims `tools/nb`,
  `tools/nb-collab`).
