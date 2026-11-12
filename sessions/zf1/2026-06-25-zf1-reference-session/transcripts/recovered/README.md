# Recovered session artifacts (transcript was lost)

The HERA driving transcript of the reference session (`6cdb1c49-165b-4f0e-8985-c65d9b5e9397`,
cwd `~/measurements/aaron/20260625-zf1`, Claude Code 2.1.191) was not kept: the
rig's `~/.claude/projects/` holds no directory for that cwd, and the session's own
`hera-archive` failed (it cannot ssh to itself), which is why the directory was never
captured. The conversation records are the terminal export
`../6cdb1c49-reference-export.txt` (4,875 lines, the scrollback saved by hand after
`/export`, 23 operator prompts) and the reconstructed log `../../session_transcript.md`.

What survives on the rig (`toploader`) was copied here read-only:

- **`claude-project-entry.json`** — the harness's per-project record from
  `~/.claude.json`: session id, model `claude-opus-4-8[1m]`, token totals,
  harness cost $316.02, window open 99.3 h (the window stayed open until the
  archive attempt at 22:51Z on 2026-06-29), graceful shutdown.

The rig has no background-task directory for this session. Not here: the
agent's reasoning and tool traffic as jsonl, and per-response token usage. The
notebooks, 14 data runs, `hera_scratch/`, the cards, the brief and
`session_notes.md` are intact in the parent archive.
