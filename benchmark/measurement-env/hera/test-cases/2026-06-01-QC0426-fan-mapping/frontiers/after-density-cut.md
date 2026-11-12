---
slug: after-density-cut
user: qingrui
cut_index: 180
latest_fileid: 79
included:
  data: [24, 26, 27, 31, 33, 63, 79]
  images: []
leak_terms:
  - "D=0.25"
  - "D=-1"
  - "D=-0.5"
  - "/ 1.3 - 8"
  - "/ 1.3 + 8"
forward_scan: "Kept region is cells 0-180 (Connect Instruments / gate-range selection / four-corner checks / 0T TG-BG map / finite-field gate sweeps / B-n sweep at D=0 / Si-gate intro / B-n at D=0 Si=+60V / 2T-contact + 6T characterization / gate map at 6T Si=+95V, ending with a 0-field density cut along the D=0.25 line). Grepped kept markdown + comments for forward references (next, later, TODO, will, then, D-series, displacement, fan): only 'sweep at D' hits are the pre-cut D=0 fans (cells 96, 111) — legitimate prior capability, not a forward reference to the D-series. No kept markdown header announces the D=0.25/1/-1/-0.25/-0.5 series; the first such header is '# B-n sweep at D=0.25' at cell 181 (stripped). Clean."
---

# Frontier — cut at end of `# gate map at 6T, Si=+95V` (before the D-series)

*Defines the decision boundary at which this fixture freezes the campaign for
offline replay. The YAML frontmatter above is the machine-readable contract the
`hera-replay` driver reads; the prose below is for humans. This is a **COVERAGE**
decision frontier — the trilayer-graphene device is fully characterized (0 T and
6 T gate maps, Landau fans at D = 0 with and without Si screening, contact and
field checks) and a fresh **0-field density cut along a D = 0.25 gate-line** has
just landed; the move is to **sweep that line vs field into a Landau fan and
repeat the fan across a series of displacement fields**. It is the third of the
three frontiers this campaign carries (the two earlier ones — `after-0T-gatemap`
→ first fan, and `after-D0-fan` → introduce the Si gate — are filed separately).
Added 2026-06-09.*

## The frontmatter contract

- **`cut_index` (180)** — fixture-relative, 0-based, inclusive. The agent sees
  cells `0..180`; everything after is the answer key. (Fixture indices == source
  indices, since the stored notebook was cropped from 0.)
- **`latest_fileid` (79)** — the 0-field density cut along the D = 0.25 gate-line
  (`multisweep` over the `[DC205-TG, k_bg]` line at base field), taken under the
  reconfigured contact set; the agent is pointed here as "the most recent result."
  See `../ground_truth/after-density-cut/reading.md`.
- **`included.data`** — the **allowlist** of pre-cut data dirs the driver
  hardlinks into the working copy: the 0 T TG-BG gate map (24), the finite-field
  gate sweep (26), the two D = 0 Landau fans (27 to 8 T, 31 to 13 T), the
  Si-screened D = 0 fan (33), the 6 T gate map (63), and the latest density cut
  (79). Authoritative; adding any of the post-cut D-series fans (80-84) would be
  the leak.
- **`leak_terms`** — post-cut-only tripwires (see below).
- **`forward_scan`** — human attestation that the kept markdown/comments carry no
  forward references to the D-series.

## Cut

- **Cut index 180** sits on a **section boundary**: cells 179-180 (the last cells
  of the `# gate map at 6T, Si=+95V` block) define the `vtg ∈ [1, 5]`,
  `vbg = vtg/1.3 − 2` gate-line and take a **0-field density cut** along it
  (`s.multisweep`) → `data/79/`. Cell 181 is the `# B-n sweep at D=0.25` markdown
  header — the first cell of the next section (the Landau-fan series), which is
  what HERA must predict.
- **No mid-section header leak.** Truncating at 180 keeps every legitimate prior
  header (through `# gate map at 6T, Si=+95V`, cell 155) and drops all five
  D-series headers (`# B-n sweep at D=0.25` / `D=1` / `D=-1` / `D=-0.25` /
  `D=-0.5`, cells 181/185/189/193/197).

