---
slug: after-0T-gatemap
user: qingrui
cut_index: 95
latest_fileid: 26
included:
  data: [24, 25, 26]
  images: []
leak_terms:
  - "B-n sweep"
  - "-1.3*Vbg"
  - "multimegasweep([magnet.mag]"
forward_scan: "Kept region is cells 0-95 (Connect Instruments / lock-ins / Keithleys / DC205 setup / gate-range selection [k_bg in [-5,4.8], k_tg in [-6.5,7.5]] / four-corner checks / 0T TG-BG gate map / gate sweep at finite field B=3T). Grepped kept markdown + comments for forward references (next, later, TODO, will, then, fan, Landau, displacement, D-series): no hits. The only 'field' hits in the kept region are cells 89/93/94 — the served `# gate sweeps at finite field` section header, `magnet.get_field()`, and the `B field (T)` config key — i.e. the finite-field (3T) gate map that is itself part of the served region (run 26), legitimate prior capability, not a forward reference to the D=0 Landau fan. No kept markdown header announces the B-n fan; the first such header is '# B-n sweep at D = 0' at cell 96 (stripped). Clean."
---

# Frontier — cut at end of `# gate sweeps at finite field` (before the first B-n fan)

*Defines the decision boundary at which this fixture freezes the campaign for
offline replay. The YAML frontmatter above is the machine-readable contract the
`hera-replay` driver reads; the prose below is for humans. This is a **DECISION**
frontier — the trilayer-graphene device has been characterized at and near zero
field (a 0 T TG-BG gate map and a 3 T finite-field gate map, on top of
instrument bring-up, gate-range selection, and four-corner checks), and the move
is to **go to field and measure the first B-n Landau fan at the charge-neutral
D = 0 line** — the step that starts resolving the quantum-Hall structure that
discriminates the stacking (ABA vs ABC). It is the first of the three frontiers
this campaign carries (the later two — `after-D0-fan` → introduce the Si gate,
and `after-density-cut` → sweep the fan across a D-series — are filed
separately). Added 2026-06-09.*

## The frontmatter contract

- **`cut_index` (95)** — fixture-relative, 0-based, inclusive. The agent sees
  cells `0..95`; everything after is the answer key. (Fixture indices == source
  indices, since the stored notebook was cropped from 0.)
- **`latest_fileid` (26)** — the **finite-field (B = 3 T) TG-BG gate map**
  (`megasweep` over `k_bg` × `dc205_volt`), the last sweep before the field-axis
  fan; the agent is pointed here as "the most recent result." See
  `../ground_truth/after-0T-gatemap/reading.md`.
- **`included.data`** — the **allowlist** of pre-cut data dirs the driver
  hardlinks into the working copy: the aborted first 0 T TG-BG map (24, cell 84 —
  stopped at ~1.2k of 55k points), the **complete** 0 T TG-BG gate map (25,
  cell 88), and the **3 T finite-field gate map** (26, cell 95, the latest).
  Authoritative; adding the post-cut D = 0 fan (27) or any later fan would be the
  leak.
- **`leak_terms`** — post-cut-only tripwires (see below).
- **`forward_scan`** — human attestation that the kept markdown/comments carry no
  forward references to the B-n fan.

## Cut

- **Cut index 95** sits on a **section boundary**: cell 95 is the last cell of
  the `# gate sweeps at finite field` block (the `megasweep` over `k_bg` ×
  `dc205_volt` at B = 3 T → `data/26/`). Cell 96 is the `# B-n sweep at D = 0`
  markdown header — the first cell of the next section (the Landau fan), which is
  what HERA must predict. Cell 97 (`## n=0 roughly corresponds to
  Vtg = -1.3*Vbg + 0.06 (from CNP at 0T)`) is the fan's D = 0 line setup.
- **No mid-section header leak.** Truncating at 95 keeps every legitimate prior
  header (through `# gate sweeps at finite field`, cell 89) and drops the first
  fan header `# B-n sweep at D = 0` (cell 96) and all the later fan / Si-gate /
  6 T / D-series headers.

## Leak terms (all verified post-cut-only)

Verified with a pre/post grep over the notebook (`nb grep <notebook> -i <term>`);
every match is at a cell index > 95:

