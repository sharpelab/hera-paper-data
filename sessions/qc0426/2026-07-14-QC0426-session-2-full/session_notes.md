# Session notes — QC0426 / VTI

Operational log (not a science notebook).

## 2026-07-14 — autonomy grant
- **E1 GRANT** — operator (Zack) said "go for autonomy" at 2026-07-14 ~20:4x local,
  after session-start VERIFY closed green (measure cell 28, exec 15) and SAFETIES
  verified against the device card (measure cell 18, exec 10). E1 engaged per the
  session brief; first E1 execute is the read-only kernel-binding probe.
- TOOLING — partial (in-flight) run TSVs carry no header row (header lands at
  completion): mid-run reads must use positional columns or `hera-watch` digests.
  Also `run.col()` raises on duplicate columns when a swept param is also fp'd
  (k_2400_tg_volt at indices [1,3]) — use col_indices/col_at; fine once known.
- TOOLING — hera-watch 2D digest labels the slow axis "None" for megasweep runs
  (run 4: `row 0/61 None=-3`); slow-param name resolves fine for 1D sweeps.
  Cosmetic, but the slow-axis value is the only per-row coordinate in the digest.
- RECIPE FIX — gatemap.md carries toploader-era pricing ("201x201 ~ 3.5 h");
  on the VTI the same map is ~24 h at the 4-tau floor. Rig-card timing wins;
  measured this session: 1D 2.13 s/pt at delay=1 (runs 0-3), 2D 1.52 s/pt at
  fast_delay=1.2 (run 4, 39.4 rows/min) — 2D per-point is *cheaper* than 1D
  here (row-batched readback), opposite of the rig card's 2.0-2.5 s/pt 2D band.
- TOOLING — hera.analysis.sdh_onset returns onset_b=nan when the record's
  oscillatory band is narrower than win_invB (default 0.18; run 5) and when
  multi-tone content flips its consensus tracker (run 6 sr1). Narrowing
  win_invB to 0.10 recovered a clean onset from run 6 sr2. Worth a docstring
  note or an adaptive window.
- RECIPE FIX — sdh-spot-check.md: sdh_fft signature is (R_grid 2D (n_B, n_fast), B)
  and returns (freqs, spec[n_fast, n_freq]); a 1D trace must be passed as
  R[:, None]. The recipe's step-5 text reads as if 1D R is accepted.

## 2026-07-15 — campaign outcome (operational summary)
- Arc completed autonomously overnight: gate C (runs 0-3) -> gatemap + CNP cal
  (run 4) -> SdH spot checks both signs (runs 5-6) -> D=0 electron fan (run 7)
  -> region-resolved call (ana): ABA strong on both Rxx regions, ABC excluded,
  f_top origin left as an explicit fork. Zero aborts, zero safety events;
  actuals: gatemap 3.1 h (est 5-5.5), spot checks 1.8 h each (est 1.5-1.7),
  fan 3.8 h (est 5.5-6.5) — 2D per-point on this rig runs *under* the 1D
  rate; rig-card Timing should split 1D vs 2D per-point explicitly.
