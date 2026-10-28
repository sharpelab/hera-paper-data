# Test case: RPL_19 — SC dome → Fraunhofer (CONTESTED frontier)

Offline HERA replay fixture. Captures the SC-dome-mapping block of Aaron's
RPL_19 2025-11-03 cooldown, frozen at the moment the dome has been mapped but not
yet interrogated, plus the campaign goal as handed to HERA at session start. The
single frontier is **CONTESTED** (the next move is a real strategic branch), so
it carries the full 2x2 autonomy×length brief grid (depth held = deep).

## Source

- Notebook: `~/sharpelab/dgglab-measurements/toploader/aaron/RPL_19/20251103_measure.ipynb`
- Captured cells: 0–84 (cropped; the served notebook is truncated to cut_index=83
  by the driver). Outputs preserved.
- Device: RPL_19 (rhombohedral graphene, SC + AH device). See `device_card.md`.

## Goal

See `goal.md` — campaign framing: "characterize the superconducting dome — map
it, then establish its nature."

## Layout

Mirrors a real measurement directory so HERA's tactical agent can be rooted here
directly (`device_card.md`, the working notebook, `data/` at top level).

- `goal.md` — campaign-altitude framing (the open baseline; briefs replace it).
- `device_card.md` — RPL_19 device + 2025-11-03 rig setup (gates, DC bias,
  lock-ins, thermometry/heater, AMI430 + Yokogawa magnets). Describes the magnet
  as *capability*; the post-cut field × bias sweep call is a leak term.
- `cell-to-fileid.md` — cell → `data/<file_id>/` map (human aid; not served).
- `20251103_measure__c0-84.ipynb` — cropped measure notebook, cells 0–84.
- `data/<file_id>/` — sweep outputs (TSV + metadata.json + plot.png). file_ids
  130–145 (16 dirs, ~19 MB).
- `frontiers/after-sc-gatemap.md` — the single frontier (cut + allowlist +
  leak_terms + forward_scan).
- `ground_truth/after-sc-gatemap/{next_move.md, reading.md}` — what Aaron did
  next (Fraunhofer) + the perception read of `data/145`.
- `briefs/after-sc-gatemap/{open-short, open-long, directive-short,
  directive-long}.md` — the 2x2 autonomy×length grid (depth = deep).

## Section structure (Aaron's headers, source indices)

| Cells | Header | Sweep family |
|---|---|---|
| 46–49 | `# Configs` | mc_* definitions |
| 50–62 | `# Gate checks` | top-gate / back-gate 1D sweeps |
| 63–83 | `# Gatemap of SC` | (Vtg,Vbg) map + gate-line cuts + small-field cuts |
| **84+** | **`# Fraunhofer`** (post-cut, the answer) | field × DC-bias maps |

## Frontier

- **`after-sc-gatemap`** — cut_index 83 (end of `# Gatemap of SC`),
  latest_fileid 145, allowlist 130–145 (16 dirs), `images: []`. Type:
  **CONTESTED**. Decision tested: "the SC dome is mapped — what experiment next?"
  Aaron went to Fraunhofer (Ic vs perpendicular field); competing legitimate
  moves: temperature dependence, oscillations, zero-effective-field gatemap. The
  brief grid probes whether autonomy/length steer the agent to Aaron's move.

## Notable: plots show leakage, not transport

Every sweep cell embeds exactly one PNG — the registered gate-leakage
live-monitor (`k_*_curr`), all ~1e−11–1e−10 A (gates healthy). The transport
signal (`sr830_*_X`) is **only in the TSVs**. So `included.images = []` and the
correct perception read requires reading TSVs, not `plot.png`. See `reading.md`.

## Leak control

`leak_terms`: `Fraunhofer`, `fraunhofer`, `megasweep(mag.field`,
`determining Ic`, `Ic at zero` — all verified post-cut-only via `nb grep`. The
magnet is real and used pre-cut (ramps, 1D `s.sweep(mag.field)`, gate-line
multimegasweeps over small fields), but the literal `megasweep(mag.field, …,
dc205_1.volt, …)` field × bias *call* is post-cut-only. `forward_scan`: clean.

## Status / for human review

- Physics in `reading.md` is defensible-but-flagged — in particular the
  **non-monotonic field dependence with a minimum ~6–8 mT** (candidate
  remanent-field offset) needs an expert spot-check; do not treat it as
  established.
- Not yet run through `hera-replay` live (dry-run leak-check only). Binaries not
  yet relocated via `link-data.sh`.
