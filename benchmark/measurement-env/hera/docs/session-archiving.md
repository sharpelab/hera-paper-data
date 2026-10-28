# HERA / IRIS session archiving

Operationalizes the post-session snapshot of a HERA tactical or IRIS run:
mirrors the measurement-dir artifacts and pulls the Claude Code transcripts
off the rig (toploader or VTI) and into the measurement-env repo for
postmortem analysis and committing.

## When to run

After a session ends. The measurement notebook can stay open / JL can stay
running — the archive is a snapshot of disk state at the moment of the
pull. Re-running against the same date refreshes the archive in place
(the sync overwrites; deletions on the source are *not* propagated to the
archive).

## What it captures

The session dir is mirrored **wholesale** — a snapshot of disk state minus a
fixed junk-exclude list (below). There is **no per-file whitelist**: anything
an agent writes into the session dir is captured, including file classes
nobody has thought of yet. (The old whitelist silently dropped
`rig_card.md` and any new artifact class until someone remembered to add it
to the script — that footgun is gone.)

Claude Code transcripts live **outside** the session dir, so they're pulled
as a separate stream and keep their own mtime window.

## Usage

```bash
hera-archive [--end DATE] [--name NAME] <user>/<device>_toploader [YYYY-MM-DD]
```

Examples:

```bash
hera-archive Isaac/b1c2_toploader              # today, single-day session
hera-archive aaron/RPL19_toploader 2026-04-22  # specific date

# Multi-day IRIS campaign — bracket a date range, custom folder suffix.
hera-archive --end 2026-05-20 --name iris-campaign Isaac/b1c2_toploader 2026-05-13
```

Positional args: relative path under `~/measurements/` on the toploader,
then the session start date (defaults to today).

Flags:

- `--rig RIG` — `toploader` (default) or `vti`. Sets the ssh host and base
  path preset.
- `--device DEV` — device name for the archive folder. Default: session-dir
  basename minus any `_toploader` suffix.
- `--end DATE` — inclusive upper bound on the mtime window. Default
  open-ended. **The window only applies to the separately-pulled streams**
  (transcripts and `data/<run>` dirs); the main session mirror is a whole-dir
  snapshot and is *not* mtime-filtered. See the mtime note below.
- `--name NAME` — override archive folder suffix. Default `session`. Use
  e.g. `iris-campaign` to keep multi-day archives distinct from single-day
  HERA sessions.
- `--no-data` — exclude the `data/` subtree from the session mirror (e.g.
  when the titan mirror already has the sweeps).

Archive lands at:

```
<repo>/hera/docs/notes/<date>-<device>-<name>/
├── POSTMORTEM.md          # human-written, not produced by the script
├── *.ipynb                # all notebooks (measure + ana + iris_scratch)
├── rig_card.md            # the deployed rig card (now captured!)
├── device_card.md
├── hera_session.md
├── session_notes.md
├── <any new file/dir>     # whatever the agent wrote — no whitelist
├── hera_scratch/          # HERA tactical live notes + analysis stagers
├── iris/                  # state.md, notes/, scratch/ — IRIS-style sessions
├── data/
│   └── <run_id>/          # sweep runs (mtime-pruned only when --end given)
└── transcripts/
    └── *.jsonl            # Claude Code conversation logs with mtime in window
```

The session-dir contents land **at the archive root**, mirroring the rig's
layout (no `artifacts/` subfolder — the previous whitelist era nested them;
the whole-dir mirror keeps the rig's own structure). `transcripts/` is the
one synthetic subfolder, since those come from a different source path.

## What's grabbed (and what isn't)

Pulled — **the entire session dir**, minus the junk excludes. That means
every top-level `*.ipynb` (including rolling-campaign notebooks appended weeks
later — notebooks with embedded figures run 30-40 MB each), `rig_card.md`,
`device_card.md`, `hera_session.md`, `session_notes.md`, `hera_scratch/`,
`iris/`, `data/`, and **any new file or directory class an agent invents**.

Plus, as a separate mtime-windowed stream:

- **Claude transcripts** with mtime in the window, from the session's **own**
  project dir only — the tactical / iris run
  (`~/.claude/projects/C--Users-<host>-…-<user>-<session>/`). The shared
  `…-measurement-env` project (every session's `hera-session` init lands there,
  unattributable by mtime) is deliberately **not** pulled — the deployed
  brief/cards already capture the init artifacts.

Typical size: ~3-5 MB for a single-day HERA archive, ~50-100 MB for a
multi-day IRIS campaign (driven mostly by rolling notebooks + transcripts).

Junk excludes (dropped from the session mirror, matched anywhere in the tree):

- `.ipynb_checkpoints/`
- `__pycache__/`, `*.pyc`
- `.git/` (any nested repo)
- syncthing control files: `.stfolder`, `.stignore`, `.stversions`,
  `.syncthing.*`, `*.syncthing.*`, `*.tmp`
- `.transcripts/` — the transcript hook's in-session snapshot. It is the rig's
  insurance copy and always a prefix of the file step 2 pulls; `transcripts/`
  is the archive's only transcript dir. If step 2 finds nothing in the window
  the tool says so and points at the rig copies (`.transcripts/`,
  `~/.hera/transcripts/`) to pull by hand.

**Behavior change vs. the whitelist era:** a few files that used to be
explicitly skipped are now captured because they live in the session dir and
aren't junk — most notably `data/log.log` (the Lakeshore log, often
>500 KB). If that's unwanted for a given pull, exclude the data subtree with
`--no-data`, or prune it from the archive before committing. `.jupyter_ystore.db`
(collab state) is *not* excluded by name — it's usually absent by the time the
archive runs, but if present it'll come along; delete it from the archive if
so.

