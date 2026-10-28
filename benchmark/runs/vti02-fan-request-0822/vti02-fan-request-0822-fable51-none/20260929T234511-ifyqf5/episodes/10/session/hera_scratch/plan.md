# Plan — vti-02 stacking call (ABAB / ABCA / ABCB), VTI, 2026-08-22/23

*Reconstructed at handoff (no plan.md existed in scratch); steps 0–3 are done, step 4 is live.*

## Discriminators I am using (my own model, hedged — no recipe corpus available)

At D = 0, a tetralayer's low-energy bands depend on stacking:
- **ABAB (Bernal)**: mirror-symmetric; two bilayer-like parabolic bands (light/heavy, masses ∝ 2cos(kπ/5): 0.62 and 1.62 × m_BLG), both touching at zero energy. Fan: **two SdH tones, both linear in n through the origin**, F1:F2 ≈ m1:m2 ≈ 0.4, F1 + F2 = F_L(n) = n h/4e; e/h roughly symmetric; zero-energy LL 16-fold (ν = ±8 first plateaus); D opens gaps in both bands.
- **ABCA (rhombohedral)**: single flat (∝k⁴) band; fan: **one tone F = F_L(n)** (no sub-F_L tones unless symmetry-broken pockets), strong-correlation cascades at low |n| (tone jumps to F_L×2, ×4 = half/quarter metals), CNP gap very D-sensitive; e/h fairly symmetric.
- **ABCB (mixed)**: no mirror symmetry; a (gapped) Dirac-like band + bilayer-like band with **intrinsic band offsets** → tones with **nonzero n-intercepts**, pronounced **e/h asymmetry**, small intrinsic gap at D = 0.

What each observable buys: tone count at D = 0 (1 → ABCA; 2 → ABAB/ABCB); intercepts + e/h asymmetry (ABAB vs ABCB); dF_total/dn (lever-arm check of the run-5 scale); LL sequence near CNP at high B (degeneracy structure).

## Steps

| # | step-slug | status | establishes |
|---|---|---|---|
| 0 | VERIFY / kernel probe | done (cells 31–32, 46) | E1 grant; rig state |
| 1 | `gate-current-sanity-check` runs 0–3 | done (ana idx 10–11) | liveness on T_0/B_3, sr1 = B_1–B_2; leakage ≤ 100 pA; two CNP peaks in 1D legs |
| 2 | `gatemap` run 5 (run 4 railed) → `cnp-and-dline-calibration` | done (ana idx 12–13, `cal_run5.json`) | c_bg/c_tg = 0.773 (data), c_tg = geometry prior, n_offset −0.089e12, D_offset −0.013 V/nm; region B (series mosaic) CNP at n_A = −0.43e12; D = 0 window n = −1.27…+3.27e12 |
| 3 | `sdh-spot-check` runs 6 (n = +3.2e12, 0→10 T) and 7 (n = −1.2e12, 10→0.3 T) | data done; **ana landing pending** | e-side: two-band content (7.5–7.8 T light tone with harmonics, ~22 T, and the full-density 33 T above 4 T; F1+F2 ≈ 30 vs F_L 33 → 10 % scale question); h-side: 4.4 / 6.7 / 12.3 T (F_L 12.4). Argues against a single-band (ABCA) read at this n; not decisive alone |
| 4 | **`landau-fan`** D = 0, B 1→10 T uniform-1/B 73 rows, n −1.2…+3.2e12 177 pts | **live (this cell)** | F_i(n) slopes + intercepts, dF_total/dn lever arm, LL sequence near CNP, e/h asymmetry; region-B doubling as a known confound (+0.43e12) |
| 5 | fan analysis (scratch → ana) | next | per-n FFT tone tracks; LL index map (n, B) → filling factors of minima; verdict draft |
| 6 | contingent: second fan riding 10→1 T at finite D (e.g. D = ±0.1 V/nm) **or** LK T-ladder at two n (masses) | decide after step 5 | ABAB vs ABCB if intercepts/asymmetry are ambiguous; masses m1/m2 |
| 7 | verdict cell in ana (output contract) | — | per-region call with strength, evidence by run id, hedges |
| 8 | `return-to-initial` close-out | on operator ask | field 0, gates 0, heaters off, readback → session_notes |

## What would change my mind
- Fan shows a **single** tone tracking F_L(n) on both sides with no sub-F_L content → ABCA becomes the lead; then the 7.5 T tone in run 6 must be explained (region B? symmetry-broken pocket?) → check with a finite-D fan.
- Tones with clear **n-intercepts** or strong e/h asymmetry → ABCB lead; a finite-D fan (gap evolution asymmetric in D) as the confirmation.
- dF_total/dn ≠ h/4e by > 10 % → re-anchor c_tg from the fan before quoting any n.
- Rail / leakage / T excursion in the first rows → abort, fix sensitivity or stop.

## Coverage trades (stated on the page)
- Hole side reaches only n = −1.2e12 (TG −0.3 V limit); electron side to +3.2e12 (TG +1.0 V).
- B ≥ 1 T only: the light band's sub-1 T oscillations are excluded from the fan (covered by the 1D records, runs 6/7).
- Nyquist 40 T in 1/B: tones above 40 T (harmonics, fully lifted degeneracy at n > 2.4e12) alias in the fan; read those from runs 6/7.
- sr1 at 100 µV (10 kΩ FS): the ν = 0 CNP peak at high B will rail over a narrow n window; LL positions are unaffected.
