# hera-archive — whitelist → whole-dir mirror (T-6 fix)

**Branch:** `subtask/triage-r3-archive` (off `hera`)
**Triage round:** R3 / 2026-06-14 QC0426-VTI session
**Status:** DRAFT — committed to branch only; not merged, not pushed.

## The footgun (T-6)

`tools/hera-archive` did not mirror the run dir. It scp'd an **enumerated
whitelist**: top-level `*.ipynb`, a hardcoded doc list, `hera_scratch/`,
`iris/`, `data/<run>`, transcripts. Two failure modes:

1. The doc list (`device_card.md` / `hera_session.md` / `session_notes.md`)
   **missed `rig_card.md`** — the deployed rig card never archived. Confirmed
   against the live rig: `dgg-vti:VTI_local_data/zack/20260614-QC0426/rig_card.md`
   exists (11,706 bytes) but the old whitelist had no clause for it.
2. Every new file class an agent invents (a new scratch dir, a new `.md`,
   a stager subfolder) was **silently dropped** until someone remembered to
   patch the script.

## What changed

Rewrote the artifact pull from an enumerated whitelist to a **whole-dir
mirror** of the session dir, minus a fixed junk-exclude list. Transcripts
(which live *outside* the session dir) keep their separate, mtime-windowed
pull.

### `tools/hera-archive` (+97 / −70; 183 → 210 lines)

- **Removed** steps 1–5 of the old whitelist (notebooks-by-mtime, the
  hardcoded metadata `for` loop, `hera_scratch/`, `iris/`, `data/<run>`-by-mtime
  — old lines ~92–153).
- **Added** the session-dir mirror (new `tools/hera-archive:118–164`):
  - **rsync path** (`:139–146`): used when rsync is present on *both* ends
    (`command -v rsync` local **and** `ssh host command -v rsync`). Trailing
    slash on source mirrors dir *contents* into the archive root.
    `--delete-excluded` + per-exclude `--exclude=`.
  - **tar-over-ssh fallback** (`:147–157`): `ssh host "tar -C base <excludes>
    -cf - dir" | tar -x --strip-components=N -C archive -f -`, where
    `N = depth of the session-dir path`. Universal — GNU tar is on every rig.
  - Pre-flight existence check (`:124–127`) errors clearly if the session dir
    is absent.
- **Exclude list** (`tools/hera-archive:84–95`), matched anywhere in the tree:
  `.ipynb_checkpoints`, `__pycache__`, `*.pyc`, `.git`, and the syncthing
  control set (`.stfolder`, `.stignore`, `.stversions`, `.syncthing.*`,
  `*.syncthing.*`, `*.tmp`).
- **`--no-data`** (`:96`): now appends `data` to the exclude list, so the
  whole-dir sync skips the data subtree (was: skipped the separate data pull).
- **`data/<run>` mtime pruning** (`:166–187`): when `--end` is given, run dirs
  whose mtime falls outside the window are pruned from the archive *after* the
  mirror. With no `--end`, all runs are kept.
- **Transcripts** (`:189–217`): logic unchanged — separate source path
  (`.claude/projects/`), still `find -newermt` mtime-windowed, still scp'd,
  still uses `ssh -n` in the while-read loops. Suffix-grep project matching
  intact.
- `--rig` presets unchanged (`vti` → `dgg-vti`/`VTI_local_data`,
  `toploader` → `toploader`/`measurements`); `HERA_ARCHIVE_HOST` override
  intact.
- **Layout change**: session-dir contents now land at the **archive root**
  (mirroring the rig), not under `artifacts/`. `transcripts/` is the one
  synthetic subfolder (different source). The `mkdir -p` no longer
  pre-creates `artifacts/` or `data/`.
- Help text (`--help` sed range `2,42p`) rewritten to describe the new model.

### `hera/docs/session-archiving.md` (+105 / −44)

- New **"What it captures"** section: whole-dir mirror, no whitelist, calls
  out that `rig_card.md` and arbitrary new files now archive.
- Rewrote the archive-layout block (root-level files, not `artifacts/`),
  the "What's grabbed" list, the exclude list, and the flags reference
  (`--rig`, `--device`, `--no-data` now documented).
