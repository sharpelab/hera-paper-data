# HERA session — b1c2 / Isaac / OFFLINE-TEST

*Constructed 2026-05-06 from cells 243–299 of Isaac's
`20260415_measure.ipynb` for offline HERA evaluation. NOT a live session;
no sweeps will run, no cells will be executed. The agent is being asked
to look at a frozen, complete campaign and reason about it.*

## Device card
See `./device_card.md` (in this fixture directory). Snapshotted from
`toploader:~/measurements/Isaac/b1c2_toploader/device_card.md` on
2026-05-06; the `## Validators` block was established during the prior
day's device-init session.

**Note on cooldown drift:** the device card describes the *current* cooldown
(post-2026-05-04 thermal cycle). The data in `./data/75–90/` is from the
*prior* cooldown (2026-04-23 → 2026-04-25). Treat this as "we have a
device card for the current state of the chip + data from a prior thermal
state of the same chip" — analogous to revisiting old data with a fresh
device summary.

## Session context
- **User running this session**: isaac
- **Notebook**: `./20260415_measure__c243-299.ipynb` *(cells 243–299 from
  the source `20260415_measure.ipynb`; outputs preserved)*
- **Cooldown**: source data from cooldown that began ~2026-04-15 (notebook
  date). Device-card state is from a subsequent cooldown started ~2026-05-04.
- **Days into cooldown** (data side): 8–10 days into the source cooldown
  when these cells ran.
- **Session #**: not meaningful for offline analysis.
- **Recent interventions**: none — this is post-hoc analysis.

## Campaign goal — this session
**"These cells in the measurement script are to characterize the
superconducting state."** — Isaac, expert framing, 2026-05-06.

The campaign moves through four sub-questions in order:
1. `# nT map at Beff = 0` (cells 243–262) — how does the (n, D) phase
   diagram evolve with temperature, at zero field?
2. `# Idc vs T` (cells 263–271) — DC bias response across temperature.
3. `# Idc vs n` (cells 272–275) — DC bias × carrier density at fixed
   temperature.
4. `# B vs Idc` (cells 276–283) — field × bias to map a candidate SC
   feature.
5. `# find 90 degrees theta` (cells 284–299) — calibration tail
   (likely separate from the SC characterization goal proper).

## Notes / scratch
- This is **offline-test mode**. The agent should not propose `nb-collab
  append` cells (no live notebook to append to). Instead, the expected
  output is **analysis** — what does the data say, did it answer Isaac's
  question, what's missing, what would you do next.
- All data dirs referenced by these cells are present in `./data/<id>/`.
  See `./cell-to-fileid.md` for the cell ↔ file_id mapping.
- All rendered plot images (PNGs from cell outputs) are in `./images/`,
  named by source-cell index. These are the natural inputs for
  `hera-classify` (where the modality matches — see `./README.md`).
- `hera-classify` is on PATH if the toploader's `~/hera_smoketest/` venv
  is active, or via `uv run hera-classify` from `~/measurement_env`.
  Either way, the expected scope is **only cells 254 / 255 / 260 / 261 /
  274** (true gate maps); other modalities are out of scope and the
  classifier should refuse them.
