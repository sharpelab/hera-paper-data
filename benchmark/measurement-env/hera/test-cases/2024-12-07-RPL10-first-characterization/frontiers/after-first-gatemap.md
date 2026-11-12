---
slug: after-first-gatemap
user: aaron
cut_index: 54
latest_fileid: 18
included:
  data: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
  images: []
leak_terms:
  - "Changing config"
  - "quick DC"
  - "Fraunhofer"
  - "rat cleansing"
  - "back gate testing"
  - "mc_2"
  - "mc_3"
forward_scan: "kept region is cells 0-54 (init + Configs + Gate checks + the full first Gatemap section). Markdown cells: # Configs (17), # Gate checks (21) + its 3 subsections, # Gatemap (43) — all current/completed-section headers. The gate-map add_comment strings ('initial gatemap, V_si = 10/-10/20') describe the just-completed section; no forward reference to DC bias / Fraunhofer / Si-BG / hysteresis. The # Changing config to do quick DC header (55) and every later header drop with the cut. Clean."
---

# Frontier — cut at end of the first `# Gatemap` (CONTESTED → ORDERED)

*Originally filed as a **CONTESTED** frontier early in RPL_10's first cooldown.
The cut sits at the end of the first transport gate-map section. The first
(n, D) maps are done and the operator has located SC-ish regions. Added
2026-06-01.*

> **Re-graded 2026-06-09 (Aaron, expert-review card).** Aaron: *"This is not
> contested"* — there is an ordering: zero-field Ic check first (it sets the Idc
> range), then a field-range check (sets the Fraunhofer window); a finer map is
> also fine; the Si-BG survey is a quick check but a secondary concern. The
> 2×2 brief grid is retained for strategic variance, but judge against the
> **ordered** buckets in `ground_truth/after-first-gatemap/next_move.md`.

## Cut

- **Cut index 54** sits on a **section boundary**: index 54 is the last cell of
  `# Gatemap` (`k_bg.volt(0)` — parking the back gate after the ten gate-map
  sweeps). Index 55 is the `# Changing config to do quick DC` markdown header —
  the first cell of the next experiment, which is what HERA must predict.
- **No mid-section header leak.** Truncation at 54 keeps `# Gatemap` (43, the
  current section) and drops everything from 55 on.

## What's live at the cut

The campaign has, in order:
1. **Gate checks** (cells 21–42 → data/0–8): gates validated and alive (see the
   `after-gate-checks` frontier).
2. **First (n, D) gate maps** (cells 43–54 → data/9–18): ten 2D maps of (Vbg,
   Vtg) transport over the validated window at several Si-back-gate settings
   (V_Si = +10, −10, +20 V), refining the window each pass. These are the first
   transport maps of the device.

**Latest landed sweep: `data/18/`** (cell idx 53) — the last gate map of the
first section (V_Si = 20 V, Vbg ∈ [−9, 5], Vtg ∈ [−4.5, 2.5]). State at the cut:
gates parked (cell 54 → k_bg=0), working validators set, base temperature, no
field. The DC-bias source (DC205) is wired but has not been swept yet.

## Why this was filed as CONTESTED (re-graded: ordered)

With the first gate maps in hand and candidate SC-like regions located, several
paths *appeared* to compete:
- **DC bias / Ic checks** (what the operator actually did first): reconfigure to
  put a probe on the SC contact pair and sweep DC bias to look for a
  critical-current / zero-bias feature.
- **Fraunhofer / field response**: take the candidate region straight to field
  to test Josephson behaviour.
- **More / finer gate maps**: higher-resolution maps to localize features
  before committing to a fixed operating point.
- **Silicon-back-gate survey**: use V_Si as a third axis to map how the features
  move (this device has a Si back gate — see `device_card.md`).

Per Aaron (2026-06-09) the spread is **ordered, not open**: the zero-field Ic
check comes first (it sets the Idc range), then the field-range check (sets the
Fraunhofer window); the finer map is also fine; the Si survey is secondary. The
frontier still carries the full 2×2 (`open-short`, `open-long`,
`directive-short`, `directive-long`, depth held = deep) — useful for seeing
whether open-brief agents recover the ordering — and the depth-probe anchor is
*not* used here (that lives on `after-gate-checks`).

## Caveats carried into the cut

- **Plotting limitation (important).** The gate-map `plot.png` (and the embedded
  cell output) shows only the **live-followed monitor** — gate leakage currents
  (`k_tg_curr`, `k_bg_curr`) vs voltage/time — **not** a 2D transport colormap.
  The operator's `s.plot()` registered the gate currents, not the lock-in
  channels, so the actual (Vbg, Vtg) transport map is **only recoverable from
  `data/<id>/data.tsv.gz`** (which has `sr830_1..9_X/P`, `sr830_4_X` being the
  current channel), not from the rendered PNG. See
  `ground_truth/after-first-gatemap/reading.md`.
- **First cooldown, no drift.** Data is from this cooldown / this notebook — no
  device-card drift; the generic replay drift warning does not apply.
- **Degraded input (v0).** No live kernel, no operator screen observations, no
  `live_notes.md`. The choice of next experiment does not hinge on an unrecorded
  live fact — only fine operating-point numbers would, and those are
  parameter-level (per the locked principle, no live_notes for that).
