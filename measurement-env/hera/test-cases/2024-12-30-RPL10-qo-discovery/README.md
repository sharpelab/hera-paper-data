# Test case: RPL_10 — quantum-oscillation discovery

Offline HERA replay fixture. Captures a contiguous block of measurements Aaron
ran on RPL_10 (rhombohedral-graphene device, SC1/SC1' superconducting domes) in
the 2024-12-30 cooldown, frozen at the moment quantum oscillations were
discovered/confirmed — and asks the agent what to measure next. **Contested
frontier**: several next experiments are legitimate.

## Source

- Notebook: `~/sharpelab/dgglab-measurements/toploader/aaron/RPL_10/241230_measure.ipynb`
- Cropped here as `241230_measure__c0-65.ipynb` — cells 0–65 (fixture indices ==
  source indices). Cells 0–54 are served (the cut); 55–65 are the
  `# Temperature dependence` opening, kept only so the answer key / ground truth
  is in the same file. The driver crops to `cut_index` (54) before serving.
- Captured: 2024-12-30 cooldown (session ran 2024-12-30 → 2025-01-07).

## Goal

See `goal.md` — Aaron's section framing: "Quantum oscillations discovery
journey."

## Frontier

One frontier, **CONTESTED**:

| slug | cut_index | latest_fileid | #data dirs | next section (answer) |
|---|---|---|---|---|
| `after-qo-discovery` | 54 | 159 | 28 (132–159) | `# Temperature dependence` |

The cut sits at the end of `# Quantum oscillations discovery journey` (header
cell 44; sub-sections `## Gate maps in field` 45 and
`## D = 0.31 V/nm up to B = 1 T` 49, running through cell 54). Cell 54 is a *raw*
(unexecuted) draft fan — the last executed sweep is cell 53 → `data/159`. The
next section the agent must reason past is `# Temperature dependence` (cell 55).

## Layout

Mirrors a real measurement directory so HERA's tactical agent can be rooted here.

- `goal.md` — Aaron's framing + offline-test preamble.
- `device_card.md` — RPL_10 device properties + this-cooldown measurement setup
  (gates incl. Si back gate, DC bias, 8×SR830 + SR860, heater, AMI430 magnet).
- `241230_measure__c0-65.ipynb` — cropped measure notebook (outputs preserved).
- `cell-to-fileid.md` — cell ↔ `data/<file_id>` map (human aid; not served).
- `data/<file_id>/` — sweep outputs (tsv(.gz) + metadata.json + plot.png).
  file_ids **132–160** (29 dirs, ~103 MB). 132–159 are the pre-cut allowlist;
  160 is the first post-cut (Temperature-dependence) sweep, kept for ground-truth
  reading only and NOT allowlisted.
- `frontiers/after-qo-discovery.md` — the cut contract (frontmatter) + prose.
- `ground_truth/after-qo-discovery/` — `next_move.md` (what Aaron did next +
  judging buckets) and `reading.md` (expert read of `data/159`).
- `briefs/after-qo-discovery/` — the brief grid (see below).

## Section structure (Aaron's headers, source indices)

| Cells | Header | Sweep family |
|---|---|---|
| 19–20 | `# Configs` | mc_4 / mc_5 |
| 21–29 | `# Taking gate maps in field` (B = ±100 mT) | field × (n,D) gatemap |
| 30–33 | multiferroism Hall check around "bubble" | Hall gatemap |
| 34–37 | `# High res gate map` | (n,D) gatemap, B = 0 |
| 38–43 | `# Perusing Idc` | DC-bias × density linecuts |
| 44–54 | `# Quantum oscillations discovery journey` | field gatemaps + n-vs-B fans @ D=0.31 |
| 55+ | `# Temperature dependence` (POST-CUT / answer) | heater × DC-bias, heater × gates |

## Briefs

`briefs/after-qo-discovery/` carries the **autonomy × length 2×2** (depth held at
*deep investigation*) plus a **depth probe** on the `directive-short` anchor:

- 2×2: `open-short`, `open-long`, `directive-short`, `directive-long`.
- depth probe: `directive-short-quick`, `directive-short` (= deep, shared
  anchor), `directive-short-paper`.

The directive briefs encode Aaron's actual next move (temperature dependence) as
the revealed strategic decision; the open briefs leave the experiment to the
agent (this is the contested-frontier test — see `hera/docs/tactical-brief.md`).

## Notes / uncertain (for review)

- **Physics labels are reviewable.** "Quantum oscillations / SdH" and the
  effective-mass / Tc interpretations follow Aaron's own section labels and the
  sweep design, but the embedded plots are raw multi-trace overlays — see
  `ground_truth/.../reading.md` limitations. Flag for expert spot-check.
- **Bias resistor unknown.** This notebook never states the DC205 series bias
  resistor / nA-per-volt conversion for RPL_10 — `device_card.md` marks it
  `[VERIFY]`. (The QO section doesn't use DC bias, so it doesn't affect the cut.)
- **Material specifics `[VERIFY]`** — exact rhombohedral layer number not in this
  notebook.

## Not yet done (per EXTRACT-BRIEF)

- `link-data.sh` has **not** been run — `data/` and the `.ipynb` are real files
  here, not yet relocated to `$HERA_DATA` / symlinked. (The b1c2 reference is
  symlinked; this fixture is left in-place pending the batch partition step.)
- No `images/` extracted — the agent reads `data/<id>/plot.png` directly.
