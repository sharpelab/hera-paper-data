---
slug: after-gate-checks
user: aaron
cut_index: 42
latest_fileid: 8
included:
  data: [0, 1, 2, 3, 4, 5, 6, 7, 8]
  images: []
leak_terms:
  - "megasweep"
  - "initial gatemap"
  - "Changing config"
  - "quick DC"
  - "Fraunhofer"
  - "mc_2"
forward_scan: "kept region is cells 0-42 (init + Configs + the full Gate-checks section). Markdown cells: # Configs (17), # Gate checks (21), ## Initial checks to see if we can even apply current (22), ## Top gate (26 nm) (26), ## Bottom Gate (40 nm) (32) — all current/completed-section headers. No add_comment strings appear before cell 43. The # Gatemap header (43) and every later header drop with the cut. Clean."
---

# Frontier — cut at end of `# Gate checks` (DEPTH / early)

*A **DEPTH-probe** frontier near the start of RPL_10's first cooldown. The cut
sits at the end of the gate-validation section, just before the first transport
gate map. The agent has gate-sweep data (so it knows roughly where the gates
respond and that the device is alive and gate-able) but **no (n, D) transport
map yet** — it must propose the first map, and the depth/rigor level should set
its resolution. Added 2026-06-01.*

## Cut

- **Cut index 42** sits on a **section boundary**: index 42 is the last cell of
  `# Gate checks` (`s.ramp(k_si.volt, 10)` — parking the Si gate after the
  bottom-gate sweeps and `s.reset()`). Index 43 is the `# Gatemap` markdown
  header — the first cell of the next experiment, which is what HERA must
  predict.
- The kept Gate-checks section is three subsections: `## Initial checks to see
  if we can even apply current` (22–25), `## Top gate (26 nm)` (26–31), and
  `## Bottom Gate (40 nm)` (32–42).

## What's live at the cut

The campaign has, in order:
1. **Initial current checks** (cells 22–25 → data/0, 1, 2): short 0→1 V sweeps
   of `k_tg` and `k_bg` and a 0→10 V sweep of `k_si`, just to confirm current
   can be applied without runaway leakage.
2. **Top-gate check** (cells 26–31 → data/3, 4, 5): `k_tg` swept 0→±13 V (top
   gate, 26 nm hBN) to find the leakage / breakdown onset; validator opened to
   ±13 V for the probe.
3. **Bottom-gate check** (cells 32–42 → data/6, 7, 8): `k_bg` swept 0→±20 V
   (back gate, 40 nm hBN); validator opened to ±20 V.

**Latest landed sweep: `data/8/`** (cell idx 37) — the `k_bg` 0→−20 V check.
State at the cut: validators set to the working window (`k_tg ∈ (−5.5, 2.5)`,
`k_bg ∈ (−9, 5)`, `k_si ∈ (−50, 50)`, see `device_card.md`), gates ramped to a
starting point (cells 40–42 ramp k_bg→5, k_tg→3, k_si→10), base temperature,
no field. **Not a cold start** — the agent has the gate-sweep data and the
established validator window, but no transport gate map.

## Why this is a DEPTH frontier

The next move (`# Gatemap`) is essentially *fixed* — after gate checks, the
obvious next experiment is the first (n, D) transport map over the validated
window. The interesting variable is **how thoroughly** to map it: a coarse recon
grid (quick) just to see if the device conducts and where the CNP / features
sit, vs a feature-resolving map (deep), vs a publication-grade map (paper). The
briefs (`briefs/after-gate-checks/`) are the depth probe `quick` / `deep` /
`paper` on that single directive anchor. This tests how the depth level sets a
*first map's* resolution (point counts, settle delay, V_Si coverage, passes).

## Caveats carried into the cut

- **Plotting limitation (real).** The gate-check sweeps' `plot.png` shows the
  live-followed parameters: gate **leakage currents** (`k_*_curr`) and the
  lock-in `X` channels vs the swept gate voltage. They confirm the gates don't
  leak and that the device responds, but they are 1D liveness checks, not a
  transport map. See `ground_truth/after-gate-checks/reading.md`.
- **First cooldown, no drift.** Unlike the b1c2 fixture, the data here is from
  *this* cooldown / this notebook — no device-card drift. The generic replay
  preamble's drift warning does not apply; the card and data match.
