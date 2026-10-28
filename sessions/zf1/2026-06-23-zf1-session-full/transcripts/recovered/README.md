# Recovered session artifacts (transcript was lost)

The HERA driving transcript for this session was **lost** — the conversation
JSONL and its `~/.claude/projects/<cwd>/` directory on the toploader were
deleted *after* a clean shutdown (`.claude.json` recorded
`lastGracefulShutdown: true`, `lastCost $76.75`, ~20 h open,
`lastSessionId 6327fc0f-1a59-4102-8a62-fa1677f8b34a`, version 2.1.187). The
deletion was targeted at that one project dir — sibling sessions and all other
artifacts of this session survived. Not a Ctrl-C / crash artifact.

These survivors were recovered from the rig (`toploader`) before they age out:

- **`file-history/`** — 27 edit snapshots (`<hash>@v2`): the actual content of
  every file HERA wrote/edited during the session (reextraction + plot scripts,
  etc.). From `~/.claude/file-history/<session>/`.
- **`tasks/`** — 33 background-command outputs (`<id>.output`): live telemetry
  from `run_in_background` jobs — gatemap progress with channels/gains/bias/ETAs,
  settle ladders, T sweeps. From
  `…/AppData/Local/Temp/claude/<cwd>/<session>/tasks/`.

- **`claude-project-entry.json`** — the harness's per-project record from
  `~/.claude.json` on the rig, copied 2026-10-26: session `6327fc0f`, model
  `claude-opus-4-8[1m]`, Claude Code 2.1.187, token totals (in 22,466 / out
  456,851 / cache write 1,994,463 / cache read 90,541,209), harness cost
  $76.75, window open 20.02 h, graceful shutdown.
- **`rig-file-times.tsv`** — creation and last-write times of the session's
  temp directory on the rig (the `tasks/` outputs above, with their times):
  scratchpad created 22:17:55Z on 2026-06-23 (the `newclaude` launch), last
  task output 07:21:31Z and tasks directory 07:24:29Z on 2026-06-24, matching
  the notebook's last HERA cell stamp (07:24:29Z).

What's **not** here: HERA's reasoning narrative and the operator dialog — that
lived only in the deleted JSONL. The science itself (notebook, 41 data runs,
`hera_scratch/`) is intact in the parent archive dir.
