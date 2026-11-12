# vti-02 — stacking-order plan (live; rewritten 2026-08-23 at the handoff)

Goal: ABAB / ABCA / ABCB for vti-02, region-resolved on the one wired Rxx pair
(sr1 = B_1 − B_2), evidence-cited, or a calibrated "cannot tell".

## Where the session stands

| step | slug | runs | status |
|---|---|---|---|
| Gate C | `gate-current-sanity-check` | 0–3 | done — contacts live, gates leak-free |
| 1 | `gatemap` (0 T) | 4 (railed), 5 | done |
| 2 | `cnp-and-dline-calibration` | (ana on 5) | done — cal in `cal_run5.json` |
| 3 | `sdh-spot-check` e-side / h-side | 6, 7 | data done; **ana landing now** |
| 4a | `cnp-vs-field` | next | pre-leg: R_CNP(B) 0 → 10 T, also sizes 4b |
| 4b | `landau-fan` | next | **the decisive step** |
| 5 | call in ana | — | output contract |

Calibration in force (run 5): c_tg = 2.796 mF/m² (9.5 nm geometry prior —
absolute n scale is a prior, the *ratio* is data), c_bg/c_tg = 0.773,
n_offset = −0.089e12, D_offset = −0.013 V/nm. D = 0 line inside the validators
spans n = −1.27 … +3.27e12 (TG-limited both ends).

**Two regions in series on the one pair.** Run 5 resolved two parallel CNP
ridges: A (main) and B, offset by 0.43e12 in n (B electron-doped vs A). Every
feature in a 1D or fan trace appears twice, shifted by 0.43e12. This is the
"region" axis the output contract asks for — A and B, not two contact pairs.

## What runs 6/7 established (and why the fan is now the right spend)

Both spot checks are *strong*: clean SdH, onsets at 0.3–0.7 T, many tones,
SNR 20–120. The device is far better than the feasibility model assumed
(T_e ≈ 8 K was expected to kill light-mass tones below ~1.5 T; it did not).

- run 6, n = +3.2e12, D = 0: FFT peaks 7.85 / 14.58 / 22.43 / 29.15 T.
  F_L(full n, prior scale) = 33.1 T.
- run 7, n = −1.2e12, D = 0: 6.8 / 4.53 / 12.47 / 19.27 T. F_L = 12.4 T.

Run 6 admits **two readings that a 1D trace cannot separate**:
 (i) **two Fermi surfaces** at 7.85 and 22.43 T — sum 30.3 T ≈ F_L (8 % under
     the geometry prior, i.e. c_tg ~8 % high, entirely allowed), with the
     14.58 T peak the *difference* (22.43 − 7.85 = 14.58 exactly) and 29.15 the
     sum. Ratio 2.86 — compare Bernal-tetralayer (ABAB) subband mass ratio
     (√5+1)/(√5−1) = 2.618, which fixes the two-subband population ratio.
 (ii) **one Fermi surface at ~7.3 T with harmonics** 2×/3×/4× — then the
     carried density is 24 % of the total and the other 76 % is unaccounted
     for, which no stacking explains. Disfavoured by the sum rule already, but
     the ladder spacings (6.73 / 7.85 / 6.72) sit within one FFT bin (1.1 T)
     of uniform, so a 1D record at one density cannot close it.

The discriminator is the **n-dependence**, which is what a fan measures:
a harmonic ladder keeps exact integer ratios at *every* n and scales as one
frequency; two subbands track their own partial densities, close the sum rule
F₁(n) + F₂(n) = |n|h/4e at every n, and carry the stacking answer in the ratio.

## Step 4a — `cnp-vs-field` (pre-leg, ~1 h 25 m)

n = 0, D = 0; B 0 → 10 T, 100 mT, sr1 at 1 mV (100 kΩ FS).
- The fan wants to run **descending** from 10 T (no wasted traverse, worst-case
  row first). Getting to 10 T costs a 73 min blind ramp either way — recording
  it costs ~10 min more and buys a real measurement.
- **Science:** R_CNP(B) at D = 0 to 10 T. ABAB tetralayer is a compensated
  semimetal at D = 0 → the ν = 0 state stays modest; ABCA and ABCB are gapped
  at D = 0 → R_CNP should climb hard. Run 5 gives the B = 0 anchor: 240 Ω.
- **Engineering:** it measures the fan's worst-case R (the fan's maximum sits
  at n ≈ 0, B = 10 T), so 4b's sensitivity is sized from data, not a guess.
  (Session lesson from run 4: size the map from the ridge, not the 1D peak.)

## Step 4b — `landau-fan` (~4 h)

`multimegasweep`: slow = `magnet.field`, 91 rows **uniform in 1/B**, 10 → 1.0 T
(`field_invB`); fast = (`k_tg.volt`, `k_bg.volt`) co-swept along D = 0,
n = −1.22 … +3.18e12, Δn = 0.05e12, 89 points (V_tg −0.283 … +0.978, 22 mV
inside the TG limit at the top, 17 mV at the bottom).

Why these numbers:
- uniform 1/B → `sdh_fft` FFTs the record directly, no resample. ΔF = 1.11 T
  (separates 7.85 from 9.2 and from 22.4 comfortably); F_Nyquist = 50 T, above
  F_L(3.18e12) = 32.9 T *and* its 1st harmonic partner, so nothing strong
  aliases down into the fundamentals.
- Δn = 0.05e12 → the ν = 4 gap (Δn = 4eB/h) is 19 points wide at 10 T, 3.9 at
  2 T. Lock-in group delay (4τ = 1.2 s at τ = 0.3 s, 24 dB/oct) with
  `fast_delay = 1.0` is ~1.1 points of lag — a constant n-shift, identical
  every row, corrected in ana; blur stays under one ν = 4 gap down to ~1.5 T.
  `fast_delay = 1.0` is run 5's validated value (81.2 min / 4158 pts = 1.17 s/pt).
- descending B, monotonic: no re-traverse; ends at 1 T so close-out is 7 min.

What it establishes:
1. F_i(n) for every tone across both carrier signs → sum rule and ratio.
2. The filling-factor structure (which ν are gapped, degeneracy steps) — the
   fan lines themselves, doubled at the 0.43e12 region-B offset.
3. The CNP's behaviour in field, at n-resolution the pre-leg cannot give.

## What would change my mind

- Pre-leg shows R_CNP railing past 100 kΩ by 4–5 T → re-size 4b's sensitivity
  (and that is itself strong evidence *against* ABAB).
- Fan first rows (10 T, 9.1 T) show a railed or flat channel → abort, re-size.
- If F(n) turns out to be a single frequency tracking |n|h/4e with integer
  harmonics and no second surface anywhere on the fan → reading (ii) wins and
  the call goes toward ABCA (single flat surface), not ABAB.
- If a third independent frequency appears that is not a sum/difference/harmonic
  of two fundamentals → ABCB comes into play (and/or the region-B copy is being
  misread); resolve by checking whether it tracks the 0.43e12-shifted density.
- If the fan's tone ratio drifts strongly with n rather than sitting near a
  fixed value → nonparabolicity/Lifshitz; the call must be made on the low-n
  end and hedged.

## Not doing (and why)

- Finite-D fans: the D = 0 fan is the undressed-subband measurement and the
  window is TG-limited; a D fan is the next session's spend, flagged as a hedge.
- Si-gate survey: session-banned.
- Elevated-T (LK mass) ladder: would pin m* per tone and is the natural
  corroboration, but it is a multi-hour spend on top of 5.5 h; hold it as the
  contingency if the fan leaves the ratio ambiguous.
