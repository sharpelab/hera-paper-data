---
slug: after-D0-fan
user: qingrui
cut_index: 102
latest_fileid: 27
included:
  data: [24, 26, 27]
  images: []
leak_terms:
  - "TG-Si"
  - "Si gate"
  - "Si=+60"
  - "VSi"
forward_scan: "Kept region is cells 0-102 (Connect Instruments / gate-range selection / four-corner checks / 0T TG-BG map / finite-field gate map / B-n Landau fan at D=0). Grepped kept markdown + comments for forward references (next, later, TODO, will, then, screen, Si gate, TG-Si, displacement, D-series, VSi): the only D-family hit is 'D=0' inside run 27's own measurement_config comment (cell 101) — the served fan's own label, not a forward reference. No kept markdown header announces the Si gate; the last kept header is '# B-n sweep at D = 0' (cell 96) with its CNP-line note '## n=0 roughly corresponds to Vtg = -1.3*Vbg + 0.06' (cell 97). The first Si-gate header '# try Si gate -- TG-Si sweep' is cell 103 (stripped). The Si Keithley `k_2410` is instantiated / validated / zeroed in the pre-cut instrument-setup + range-finding cells (17,18,28,31,34,35,53,60,65,67,72,76,77) but is never driven to a screening voltage and never swept pre-cut — prior capability, not an answer signature. Clean."
---

# Frontier — cut at end of `# B-n sweep at D = 0` (before the Si gate is introduced)

