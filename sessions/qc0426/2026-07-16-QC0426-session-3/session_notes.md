# Session notes — QC0426 / VTI

Operational log (not a science notebook).

- **GRANT — 2026-07-16 ~14:45**: operator (Zack) said "go for autonomy" → E1 engaged.
  SAFETIES green from disk (cell 18 exec [10], card numbers verbatim). Session-start
  VERIFY cell (idx 28, id 1633bd9a) landed but not yet run at grant time — executed
  by HERA as first E1 actions (kernel-binding probe first, per brief).

- **TOOLING** — `hera.analysis.Run.col()` raises on the swept-gate voltage column
  because the sweep axis and an explicit `fp(gate.volt)` produce duplicate column
  names (`k_2400_tg_volt` at indices 1 and 3 in runs 0–3); worked around with
  `col_at(1)`. Either the recipes should drop the redundant `fp(swept.volt)` or
  `col()` could prefer the setpoint column with a warning.

- **TOOLING** — `hera.analysis.sdh_onset` returned `onset_b = NaN` on run 6 (clean
  1303-pt SdH record, oscillations clearly emerging ~1.8-2 T in the bg-subtracted
  trace). consensus_freq was sensible (11.1 T). Onset had to be read by eye —
  investigate the SNR-window logic (possibly the low-B window never crosses its
  SNR threshold at T_e ~ 8 K amplitudes).

- **RECIPE FIX — landau-fan**: the step-1 dynamic-range rule sizes the worst corner
  from "spot-check/CNP R-anchor × the measured MR factor", but the MR factor is
  strongly n-dependent: QC0426 showed ×20 (0→8 T) at n=-6e12 vs ×7.8 already by
  1.6 T at n=-1.5e12 (near-CNP columns). Fan v1 (run 8) was killed at first rows for
  exactly this. Suggest the rule name the *low-n* MR factor explicitly, and when no
  low-n field data exists, take the first fan rows as the calibrator before
  committing (or start the fan at the low-|n| end of a descending... — direction
  doesn't help; first-rows check does).

- **RECIPE FIX — trilayer-stacking-fs-count / fs_count_b0**: the model's `aba_fs` /
  `abc_fs` solve the electron side only (E_F search over positive energies /
  conduction band), but the investigation's Verify names the Onsager overlay as
  primary arc-reader without stating the electron-only limitation — this session's
  fan is hole-side (chosen per step 3, cleaner SdH), so the overlay is qualitative
  here. Also both spot-check densities (±6e12) sit above the |n| ≤ 3.5e12 clamp.
  Suggest: README + investigation note the hole-side gap next to the clamp; model
  TODO gains "valence-band F(n)".

- **Session wrap 2026-07-17 ~03:40**: campaign goal delivered — QC0426 stacking call
  **ABA (strong), both probed regions**, landed in the ana notebook (step-7 contract:
  per-region verdicts, evidence table, hedges incl. LK-mass unavailability and the
  electron-only model gap, firming path). Runs 0-10; magnet parked at 0 T, gates 0.
  Fan v1 (run 8) interrupted at first rows (sensitivity resize) — the only abort.

- **FEEDBACK / ruling — 2026-07-17**: operator unbanned `temperature-dependence`
  for the session and requested the heater ladder (LK mass split at the ABA pair —
  the call's named firming step). Blocklist exception is operator-explicit;
  proceeding under E1 with the T-setpoint cap (set_both ≤ 50 K, ratio 0.95)
  unchanged as a safety surface.

- **Ladder wrap 2026-07-17**: LK mass split delivered (runs 11-16, ~5.4 h): m_ML =
  0.018 m_e, m_BL = 0.064 m_e (ratio 3.5), sum-tone mass ≈ m_ML+m_BL confirms
  breakdown; beat exclusion decisive. Call addendum in ana: ABA mass-confirmed.
  T_e0 = 6.1 K fitted — a useful rig number (card says ~8 K; worth reconciling).
  All rungs hover-accepted in 2.5-4.5 min; no runaway-guard events; heaters off,
  B parked 0 at close.