- **`B-n sweep`** — the B-n fan section-header family (first at cell 96; recurs in
  the fan configs and the D-series headers). The move being predicted. No pre-cut
  occurrence.
- **`-1.3*Vbg`** — the CNP D-line note at cell 97 (`Vtg = -1.3*Vbg + 0.06`), which
  sets up the constant-D = 0 line the fan co-sweeps. The notebook writes this only
  post-cut. *(The CNP **slope as a fact** is legitimately in hand — the device
  card reports `Vtg ≈ −1.3·Vbg + 0.06` fitted from the 0 T map, in unicode — but
  that is a different token from the notebook's ASCII `-1.3*Vbg`, so the tripwire
  catches a re-leak of the fan setup, not the established device knowledge. Same
  precedent as `after-density-cut`'s `D=0.25` label vs the device-card's `D = 0.25`.)*
- **`multimegasweep([magnet.mag]`** — the field-axis fan-sweep signature
  (`s.multimegasweep([magnet.mag], [np.linspace(0, 8, 401)], …)`, cell 102), the
  call that adds the B axis. Compound on purpose: **bare `magnet.mag` appears
  pre-cut** at cell 92 (`magnet.mag(3)`, ramping to the 3 T gate map), so using
  bare `magnet.mag` as a tripwire would false-positive — the answer signature is
  specifically a `multimegasweep` *over* the magnet axis.

Note on **`magnet.mag` / `B field`**: deliberately *not* bare leak terms. The
magnet is driven in the kept region (cell 92 ramps to 3 T, cells 93-94 read the
field for the served finite-field map), so field use is pre-cut capability, not
an answer signature — the fan-specific compound above is the tripwire.

## What's live at the cut

A VTI cooldown of trilayer-graphene QC0426, characterized at and near zero field
and poised to go to field:

1. **Instruments + gate ranges** (cells 0-80) — AMI430 magnet, LakeShore
   thermometry, SR830 lock-ins, the **DC205 driving the top gate** (`DC_bias`)
   and Keithleys driving the back (`k_bg`) and Si (`k_2410`) gates; safe ranges
   chosen by 1D sweeps and four-corner checks (`k_tg ∈ [−6.5, 7.5]`,
   `k_bg ∈ [−5, 4.8]`). *(Cell 51: the back-gate Keithley was briefly repatched to
   push the top gate during range-finding — read `measurement_config` per run.)*
2. **0 T TG-BG gate map** (cell 88 → `data/25`, complete; cell 84 → `data/24`, an
   aborted first pass) — the zero-field characterization; the CNP diagonal it
   shows is what fixes the `Vtg ≈ −1.3·Vbg + 0.06` D = 0 line.
3. **3 T finite-field gate map** (cell 95 → `data/26`, the latest landed sweep) —
   the same `k_bg × dc205_volt` map repeated at B = 3 T; the CNP diagonal
   persists, the immediate precursor to a full B-n fan.

State at the cut: gates parked, Si gate grounded (this section floats / grounds
the Si gate — the Si screening comes later), magnet at the 3 T set-point for the
finite-field map (about to be swept), base T ≈ 1.2 K (VTI).

## Caveats carried into the cut

- **Gate-map plotting limitation.** `data/<id>/plot.png` shows the live monitor,
  not the re-formed transport map; the `Rxx(Vtg, Vbg)` map must be built from the
  TSV as `sr{1,2,3}_X / (sr0_X / sr0_gain)` and reshaped over the megasweep grid.
  Faithful to the live view — see `reading.md`.
- **VTI base temperature (~1.2 K), not millikelvin.** This rig is a
  variable-temperature insert; `sample_temperature ≈ 1.18 K` at the 3 T map.
  Quantum-Hall plateaus are resolvable at 1 K + several T, but fragile/fractional
  states are not — relevant when judging what the coming fan can show (and why the
  campaign ultimately couldn't make a definitive ABA/ABC call).
- **Trapped-flux zero.** "Zero field" is the magnet's current null, not an
  absolute B = 0; the fans are swept from set field values (0↔8 T, 13→0 T), so
  this is not load-bearing here, but don't read an absolute B from a nominal-zero
  point.
- **Degraded input (v0).** No live kernel, no operator screen, and deliberately
  **no `live_notes.md`**: the next decision (go to field and take the B-n fan at
  D = 0) does not hinge on an unrecorded live fact.
