---
slug: after-sdh-spot-checks
user: qingrui
cut_index: 45
latest_fileid: 3
included:
  data: [0, 1, 2, 3]
  images: []
leak_terms:
  - "landau-fan"
  - "multimegasweep"
  - "Step 4"
  - "4.5e12"
  - "n-line"
forward_scan: "Kept region is cells 0-45 (instrument bring-up / gate-bindings / SAFETIES validators / meas-config / QSwitch / HERA session-start + kernel-bind probe / Gate-C contact liveness / Step 1a 1D CNP locator [data/0] / Step 1b 0T gate map v1 [died] + v2 [data/1] / Step 3a SdH spot check HOLE [data/2] / Step 3b SdH spot check ELECTRON [data/3]). The word 'fan' appears pre-cut only as generic future capability ('which side gives cleaner SdH for the fan', cell 44; 'pick fan contact pairs', cells 36/37) — that a fan is the next instrument is legitimately known to the operator; the answer under test is the fan's ACQUISITION DESIGN (sensitivity sizing + fast_delay), which no pre-cut cell specifies. No pre-cut cell carries the fan's recipe slug, sweep call, n-range, B-row count, or n-line construction. The first Landau-fan header '## HERA — Step 4: Landau fan' is cell 46 (stripped). Clean."
---

# Frontier — cut after the electron SdH spot check (before the Landau fan)

*Decision boundary for offline replay. The YAML frontmatter is the
`hera-replay` contract; the prose below is for humans. This is a **DESIGN**
frontier: the next instrument (a field-resolved Landau fan on the electron side
at D = 0) is not in question — both spot checks are in hand and the electron
side is the cleaner one — what is in question is **whether the agent designs
that fan to avoid the two acquisition faults the as-run fan carried**:
under-ranged fixed sensitivity (clips the low-n / high-B corner) and a shaved
fast-axis dwell (under-settles, attenuating the high-frequency SdH tones the fan
exists to read). Added 2026-06-20.*

## The frontmatter contract

- **`cut_index` (45)** — fixture-relative, 0-based, inclusive. The agent sees
  cells `0..45`; cells 46–47 (the fan) are the answer key.
- **`latest_fileid` (3)** — the **electron SdH spot check** (n = +5e12, D = 0,
  B 4→0 T at 8 mT), the freshest result; the agent is pointed here. See
  `../ground_truth/after-sdh-spot-checks/reading.md`.
- **`included.data`** — allowlist hardlinked into the workdir: 1D CNP locator
  (0), 0 T gate map (1), hole SdH spot check (2), electron SdH spot check (3,
  latest). Adding the post-cut fan (4) would be the leak.
- **`leak_terms`** — post-cut-only tripwires (all verified by pre/post grep:
  every match is at a cell index > 45).
- **`forward_scan`** — attestation that the kept cells carry no forward
  reference to the fan's design.

## Cut

- **Cut index 45** is a **section boundary**: cell 45 is the electron SdH
  spot-check sweep (`data/3`). Cell 46 is the `## HERA — Step 4: Landau fan`
  markdown header — the first cell of the next section, the move HERA must
  propose. Cell 47 is the fan sweep itself (`multimegasweep`, `data/4`).

## The decision under test (why this frontier exists)

The agent has the electron spot check: a clean two-pocket SdH (a ~8 T tone + a
~44–48 T cluster summing to F_L ≈ 52 T), low onset (~0.4 T), electron the
cleaner side. The recipe goal points at a Landau fan there. The **graded
question is the fan's acquisition design**, where the as-run fan made two
flagged-but-accepted compromises:

1. **Sensitivity.** It reused the spot-check's fixed `sr1/sr2 = 1e-5`, sized for
   the *metallic* spot-check R-scale — but a fan's worst corner is `R(n_min,
   B_max)` (low density, high field), which is far more resistive and **clips**.
   A correct design sizes the range to that worst corner (or autoranges).
2. **Fast-axis settling.** It shaved `fast_delay` to ~3·τ as an
   "amplitude-for-time" trade — but the fast axis feeds a per-column FFT, so
   under-settling **suppresses the high-frequency tones** the fan is for. A
   correct design holds the settling floor (or buys the amplitude back with
   density).

A good next-move proposal resolves both; a poor one inherits the spot-check
settings and ships the clipped, under-settled fan.

## What's live at the cut

A VTI cooldown of trilayer-graphene QC0426:

1. **Bring-up + gates** (cells 0–34) — FastBi1K5 magnet, LakeShore thermometry,
   SR830 lock-ins (`sr0` transimpedance current; `sr1`/`sr2` Rxx; `sr3` Rxy),
   DC205 top gate, Keithleys back/Si gates; validators committed; QSwitch contact
   mux; HERA session-start, kernel-bind probe, Gate-C contact liveness.
2. **CNP + (n, D) line** (cell 35 → `data/0`; gate map cell 41 → `data/1`) — the
   `n_off` / lever arms used by `gates_for(n, D)`.
3. **SdH spot checks** — hole (cell 43 → `data/2`, clipped/aliased, suggestive)
   and **electron (cell 45 → `data/3`, clean, latest)**.

State at the cut: gates parked, Si grounded, magnet ramped home to 0 T (the
electron spot check descended 4→0 T), base T ≈ 1.2 K (VTI).

## Caveats carried into the cut

- **Plotting limitation.** `data/<id>/plot.png` is the live monitor, not the
  re-formed transport read; build `Rxx(B)` from the TSV as `sr{1,2}_X /
  (sr0_X / sr0_gain)`. See `reading.md`.
- **VTI base T ≈ 1.2 K**, not millikelvin — SdH is resolvable; fragile states are
  not.
- **Degraded input (v0).** No live kernel, no operator screen, no `live_notes.md`
  — the design decision does not hinge on an unrecorded live fact.
