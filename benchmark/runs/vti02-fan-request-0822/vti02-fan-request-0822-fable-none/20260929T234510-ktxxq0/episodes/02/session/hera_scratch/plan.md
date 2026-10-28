# vti-02 stacking-order plan (rebuilt 2026-08-23 — plan.md was missing from scratch at handoff; reconstructed from the notebooks + session notes)

**Goal:** ABAB vs ABCA vs ABCB call (or calibrated "cannot tell"), region-resolved, evidence-cited (output contract in the brief).

## Steps

1. ~~**Gate C liveness + gate-current sanity** (runs 0–3)~~ — done. Provided pair alive; leakage at pA floor.
2. ~~**0 T gatemap → CNP + (n, D) calibration** (runs 4–5)~~ — done. Ratio c_bg/c_tg = 0.773 (data), c_tg = geometry prior (scale ±~10%), n_offset −0.089e12, D_offset −0.013 V/nm. Two CNP ridges: main region A + parallel region B (mosaic, A + 0.43e12 — series confound: possible satellite tones at ×1.13 in F). D-tunable gap on ridge A (240 Ω at D≈0 → 2.4 kΩ at +0.25 V/nm) — 3 candidate parents, not a stacking read alone.
3. ~~**SdH spot checks at D = 0** (runs 6–7)~~ — done (ana cells 14–15). Electron n=+3.2e12: tones 7.1/14.1/22.1/29.5 T; favored read light+heavy two-band (7.1 + 29.5 = 36.6 vs F_full 33.1, +11% inside scale prior) — Bernal-consistent, ABCB not excluded, harmonic-ladder reading not excluded. Hole n=−1.2e12: multi-pocket (6.6+4.7 ≈ 11.3 vs 12.4), semimetal-like.
4. **→ Landau fan at D = 0** (this step, operator-requested): fast (Vtg,Vbg) along D=0, n −1.25→+3.24e12, 129 pts; slow B 0→10 T, 50 mT, 201 rows. ~10 h 45 m. Establishes: (a) F(n) branches — harmonics scale together, bands have distinct dF/dn; sum rule ΣF(n) vs F_full(n) calibrates the lever-arm scale absolutely; (b) fan-line slopes → gap filling factors → LL degeneracy pattern; (c) CNP column vs B → gapped vs semimetallic at D = 0. Discriminators: ABAB — light+heavy bilayer-like pair, semimetallic-ish CNP at D=0; ABCA — single heavy/flat low-E band (LK-dead tones at T_e≈8 K, F≈F_full singleton), strong CNP gap physics; ABCB — gapped at D=0 even, monolayer-like + bilayer-like mix.
5. **Contingency / refinement** (pick by fan read): D≠0 fan or fixed-n D-sweeps at moderate B (gap closing/opening vs D — ABAB gap opens with |D|, ABCA gap at D=0 closes then reopens, ABCB asymmetric in D); ride the 10 T end down for whatever B-path the choice needs (never re-traverse).
6. **Call** — final ana cell per the output contract (per-region: A and mosaic-B satellite read).
7. **Close-out** — `return-to-initial` (field 0, gates 0 at committed pacing, heaters off, readback → session_notes).

## What would change my mind / kill criteria
- Fan first rows: rail (>50 kΩ at CNP low-B — unexpected), leak trip, dead channel → abort at minutes.
- ~2.5 T checkpoint: fan lines forming? If Rxx(n) featureless at 2.5 T beyond runs 6/7 levels → check sensitivity/smearing before burning 8 more h.
- ~5 T checkpoint: partial per-column FFT — if F(n) already separates harmonic-vs-band cleanly and CNP behavior is unambiguous, consider truncating at ~8 T to buy the D-sweep step.
- Mosaic: satellite branches at ×1.13 in F(n) → attribute to region B, keep verdicts per-region.