## Leak terms (all verified post-cut-only)

Verified with a pre/post grep over the notebook; every match is at a cell index
> 180:

- **`D=0.25`** — the first D-series header (cells 181, 183, 187, 191, 195). The
  D value being predicted. (Note: the bare D-line *construction* `linspace(1, 5)`
  / `/ 1.3 - 2` for D = 0.25 **does** appear pre-cut at cells 179-180 — that is
  the served density cut's own gate-line, legitimately in hand — so the tripwire
  is the `D=0.25` label, not the line arithmetic.)
- **`D=-1`** — the D = −1 header (cell 189), post-cut only.
- **`D=-0.5`** — the D = −0.5 comment/header (cells 197, 199), post-cut only.
- **`/ 1.3 - 8`** — the D = 1 gate-line offset (`vbg = vtg/1.3 − 8`, cell 186), a
  parameter signature unique to the post-cut series.
- **`/ 1.3 + 8`** — the D = −1 gate-line offset (`vbg = vtg/1.3 + 8`, cell 190),
  likewise post-cut only.

Note on the **reconfigured contacts** (`sr0` "drain current on 42", `sr1=09-01`,
`sr3=09-12`): deliberately *not* leak terms. The new contact set appears in the
kept region (the 6 T characterization block, cells 130-180, and the served
density cut 79 itself), so it is pre-cut capability, not an answer signature.

## What's live at the cut

A VTI cooldown of trilayer-graphene QC0426, fully characterized and now set up for
field mapping:

1. **Instruments + gate ranges** (cells 0-80) — FastBi1K5 magnet, LakeShore
   thermometry, SR830 lock-ins, the **DC205 driving the top gate** and Keithleys
   driving the back (`k_bg`) and Si (`k_2410`) gates; safe ranges chosen
   (`k_tg ∈ [−6.5, 7.5]`, `k_bg ∈ [−5, 4.8]`).
2. **0 T TG-BG gate map** (cell 84 → `data/24`) and **finite-field gate sweep**
   (cell 95 → `data/26`) — the zero-field characterization.
3. **B-n Landau fan at D = 0** (cell 102 → `data/27`, to 8 T; and `data/31`, to
   13 T) — establishes the fan technique and the `Vtg ≈ −1.3·Vbg + 0.06` CNP
   D-line.
4. **Si-gate introduction** and **D = 0 fan with Si = +60 V** (cells 103-115 →
   `data/33`) — screening test.
5. **2T-contact + 6 T characterization** (cells 116-180) — contact checks, a
   **6 T gate map** (`data/63`), and finally a **0-field density cut along the
   D = 0.25 line** (`data/79`, the latest landed sweep), under a reconfigured
   contact set (`sr0` on 42, `sr1=09-01`, …), `Si = +95 V`.

State at the cut: gates parked, `Si = +95 V` context, base T ≈ 1.2-1.3 K (VTI),
field returned to ~0; a 0-field density cut along the D = 0.25 gate-line is the
freshest result.

## Caveats carried into the cut

- **Density-cut plotting limitation.** `data/79/plot.png` shows the live monitor,
  not the re-formed transport trace; the `Rxx(n)` curve must be built from the TSV
  as `sr{1,2,3}_X / (sr0_X / sr0_gain)`. Faithful to the live view — see
  `reading.md`.
- **VTI base temperature (~1.2 K), not millikelvin.** This rig is a
  variable-temperature insert; `sample_temperature ≈ 1.246 K` at the density cut.
  Quantum-Hall plateaus are resolvable at 1 K + several T, but fractional/fragile
  states are not — relevant when judging what the fan can show.
- **Trapped-flux zero.** As on the toploader rig, "zero field" is the magnet's
  current null, not an absolute B = 0; the fans are swept from set field values
  (0↔8 T) so this is not load-bearing here, but don't read an absolute B from a
  nominal-zero point.
- **Degraded input (v0).** No live kernel, no operator screen, and deliberately
  **no `live_notes.md`**: the next decision (turn the density cut into a Landau
  fan and sweep the fan across D) does not hinge on an unrecorded live fact.