- RECIPE FIX — trilayer-stacking-fs-count.md: the intermod-at-F_L degeneracy
  (an ABA pair's mixing tone lands exactly at F_L, mimicking the ABC singleton)
  deserves explicit text in Why/Verify, plus the magnetic-breakdown candidate.
  Amplitude-systematics (B-window split) worked as a cheap partial discriminator.
- RECIPE FIX — sdh-spot-check.md/landau-fan.md: on high-T_e rigs the usable
  1/B record above onset, not the field cap, sets dF — worth a line making
  dF = 1/(1/B_onset - 1/B_max) a first-class design number (it drove the
  side choice and the fan value here).
- **E0 DROP** — operator withdrew the grant for session wrap-up (2026-07-15
  ~morning). Autonomous execution ends; E1 resumes only on explicit re-grant.
- FEEDBACK — Aaron (via Zack): the uniform-1/B spot-check collection "looks
  like shit" on the data-collection side. Discussion + redesign below /
  in-chat; candidate RECIPE FIX for sdh-spot-check (VTI variant).
- RECIPE FIX — sdh-spot-check (VTI delta, validated run 9 vs run 6): collect
  UNIFORM IN B with dB = d(1/B)_Nyq * B_lo^2; sdh_fft resamples internally.
  Same wall-clock, ~30x per-period averaging at high B, no blind ramps,
  cleaner spectra; also hardens tones against alias readings (grid-change
  reproduction). Retires uniform-1/B collection on blocking rate-limited
  magnets. Origin: Aaron's collection-side complaint via Zack.
- **OPERATOR RULING** (Zack, 2026-07-15 wrap-up): temperature-dependence
  unblocked for this session — enablement work done on the rig side.
  Vaporizer loop now works as commanded (historical vaporizer-probe/needle-
  valve issues addressed); heater.set_both(T, ratio=0.99) is the sanctioned
  method; ranges authorized up to 50 K. Supersedes the rig card's
  "vaporizer is operator-only" for commanded set_both use — RIG CARD UPDATE
  candidate for triage.
- **E1 RE-GRANT** (Zack, 2026-07-15 wrap-up): "go to E1 ... proceed with the
  validation, measurement and analysis" — scope: thermal validation Cell A
  (measure 54), LK ladder Cell B (measure 56), analysis. Per standing rulings:
  set_both <= 50 K Auto; temperature-dependence unblocked. Instructed to ping
  + drop to E0 if anything is needed.
- Self-correction (E1): ladder v1 aborted at rung 1 — the vaporizer-overshoot
  assert was up-leg-only (fired on legitimate cooling from 50 K). finally
  worked (heaters off, gates parked). v2 (measure cell 58) uses a directional
  runaway guard. PROTOCOL note: settle-verify guards must be direction-aware
  when a ladder descends.
- TOOLING/RIG CARD — measured: the lakeshore worker writes the VTI temperature
  logfiles on a ~30 s cadence. Freshness guards must allow >= 2-3 periods
  (90 s used); a 30 s threshold false-fires at cadence. Ladder v2 abort was
  this; v3 running. Rig card's thermometry section should state the cadence.
- PROTOCOL/RECIPE — descending T rungs on the VTI: with set_both held, the
  sample cools passively toward the vaporizer setpoint (measured tau ~27 min
  at 34K->25K) — ~2 h/rung to tolerance. Heating catches are 2.5-4 min.
  Correct pattern (ladder v4): heaters OFF through the descent, catch at
  target-0.2 K, set_both lifts and holds. temperature-dependence recipe
  (VTI variant) should encode this asymmetry.
- PROTOCOL/RECIPE — VTI sample-loop PID is untuned (driver TODO confirmed
  live): post-step overshoot ~+1.4 K then bath-limited relaxation
  (~0.015 K/min). Tolerance-settling cannot pass below ~20 K. Ladder v5 uses
  hover acceptance (spread < 0.1 K / 90 s within [nom-0.5, nom+3]); the fp'd
  per-point T is the LK fit axis, rung labels nominal. temperature-dependence
  VTI variant should adopt hover acceptance until PID is tuned; rig card
  thermometry section should state the overshoot figure.
- LK ladder complete (runs 10-17, 8 rungs 26.6->1.27 K measured). Final call
  updated in ana (cells 34-36): T3-T4 pure ABA strong (m_top = m_s+m_B ->
  breakdown/intermod); B4-B5 ABA + ABC minority domain moderate (m_top 0.056
  distinct from sum 0.094). T_e0 unconstrained <= ~8 K (masses too light to
  probe). Model TODO: fs_count_b0 should emit band masses at E_F for the
  ML/BL labeling check (measured m_s ~ m_B, not the naive light/heavy split).
- RECIPE FIX — temperature-dependence (VTI variant): encode hover acceptance
  + descend-catch + the whole guard set from ladder v1-v5 (this session's
  worked example: measure cells 56-60).
- Session hardware end-state (2026-07-16 ~04:40): B = -0.0002 T, gates 0/0/0,
  heaters off (ranges 0,0), T = 1.181 K. 18 runs (0-17), zero interrupted.
  E1 idle; both campaign questions answered (stacking call + LK fork).
