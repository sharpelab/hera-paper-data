# vti-02 stacking-order plan (written 2026-08-23 at handoff pickup; steps 1–3 were run by the previous instance)

Goal: ABAB vs ABCA vs ABCB, region-resolved (one pair wired: sr1 = B_1−B_2), evidence-cited. No Rxy channel —
every filling-factor read comes from Rxx minima lines in the (n, B) plane.

## Discriminants (what the data must show)
- **ABCA (rhombohedral)**: one chiral band, zero-energy LL 16-fold (4 orbitals × spin/valley). Fan at D = 0: gap-free
  block |ν| < 8 at low B, first strong minima at ν = ±8, then Δν = 4; symmetry-broken integers appear only at high B.
  SdH at fixed n: a single fundamental at F_L = n h/4e (plus harmonics). B = 0 CNP at D = 0 gapless / weakly gapped.
- **ABAB (Bernal)**: two bilayer-like sub-bands (light + heavy) overlapping at D = 0 (semimetal). Fan: two
  interpenetrating LL ladders with different slopes, LL crossings; near the CNP electron- and hole-like lines coexist.
  SdH at fixed n: two fundamentals F_light + F_heavy = F_L (light ≈ 0.2–0.3 F_L).
- **ABCB (mixed)**: monolayer-like Dirac band + bilayer-like band, no inversion → intrinsic gap at D = 0. Fan: a
  Dirac-like sequence (ν = ±2, ±6, ±10 …) superimposed on a 4-fold ladder; CNP gapped at D = 0 already at B = 0.
- Confound carried since runs 0–3: **series mosaic** — a second CNP ridge (region B) electron-doped by 0.43×10¹² vs
  region A (run 5). Its fan is region A's fan shifted by Δn = +0.43×10¹² along n (same slopes). Read both.

## Steps
1. ✅ Gate C liveness (runs 0–3): alive, 60–330 Ω, no leakage. Two CNPs in series.
2. ✅ 0 T gatemap (run 5; run 4 railed): CNP ridge A, ratio c_bg/c_tg = 0.773, n_offset −0.089, D_offset −0.013
   (R_CNP(D) vertex). Absolute n scale = geometry prior (c_tg at 9.5 nm) — **uncalibrated until the fan slopes fix it**.
3. ✅ SdH spot checks at D = 0 (run 6: n = +3.2; run 7: n = −1.2): oscillations from ~1.6 T, Rxx → 0 minima on the
   electron side; irregular 1/B spacing on both — two ladders and/or the mosaic; 1D cannot separate them.
4. **▶ Landau fan at D = 0** (`landau-fan`): B slow 1.5 → 10 T (0.1 T, 86 rows), (V_tg, V_bg) co-swept along the
   calibrated D = 0 line, n = −1.25 … +3.25×10¹² (129 pts). Establishes: the ν sequence at low ν (high B), LL crossings
   (Bernal) or their absence, the absolute n scale from the line slopes (dn/dB = ν e/h), and the region-B offset fan.
   ~5.5 h. Ends at 10 T.
5. Depending on step 4: (a) if lines are clean, a D ≠ 0 fan or a fixed-B (10 T) (n, D) map to test gap opening vs D
   (ABCA: ν = 0 gap grows monotonically with |D|; ABAB: LL crossings move with D); (b) if T_e-limited, a short
   temperature ladder on one strong minimum for the LL gap / mass. Ride the magnet down through whatever comes next.
6. Call in ana (output contract), then `return-to-initial` on the operator's ask.

## What would change my mind
- Fan lines not straight through the origin → n calibration/offset wrong → refit before any ν assignment.
- Region B dominating (its fan stronger than A's) → the contact pair reads mostly region B; call per region anyway.
- Rail of sr1 across a broad low-|n| band at high B → the ν = 0 state is ≥ 20 kΩ: strongly gapped — itself evidence.
- No minima below ν ≈ 8 at 10 T on either side → consistent with ABCA's 16-fold zero LL; ν = ±4 minima present at
  moderate B → against ABCA.