Not captured:

- **Prior-session notebooks under a *different* session dir** — the mirror is
  scoped to the one session dir you name. Recover others via
  `dgglab-measurements/` or scp manually.

## mtime window — what changed

The `--end DATE` window was a whitelist-era feature: the old script ran a
remote `find … -newermt` to pick which notebooks / data dirs / transcripts to
pull. A whole-dir mirror is a **snapshot** — per-file mtime filtering across an
arbitrary tree is both impractical (tar/rsync don't bracket cleanly by mtime)
and wrong for incremental files (a card or `state.md` touched once mid-campaign
would be dropped). So:

- The **session mirror is not mtime-windowed** — it's the current disk state.
- The window is preserved where it's cheap and meaningful:
  - **`data/<run>` dirs** — when `--end` is given, runs whose mtime falls
    outside the bracket are pruned from the archive after the mirror (the run
    dirs are flat and mtime-meaningful). With no `--end`, all runs are kept.
  - **Claude transcripts** — pulled with the same `find -newermt` filter as
    before (they're a separate source, untouched by this change).

## Following up

After running `hera-archive`:

1. Write the `POSTMORTEM.md` next to the artifacts. The
   `2026-05-05-b1c2-session/POSTMORTEM.md` is the reference shape: what
   worked, what broke, recipe-fix items surfaced, items added to
   `hera/docs/eng-backlog.md`, what's deferred.
2. **Run the resolution triage** (below) over the session's notes.
3. Commit. The transcripts add ~1 MB per session — committable, gives an
   evidence trail for backlog items and recipe rewrites.

## Resolution triage — the standing post-session step

Every tagged entry from the session's note streams (the agent's
`session_notes.md` RECIPE FIX / TOOLING / PROTOCOL / FEEDBACK entries
*and* the support-session log, merged into one queue) gets an explicit
disposition before the archive closes.

This step is owned by **Chiron** (`hera/chiron.md`, the post-session
triage agent — launch via `chiron --rig vti <user>/<session-dir>
[date]`; it runs `hera-archive` itself as its step 0, so the normal flow
is to launch Chiron and let it drive). Prototyped interactively
2026-06-11 on the first VTI live session (`session-notes-resolution`
subtask) — the resolution log appended to
`hera/docs/vti/2026-06-10-live-session-log.md` is the reference shape.

The full contract — dispositions, autonomy ladder (what Chiron may land
without a per-item ruling), inclusion thresholds, growth controls, and
the scoreboard — lives in `hera/docs/triage-workflow.md`. Invariants
worth restating here:

- **Human-ruled where it matters**: recipe/STYLE/prompt/tooling changes
  are presented one (or a tight cluster) at a time with a recommended
  disposition and the concrete diff; the human rules; the agent applies.
- **The resolution table is appended to the session log itself** —
  item → ruling → change/commit — so the log ends as both record and
  changelog, and note→fix latency is derivable.
- **Rig-side writes** go to an ordered maintenance-window checklist in
  the same log, never applied while the rig is in use.
- Agents may attach **proposed diffs** to RECIPE FIX entries
  in-session; triage applies, edits, or rejects — never auto-applied.
- Cross-cutting check while fixing artifacts: **operational defaults
  are also information** — scrub inherited setpoints/comments from
  templates and cards (STYLE rule 11), not just stale conclusions.

## Implementation notes

- Lives at `tools/hera-archive`, installed by `scripts/install.sh` to
  `~/.local/bin/hera-archive`. Bash wrapper around `ssh` + (`rsync` | `tar`) + `scp`.
- **Session mirror transport**: prefers `rsync` over ssh when it's present on
  *both* ends (incremental, fast re-runs). Falls back to **tar piped over ssh**
  (`ssh host 'tar -C base --exclude=… -cf - dir' | tar -x --strip-components=N`)
  when the remote lacks rsync. The tar path is the universal one: GNU tar is
  on every rig (toploader has rsync via chocolatey; **dgg-vti does not** —
  Git Bash/Msys ships no rsync, so VTI archives go through tar). Both paths
  produce byte-identical layouts with the same excludes.
- Transcripts are still pulled with `scp` (per-file, mtime-windowed).
- Uses `ssh -n` inside `while-read` loops to prevent ssh from consuming
  loop stdin (a classic gotcha that bit v0).
- Project dir matching uses suffix grep (`<user>-<session>$`) rather than
  reconstructing Claude Code's dirname-mangling rules. More robust to
  convention changes.
- `HERA_ARCHIVE_HOST` env var overrides the default `--rig` ssh host
  (e.g., for testing against a different machine).
- **Maintenance check**: validate a live-rig pull periodically — the tar path
  in particular is sensitive to remote `tar` flag support and path quoting.
  A read-only dry-run (`HERA_ARCHIVE_HOST=… --no-data` into a throwaway dir,
  or just inspect the printed layout) catches regressions.
