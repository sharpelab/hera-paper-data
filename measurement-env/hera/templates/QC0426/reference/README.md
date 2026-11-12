# Reference pack — QC0426 / 2026-06-10 HERA session

Curated baseline snippets for Gate C (re-entry checks). **This pack is the
session's only prior data** — the agent does not read other campaign
directories (see the session brief).

## Files

- `baseline_B0_densitycut_Dp0p25.{csv,png}` — Rxx(n) at **B = 0**,
  D = +0.25 V/nm, Si = +50 V, 201 pts.
- `baseline_B0_densitycut_Dm0p25.{csv,png}` — same at D = −0.25 V/nm,
  101 pts.

Both on the session wiring (`sr1 = 09-01`, `sr2 = 12-20`, drain on 42,
gain −1e6), extracted from the prior campaign's final measurements
(2026-06-09) by the session team. CSV columns:
`vtg_V vbg_V n_1e12cm2 current_A R_sr1_Ohm R_sr2_Ohm` (R already includes
the sr0 gain division).

## What to compare on re-entry

A fresh density cut along the same D-line should reproduce, per channel:

1. **Resistance scale** — CNP peak |Rxx| within ~2× of the baseline
   (sr1 at D = +0.25: ≈ 4.5 kΩ; at D = −0.25: ≈ 15 kΩ).
2. **CNP position** — peak within ~0.1×10¹² cm⁻² of n = 0 (else the
   n-offset has drifted; refit before designing D-lines).
3. **Shape** — electron/hole-side asymmetry and the broad fall-off;
   gross changes suggest contact degradation over the handover.
4. **Drain current** — |I| ≈ 5 nA scale at 0.5 V through 100 MΩ;
   a large drop means a contact or wiring problem, stop and ask.

Disagreement on any of these is a stop-and-report, not a push-through.
