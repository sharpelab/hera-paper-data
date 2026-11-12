# vti-02 stacking call — plan (HERA, living document)

*Re-written 2026-08-23 ~05:30 at the instance handoff: the prior instance's plan lived only in
measure-cell markdown (cells 35/39/41). Steps 0–3 below reconstruct what ran; 4+ is forward.*

Goal: ABAB vs ABCA vs ABCB for the one measured contact pair (sr1 = B_1−B_2; source T_0, drain B_3),
region-resolved where the data allows, per the brief's output contract.

## Fixed facts this session established
- Gate C pass (runs 0–3): alive, gate currents at pA offsets, Rxx 60–330 Ω at 0 T.
- Run 5 gatemap (run 4 = same map aborted, railed at 2 kΩ): ridge A (main) + parallel ridge B.
  Cal (region A): c_bg/c_tg = 0.773 (data), c_tg = 2.796e-3 F/m² (9.5 nm prior — absolute
  n scale unverified), n_offset −0.089e12, D_offset −0.013 V/nm (R_CNP(D) vertex).
  Region B is +0.43e12 electron-doped vs A (series mosaic between B_1 and B_2).
  R_CNP grows 300 Ω (D≈0) → ~2.4 kΩ (D≈+0.25 V/nm); −D side covered only to −0.08 V/nm.
  D = 0 line inside validators: n = −1.27 … +3.27e12 (TG-limited both ends).
- Runs 6/7 SdH spot checks at D = 0 (n = +3.2 / −1.2e12): see ana; both show a ~7 T light tone
  (onset ≤ 1 T) plus heavier content; single traces can't separate independent tones from harmonics
  or tell whether the ~7 T tone tracks n.

## Discriminators (what each stacking predicts, D = 0)
- **ABAB**: two bilayer-like bands (mass ratio ≈ 2.6) → two SdH branches whose frequencies both
  scale with n and sum to F_L (light fraction ≈ 0.2–0.3 at high n; closer to balanced near the CNP
  semimetal regime). Light branch has small m* → survives LK at T_e ≈ 8 K to ~1 T. Low R_CNP at D = 0,
  gap opened by D. Many LL crossings between the two ladders at high B.
- **ABCA**: one chiral (quartic) band → a single branch F = F_L above the Lifshitz regime, heavy m*
  (LK-suppressed at T_e ≈ 8 K; may show only at high B); no light tone. Strongly insulating CNP that
  grows fast with |D|; few LL crossings.
- **ABCB**: two bands with a split unlike ABAB and no inversion symmetry → R_CNP(D) minimum displaced
  from the gate-symmetric point / ±D asymmetry. (Hedge: my ABCB band-fraction expectation is the least
  certain of the three — the call leans on the ABAB/ABCA contrasts plus the ±D symmetry test.)
- **Confounds**: (i) mosaic — region B replicates every branch shifted by −0.43e12 in n (same slope,
  offset), not a second band; (ii) a flat F(n) tone = ungated/contact-doped region (Si couples to the
  contacts), not a band; (iii) harmonics k·F.

## Steps
0. Gate C — DONE (runs 0–3).
1. 0 T gatemap + (n, D) calibration — DONE (run 5).
2. Feasibility model (F_L, ABAB pair, LK at T_e 8 K) — DONE (measure cell 39/41 markdown).
3. SdH spot checks both carrier signs at D = 0 — DONE (runs 6, 7). Ana landed 2026-08-23.
4. **D = 0 Landau fan** (`landau-fan`) — NEXT (operator's request). B slow 10 → 0.8 T descending
   (0.2 T steps to 5.2 T, then uniform in 1/B, Δ(1/B) = 0.008: 157 rows), n fast −1.24 … +3.24e12
   at 0.04e12 (113 pts) co-swept (Vtg, Vbg) on the region-A D = 0 line, fast_delay 1 s, sr1 200 µV.
   Pre-ramp 0 → 10 T unrecorded. ≈ 9 h. Establishes: F(n) branches (count, slopes, sum rule), which
   tones track n vs sit flat, mosaic replicas, high-B QH sequence + LL crossings, R_CNP(B) column.
   Checkpoints: first row at 10 T (rail at CNP? gate currents, CNP/ridge-B positions vs cal);
   after the 10 → 5.2 T block (~1.5 h in: QH pattern); at B ≈ 2 T (partial column FFT on 1/B part).
5. Conditional on step 4:
   5a. Two n-tracking branches summing to F_L → ABAB lean. Test with D: an (n, D) cut at fixed high B
       or a finite-D fan within validators (hybridization / crossing shifts), and the ±D R_CNP
       symmetry at 0 T with the −D side covered (small gatemap extension inside the validators).
   5b. Single F_L branch / no light tone → ABCA lean; confirm with R_CNP(D) gap growth and T-dep.
   5c. Unequal split / asymmetric R_CNP(±D) → ABCB lean; measure the ±D R_CNP symmetry directly.
   5d. m* of the light tone from SdH T-dependence (set_both ladder, ratio 0.95) at 1–2 densities if the
       mass is what separates the candidates.
6. Call in ana (output contract). 7. Close-out (`return-to-initial`).

## What would change my mind
- ~7 T tone flat in n across the fan → it is parasitic, drop it from the band count.
- Only replica-slope branches (equal dF/dn, n-offset 0.43e12) → mosaic, one band per region → ABCA lean.
- Branch sum ≠ F_L by > ~15 % across n → absolute c_tg scale is off (9.5 nm prior) or a band is missing;
  re-anchor the n scale on QH minima at high B (ν = nh/eB) before reading fractions.
- Fan rows rail at the CNP at high B → confined to |n| ≲ 0.1e12 accept; otherwise resize and restart.