- New **"mtime window — what changed"** section documenting the snapshot
  semantics (see decision below).
- Implementation notes: rsync-vs-tar transport, the dgg-vti-has-no-rsync fact,
  and a maintenance-check reminder for live-rig dry-runs.
- Behavior-change callout: `data/log.log` (Lakeshore log, >500 KB) is now
  captured (it's in the session dir and isn't junk) — use `--no-data` or
  prune if unwanted. `.jupyter_ystore.db` isn't name-excluded; delete from the
  archive if it shows up.

## Decisions & trade-offs

### mtime window (`--end`)

A whole-dir mirror is a **snapshot**; per-file mtime filtering across an
arbitrary tree is both impractical (tar/rsync don't bracket cleanly by mtime)
and *wrong* for incremental files (a card or `iris/state.md` touched once
mid-campaign would be dropped). Decision:

- The **session mirror is no longer mtime-windowed** — it's current disk state.
- The window is **preserved where it's cheap and meaningful**:
  - `data/<run>` dirs — flat and mtime-meaningful; pruned post-mirror when
    `--end` is set.
  - Claude transcripts — separate source, kept the original `find -newermt`
    filter untouched.

This is the behavior change the prompt anticipated; documented in
session-archiving.md under "mtime window — what changed".

### rsync vs. scp/tar fallback

The rig is Windows/Git Bash. **rsync availability is rig-dependent**:
`toploader` has it (chocolatey); **`dgg-vti` does not** (Git Bash/Msys ships
none). So a single rsync-only path would break VTI archives. Chosen design:
prefer rsync when present on both ends (fast incremental re-runs), else
**tar piped over ssh** — GNU tar 1.35 confirmed present on dgg-vti and
toploader. Both transports produce byte-identical layouts with the same
excludes. (`scp -r` was rejected: it can't apply excludes, so junk would
leak in.)

## Validation

All read-only against the rig; nothing written to dgg-vti, nothing written
into the repo archive dir during testing.

- **`bash -n`**: clean.
- **shellcheck 0.10.0**: clean, zero warnings. (shellcheck wasn't installed;
  fetched the static binary to `/tmp` for the check.)
- **`--help`**: renders the full updated header (exit 0).
- **Local mock-dir test**: built a mock session tree with `rig_card.md`, an
  arbitrary `some_new_artifact_class.md`, `iris/`, `hera_scratch/`, `data/`,
  plus junk (`.ipynb_checkpoints/`, `__pycache__/`, `*.pyc`, `.git/`,
  `.stfolder`, `*.tmp`). Verified **both** the tar pipeline and the rsync
  pipeline produce identical layouts: `rig_card.md` + the new file captured,
  junk excluded, `--no-data` correctly drops the `data/` subtree.
- **Live-rig dry-run (tar fallback) against `dgg-vti`**: ran the tar-over-ssh
  pipeline against the real `VTI_local_data/zack/20260614-QC0426/` session into
  a throwaway `/tmp` dir (data excluded for speed). Result: `rig_card.md`
  archived (11,706 bytes — the exact file the old whitelist dropped), full
  `hera_scratch/` (all `.py`/`.png` stagers), both notebooks, all three
  metadata files; `.ipynb_checkpoints/` correctly excluded. Pipeline exit 0
  under `set -o pipefail`.
- **Transcript project-dir match** confirmed on dgg-vti: both
  `C--Users-DGG-VTI-local-data-zack-20260614-QC0426` and
  `C--Users-DGG-measurement-env` match the suffix grep.

### Untested

- **The rsync transport against a real rig** — dgg-vti has no rsync, so the
  live test exercised only the tar fallback. The rsync path was validated
  locally (host-to-host, no ssh) only. A toploader dry-run would exercise
  rsync end-to-end; recommend adding that to the maintenance checklist.
- **No full end-to-end script run** against a rig (would write into the repo
  archive dir). Validation was of the transport pipeline in isolation plus
  static checks.

## Net line delta

| File | + | − |
|---|---|---|
| `tools/hera-archive` | 97 | 70 |
| `hera/docs/session-archiving.md` | 105 | 44 |
| **total** | **202** | **114** |

(+88 net before this summary file.)
