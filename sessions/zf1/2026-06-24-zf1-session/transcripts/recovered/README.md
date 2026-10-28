# Recovered session artifacts (transcript was lost)

The HERA driving transcript of this session (`9ceaffa3-25ed-42b6-a395-3ef979018bb2`,
cwd `~/measurements/aaron/20260624-3-zf1`, Claude Code 2.1.191) was not kept: the
rig's `~/.claude/projects/` holds no directory for that cwd. The only
conversation record is the terminal export `../9ceaffa3-marathon-export.md`
(the session's own `/export` failed with EEXIST; the file is the terminal
scrollback saved by hand). The jsonl in `../` is the `hera-session` setup
agent's (`3ca2a7a0`, cwd `~/measurement_env`), not the measurement agent's.

What survives on the rig (`toploader`) was copied here read-only:

- **`claude-project-entry.json`** — the harness's per-project record from
  `~/.claude.json`: session id, model `claude-opus-4-8[1m]`, token totals,
  harness cost $30.74, window open 6.47 h, graceful shutdown.
- **`tasks/`** — 23 background-command outputs (`<id>.output`) from
  `%LOCALAPPDATA%\Temp\claude\<cwd>\<session>\tasks\`: hera-watch follows and
  sweep progress of runs 0–13. `bo5l3u6u6.output` is a hera-watch follow whose
  websocket died when the rig went down on 2026-08-02; its content is from the
  session.
- **`rig-file-times.tsv`** — creation and last-write times of that temp
  directory. The session scratchpad was created at 22:50:42Z on 2026-06-24
  (the `newclaude` launch), the last task output was written at 03:23:56Z on
  2026-06-25 and the tasks directory at 03:24:43Z, which brackets the session
  together with the notebook's cell stamps (last HERA cell 03:24:08Z).

Not here: the agent's reasoning and tool traffic as jsonl, and per-response
token usage. The notebook, 14 data runs and `hera_scratch/` are intact in the
parent archive.
