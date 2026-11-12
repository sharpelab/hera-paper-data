# Cutting a frontier at a completed sweep

How a replay cut is placed and masked when the decision under test follows a
sweep that ran for a long time. Written from the `vti02-fan-design` cut
(2026-09-22). Not agent-visible.

## The state we want

"The launched sweep is complete and the agent has done nothing since launching
it." That is the state a design decision should be judged from: the data are on
disk, nothing is read, nothing is drafted, nothing is planned.

The transcript has no entry for it. A live agent fills a long sweep with work:
interim reads of the run in flight, reads of the previous run landing in the
analysis notebook, notes appended, the next cell drafted, wake-up polls. Every
transcript entry between the launch and the completion carries some of that
work, and the completion result itself carries all of it.

## The manual primitive

1. **Cut on the completion result**: the `tool_result` whose text ends the
   sweep (`done: B = …`). `derive` then keeps the run and the cell's outputs.
2. **Enumerate the window**: every tool call between the launch call
   (`nb-collab execute-cell …`) and the cut. A script over the transcript
   lines that prints `line, timestamp, tool, file_path | command` is enough.
3. **Map each op to a mask entry.** A file created in the window: `drop`. A
   notebook cell appended in the window: `drop` as `<nb>#<cell id>`. An append
   to an existing file (session notes): an `edits` entry removing the appended
   text. An edit to a file that survives: an `edits` entry reverting it, or
   drop the file if it goes anyway.
4. **Rule on what predates the launch** but was made while the *previous*
   sweep ran: drafts of the next cell, read scripts, interim plots of the
   previous run. These are on disk at launch and the window enumeration does
   not find them. Each needs its own drop or keep.
5. **Assert the inventory.** The state test lists every `hera_scratch/` file
   at the cut by name, the last cell of each notebook, and the tail of the
   notes. A file that rides along with the archive fails the test instead of
   leaking into an arm.

## Gotchas

- **Background interim reads produce PNGs.** A text grep over the state cannot
  see a plot of the run in flight. `spot_run7.png` was made by a background
  read at 5 T, an hour before the cut, and passed a phrase-based test.
- **Notes get appended mid-sweep.** `session_notes.md` is reconstructed to the
  cut faithfully, which includes bullets the agent wrote while waiting. Two
  of them at the vti02 cut restated a read of the previous run.
- **Drafts made during the previous sweep are already on disk at launch.** The
  fan cell was first written from an interim read of run 6, ninety minutes
  before the hole sweep started.
- **The mask's edit sites are exact.** A `from`/`to` span keeps the `to`
  token; use `old` with the full text to remove a tail.

## Worked example: vti02-fan-design, 08-22

Launch 10:35:00Z (line 844), completion 12:11:33Z (line 1037, cut). The
window:

| Time | Op | Mask |
|---|---|---|
| 10:36 | electron read landed in ana (cells `a1d41a69`, `c056c015`); `ana_spot6.py` edited | cell drops; file drop |
| 10:35–10:36 | run-6 read re-run, `spot_run6.png` remade | file drop |
| 10:39 | two bullets appended to `session_notes.md` | `edits` removing them |
| 10:39–10:40 | `cell_fan.py` edited twice, `fan_read.py` written | file drops |
| 10:51–11:27 | run-7 interim read, `spot_run7.png` | file drop (with `spot_fft.py`) |
| 10:51 | LK arithmetic in a heredoc | ephemeral, nothing on disk |

Predating the launch and ruled dropped: `cell_fan.py` (09:08), `spot_fft.py`
(08:45), `ana_spot6.py` (10:08), `spot_run6.png` (08:56). Kept: the spot-check
cells, their scratch copies and `md_spot_h.md`, with the recipe's field-step
rule edited out at thirteen sites.

## When to build the tool

A `launch` cut in `derive` would do steps 1–3 by construction: cut file ops
and cells at the launch call, keep the launched cell's archived outputs
although its `executed_at` stamp is at completion, keep the run it started,
start the clock at the run's `end_time`. Step 4 stays a ruling. The next cut
of this kind is the point to build it.