*Defines the decision boundary at which this fixture freezes the campaign for
offline replay. The YAML frontmatter above is the machine-readable contract the
`hera-replay` driver reads; the prose below is for humans. This is a **DECISION**
frontier, and the **most contested fork in the campaign**: the first Landau fan
at the charge-neutral D = 0 line is in hand, and the operator must decide what
control to add next. The campaign goal ("get the fan working, then sweep it
across D") points naively at **starting the D-series now**; what Qingrui actually
did was **detour to bring up the Si back gate first** (a TG-Si map, then a
Si-screened fan, then Si-dependence maps) before committing to the long D-series.
Two strong experts genuinely split here — which is exactly why this frontier is
worth carrying. It is the second of the three frontiers this campaign carries
(the earlier `after-0T-gatemap` → first fan, and the later `after-density-cut` →
sweep the D-series, are filed separately). Added 2026-06-09.*

## The frontmatter contract

- **`cut_index` (102)** — fixture-relative, 0-based, inclusive. The agent sees
  cells `0..102`; everything after is the answer key. (Fixture indices == source
  indices, since the stored notebook was cropped from 0.)
- **`latest_fileid` (27)** — the **D = 0 Landau fan to 8 T**
  (`multimegasweep([magnet.mag],[linspace(0,8,401)],[dc205_volt,k_bg.volt],…)`,
  cell 102), the freshest result; the agent is pointed here as "the most recent
  result." See `../ground_truth/after-D0-fan/reading.md`.
- **`included.data`** — the **allowlist** of pre-cut data dirs the driver
  hardlinks into the working copy: the 0 T TG-BG gate map (24), the finite-field
  (B = 3 T) gate map (26), and the D = 0 Landau fan (27). Authoritative; adding
  the post-cut Si-gate runs (28/30/31/32/33) would be the leak.
- **`leak_terms`** — post-cut-only tripwires (see below).
- **`forward_scan`** — human attestation that the kept markdown/comments carry no
  forward references to the Si-gate decision.

## Cut

- **Cut index 102** sits on a **section boundary**: cell 102 is the last cell of
  the `# B-n sweep at D = 0` block — the `s.multimegasweep(...)` that produces the
  D = 0 fan (`data/27`, to 8 T). Cell 103 is the `# try Si gate -- TG-Si sweep`
  markdown header — the first cell of the next section (the Si-gate introduction),
  which is what HERA must predict.
- **No mid-section header leak.** Truncating at 102 keeps every legitimate prior
  header (through `# B-n sweep at D = 0`, cell 96, and its CNP-line note, cell 97)
  and drops the Si-gate headers (`# try Si gate -- TG-Si sweep`, cell 103;
  `# B-n sweep at D=0, Si=+60V`, cell 111) and everything after.

## Leak terms (all verified post-cut-only)

Verified with a pre/post grep over the notebook; every match is at a cell index
> 102:

- **`TG-Si`** — the Si-gate header `# try Si gate -- TG-Si sweep` (cell 103). The
  literal name of the move being predicted.
- **`Si gate`** — the same header (103) and the later 6 T-block header (116),
  both post-cut.
- **`Si=+60`** — the Si-screened-fan signature (`# B-n sweep at D=0, Si=+60V` and
  its config, cells 111/113); the `+60 V` screening set-point is unique to the
  post-cut Si section.
- **`VSi`** — the VSi-n Si-dependence maps (cells 120, 141 → `data/32`, `data/33`),
  post-cut only.

Note on **`k_2410`** (the Si Keithley): deliberately **not** a leak term. The
instrument is instantiated, range-validated, and zeroed in the pre-cut
instrument-setup and gate-range-finding cells, so its *name* is pre-cut capability.
The answer signature is the *act* of using the Si gate (driving it to a screening
voltage, sweeping TG-Si / VSi-n) — captured by the four terms above — not the
Keithley handle.

## What's live at the cut

A VTI cooldown of trilayer-graphene QC0426, characterized at 0 T and now with its
first field-resolved fan:

1. **Instruments + gate ranges** (cells 0-80) — AMI430 magnet, LakeShore
   thermometry, SR830 lock-ins, the **DC205 driving the top gate** (`DC_bias`) and
   Keithleys driving the back (`k_bg`) and Si (`k_2410`) gates; safe ranges chosen
   (`k_tg ∈ [−6.5, 7.5]`, `k_bg ∈ [−5, 4.8]`). The Si gate is wired and zeroed but
   not yet used as a control knob.
2. **0 T TG-BG gate map** (cell 84 → `data/24`) and **finite-field (B = 3 T) gate
   map** (cell 95 → `data/26`) — the zero/low-field characterization; the 0 T map
   fixes the CNP D-line `Vtg ≈ −1.3·Vbg + 0.06`.
3. **B-n Landau fan at D = 0** (cell 102 → `data/27`, to 8 T) — the first
   field-resolved fan, co-sweeping the constant-D = 0 gate-line vs B. This is the
   latest result at the cut: a bright insulating CNP stripe with only faint,
   washed-out Landau modulation at the VTI's ~1.2 K.

State at the cut: gates parked, Si grounded, base T ≈ 1.2-1.3 K (VTI), field
returned toward 0; the D = 0 fan to 8 T is the freshest result, and no Si-gate
measurement exists yet.

## Caveats carried into the cut

- **Fan plotting limitation.** `data/27/plot.png` shows the live monitor, not the
  re-formed transport map; the `Rxx(n, B)` fan must be built from the TSV as
  `sr{1,2,3}_X / (sr0_X / sr0_gain)` and reshaped row-major `(B, gate-line)`.
  Faithful to the live view — see `reading.md`.
- **VTI base temperature (~1.2 K), not millikelvin.** This rig is a
  variable-temperature insert; the D = 0 fan is visibly washed out, which is the
  campaign's central limitation — too warm for a definitive ABA/ABC call.
- **Trapped-flux zero.** "Zero field" is the magnet's current null, not an absolute
  B = 0; the fan is swept from set field values (0↔8 T), so this is not load-bearing
  here, but don't read an absolute B from a nominal-zero point.
- **Degraded input (v0).** No live kernel, no operator screen, and deliberately
  **no `live_notes.md`**: the next decision (what control to add after the first
  D = 0 fan) does not hinge on an unrecorded live fact.
