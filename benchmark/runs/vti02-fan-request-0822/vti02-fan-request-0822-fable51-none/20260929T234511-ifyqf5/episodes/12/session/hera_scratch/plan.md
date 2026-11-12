# Plan — vti-02 stacking call (ABAB / ABCA / ABCB / cannot tell)

*Written 2026-08-23 05:30 by the pickup instance (the first instance left no plan.md;
steps 1–3 are reconstructed from the notebooks and data). Kept current as data lands.*

## State on pickup
- Rig: B = 0 T, gates 0 V, T_sample 1.18 K, heaters off, E1 engaged (session_notes).
- Contact pair available: **one** — Rxx on sr1 = B_1−B_2, drain sr0 = B_3, source T_0. The
  "region-resolved" call therefore has one region (the B_1−B_2 channel), with a **series
  mosaic confound**: run 5 shows a second, parallel CNP ridge (region B) electron-doped by
  0.43e12 relative to region A.
- Calibration (run 5, `cal_run5.json`): c_bg/c_tg = 0.773 (data), c_tg = 2.796e-3 F/m²
  (9.5 nm hBN prior — **absolute n scale is a geometry prior**), n_offset = −0.089e12,
  D_offset = −0.013 V/nm. D = 0 line inside the validators: n = −1.27 … +3.27e12.

## Steps
1. **Gate C liveness** — DONE, runs 0–3: alive, Rxx 60–330 Ω, no leakage.
2. **0 T gatemap → CNP + (n, D) calibration** — DONE, run 5 (ana cells 12–13).
3. **SdH spot checks at D = 0** — DONE, runs 6 (n = +3.2e12, 0→10 T) and 7 (n = −1.2e12,
   10→0.3 T). Scratch read (`ana_spot.py`, `spot_runs67.png`): SdH onset ≈ 1–2 T, clean
   to 10 T. Dominant tones: e-side 29.5 T (= 0.89 F_L(3.2e12) — consistent with one 4-fold
   FS at n 11 % below the prior scale, the same 11 % the ratio fit moved c_bg); h-side
   12.6 T (= 1.02 F_L(1.2e12)). A 7.1–7.3 T tone appears at **both** densities
   (flagged near-residual by `sdh_onset`) — a density-independent frequency is either the
   detrend residual or a fixed-density series region; the fan resolves it (a fixed-n region
   gives lines that don't move with the gate line). **Ana landing pending** (to do while
   the fan runs).
4. **Landau fan at D = 0** — NEXT (operator-requested). Fast axis: the D = 0 gate line,
   n = −1.25 … +3.25e12 in 0.04e12 steps (113 pts, TG 9 mV inside its limits); slow: B rows
   {0, 0.5, 1.0 → 10.0 @ 0.1 T} (93 rows), ascending from 0 where the magnet sits. sr1 at
   100 µV (10 kΩ FS; SdH amplitudes 50–200 Ω, R at 10 T up to ~600 Ω at n = −1.2, the CNP
   column may rail — accepted). fast_delay 1.0 s at τ = 0.3 s/24 dB: filter mean lag 4τ ≈
   1 pt, blur σ ≈ 0.5 pt vs LL spacing ≥ 4.8 pts at 2 T — uniform shift, calibrated by the
   B = 0 row's CNP. Price: 1.23 s/pt (run 5) → 2.3 min/row + 0.1 T ramp 44 s + settle →
   ≈ 5 h.
   **Establishes:** (a) the filling factors ν = n h/(eB) of the Rxx minima — a single fan
   of lines through n = 0 with 4-fold spacing vs two interpenetrating fans with crossings;
   (b) the zero-energy LL degeneracy from the lowest-ν strong gaps (ν = ±16 line is inside
   the window for B < 8.4 T at n = 3.25); (c) the absolute n scale, by requiring integer ν
   (fixes the c_tg anchor); (d) whether the 7.2 T tone moves with n.
   **Templates:** ABCA — one origin, one frequency per n (F = F_L), 16-fold zero LL (gaps
   at ν = ±16 dominant; ν = 4, 8, 12 weaker interaction-driven), large D-tunable gap.
   ABAB — two bilayer-like bands, both from n = 0 at D = 0: two frequencies per n summing to
   F_L, two superposed fans with LL crossings, 8+8 zero-LL. ABCB — mixed: no clean
   decomposition; expect asymmetric/two-origin features unlike either clean template.
   **Abort/adjust:** first row (B = 0): CNP peak must sit at |n| < 0.1e12 with R ≈ 250–300
   Ω, no rail, gate currents at pA; else stop and recalibrate. At ~3 T and ~6 T: interim fan
   plot from the landed rows — continue if LL minima are developing and lines are
   straight; abandon if featureless or the channel rails everywhere.
5. **Follow-ups riding the magnet down from 10 T** (choose on the fan read):
   (a) D-cuts at fixed high B / a finite-D fan row set — the D-tunable CNP gap (run 5:
   R_CNP 240 Ω → 2.4 kΩ at D = 0.25 V/nm) separates ABCA (large gap) from ABAB (small);
   (b) a T-ladder of the CNP resistance at D ≠ 0 (gap size) — `set_both(T, 0.95)`, ≤ 100 K;
   (c) LK m* at a spot — low value at T_e ≈ 8 K, last priority.
6. **Call** — final ana cell per the output contract; then `return-to-initial` close-out.

## What would change my mind
- B = 0 row CNP off n = 0 by > 0.1e12 → the D = 0 line is mis-set; recalibrate n_offset
  before reading ν.
- LL lines not extrapolating to n = 0 → second band / second origin → ABAB or ABCB weight.
- A second fan scaled ×1.13 in n → region B ghost (confound), not a second band.
- Lines that don't move with n (fixed-density set) → ungated series region; exclude from
  the read.
