---
slug: early-characterization
user: isaac
cut_index: 10
latest_fileid: null
included:
  data: []
  images: []
leak_terms:
  - "multisweep"
  - "multimegasweep"
  - "mag.field"
  - "B vs Idc"
  - "Idc vs T"
  - "Idc vs n"
  - "theta"
forward_scan: "kept region is cells 0-10 (setup only: heater instantiation, meas_config, station, gate ramps, validators, reset). No sweeps have run. The one forward-looking item is the index-0 markdown header `# nT map at Beff = 0`, which announces the operator's section intent — acceptable here because the briefs for this frontier are DIRECTIVE (they specify an initial (n,D) gate map), so the header is consistent context, not a hidden answer. Would leak for an OPEN early brief at this cut; use a later/redacted cut for that."
---

# Frontier — cold start (early characterization)

*A **cold-start** frontier: cut at index 10, after session setup but before the
first sweep lands. The agent has the device card + the setup cells and **no
measured data** — it must propose the *first* measurement. Added 2026-06-01 to
demonstrate the depth axis (quick vs deep) on an early-characterization brief.*

## Cut

- **Cut index 10** — the last setup cell (`s.reset()`); cell 11 (the first
  `s.multisweep([k_tg, k_bg], …)` baseline gate map → data/75) and everything
  after are the answer key. `multisweep` is a leak term precisely because the
  very next cell is the experiment a good agent should propose.
- `included` is **empty** — no sweeps have landed at this cut, so nothing from
  `data/` or `images/` is served. `latest_fileid: null` puts the driver in
  cold-start mode (no "read the latest sweep" — section 1 becomes "starting
  point").

## What's live at the cut

Session setup for a freshly-cooled, gate-validated device: heater instantiated,
`meas_config` built, `AsyncStation` up, gate vectors ramped, validators set
(`k_tg ∈ (-7,6)`, `k_bg ∈ (-4,4.4)`), bias parked. Base temperature, Beff = 0.
No transport measured yet. `device_card.md` carries the device + rig setup.

## Purpose / briefs

This frontier exists to show what the **depth/rigor** level nets out to in actual
execution, holding the experiment fixed. The briefs (`briefs/early-characterization/`)
are directive — *do an initial (n,D) gate map* — at two depths:
- `quick` — fastest coarse map to see if the device behaves and roughly where.
- `deep` — a map you can read the phase structure off.

Expert reference (post-cut, for judging): the operator's actual first move was a
baseline (Vtg,Vbg) `multisweep` gate map (cell 11 → data/75), followed by the nT
heater sweep (cell 12). See `ground_truth/early-characterization/`.
