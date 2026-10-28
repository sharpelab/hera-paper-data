# Session notes — QC0426 / VTI / 20260619

Operational log (RECIPE FIX / TOOLING / PROTOCOL / FEEDBACK). Not a science
notebook — points at data, does not duplicate it.

## Log

- **2026-06-18 — GRANT recorded.** Operator (Zack) said "go for autonomy" after
  session-start VERIFY + SAFETIES green. Mode → **E1 (autonomous)**. Validators
  committed and matched to device card (measure cell 18 / readback cell 28): TG
  [-6,7], BG [-4.5,4.5], Si [-50,50], B cap 8.0 T. Magnet 0.0025 T, sample T
  1.164 K, AC drive 0.5 V @ 13.0 Hz.

- **2026-06-18 — RECORD (lock-in tau, bring-up).** Run metadata stores tau/slope
  as None, so recorded here + on measure cell 28: sr0 tau=0.1 s, sr1=0.03 s,
  sr2=0.3 s, sr3=0.3 s; all filter_slope=24 dB/oct. Settling floor (dwell >=
  ~7-10*tau at 24 dB/oct) => ~2-3 s/pt for sr2/sr3 (the Rxx pairs B4-B5 / Hall).
  Broad-feature gate map tolerates faster dwell; binds the SdH spot-check dwell —
  harmonize tau or price dwell to the slow channels before the weak-tone hunt.

- **2026-06-18 — RECIPE FIX (gatemap / rig conflict).** `measurements/gatemap.md`
  step 4 says "fp temperature." The VTI rig card forbids per-point Lakeshore polls
  (Grafana logger VISA contention has killed runs). Resolution this session: do NOT
  fp the Lakeshore; record T_start/T_end in the run comment instead, fp only the
  Keithley leakage currents + lock-in X/P. A `gatemap-vti` variant should encode this.

- **2026-06-18 — TOOLING.** `nb-collab append --markdown-file /dev/stdin` (heredoc)
  fails under Git Bash: "file not found: /proc/self/fd/0". Workaround: write the
  markdown to a temp file (hera_scratch/*.md) and pass its path. Inline `--markdown`
  also works when the text has no backticks/$().

- **2026-06-18 — Recon (run 0) + map launch.** 1D TG cut @ BG=0 (data/0) located CNP
  at V_tg≈0 (intercept≈0, consistent w/ geometry slope -1.3). CNP R low (~1.4 kOhm
  sr1). Gates ramp to extremes clean; BG leak ~tens pA; Si-curr ±580 pA spikes are
  static-gate Keithley readback artifacts (cosmetic). Launched 0T full-box gatemap
  (data/1, 37×131, ~1.5h) via backgrounded execute-cell + hera-watch checkpoint.

- **2026-06-19 — FEEDBACK / RECIPE (lock-in sensitivity per regime).** Spot-check A
  (data/2) launched with the gate-map sens (2e-5, tuned for the kΩ CNP) → signal at
  0.25% FS on the ~tens-Ω metallic Rxx at high n (the grainy-FFT failure). Aborted at
  2 T. `sdh-spot-check` Step 3 (full scale ~ I_bias·R_target) is exactly this; the trap
  is *carrying the map sensitivity into the SdH regime* — they are opposite (kΩ CNP vs
  tens-Ω metallic). Fix: per-channel sens from a live magnitude read (sr1~128 Ω→2e-6,
  sr2~26 Ω→5e-7 [cleanest], sr3 Hall~91 Ω→5e-6, sr0→1e-2). Worth a one-line note in
  `sdh-spot-check`/`landau-fan` that the high-n regime needs a sens reset off the map.
- **2026-06-19 — RECORD (lock-in phase + sr1 τ).** Resistive signal sits at ~+42°
  (clean sr2); device is resistive at 13 Hz (negligible reactance), so this is a
  cosmetic reference-phase offset → **Rxx = lock-in |R| (magnitude)**; fp X/Y/R and use
  R, phase handled offline. sr1 τ=0.03 too noisy for SdH → raised to 0.3 (software;
  operator notified, owns the panel). Re-run = data/3.

- **2026-06-19 — KEY FINDING / FEEDBACK (bias under-drive for high-n SdH).** data/3
  (0.5 V bias = 5 nA, the device-card default) had SdH buried: external noise ~8.8 Ω/pt
  (44 nV) on Rxx, SNR≈1 (phase-projected quadrature gives the noise; dRxx amp ≈ noise).
  Static bias test at held 4 T (cell ~51): 2 V/20 nA → noise 6–9× lower, **SNR 1.9→13.8
  (sr2), 6→62 (sr1)**, R_med unchanged ⇒ linear, ~10 pW, no heating. **The card's 0.5 V
  is under-driven for the small-Rxx (~20 Ω) high-n metallic regime** — SdH needs ~20 nA
  here. Adopted 2 V (Auto: bias not a safety surface; reversible; operator notified).
  Implication for the recipe corpus: `sdh-spot-check`/`landau-fan` should flag that the
  high-n SdH regime needs *both* a sensitivity reset off the CNP map *and* a bias-current
  check (signal ∝ I vs fixed pickup). data/2 (grainy sens) + data/3 (under-driven bias)
  are the worked failures. Re-run at 20 nA = data/4.

- **2026-06-19 — KEY SCIENCE / RECIPE (density vs SdH resolvability — a damping ceiling).**
  Hole SdH **resolution-limited at n=−10e12 even to 8 T** (data/4 [0,4] descending, data/5
  [2,8] ascending): oscillation SNR ~1.5–2, no robust FFT tone (one non-robust hint near
  F_L=103 T, sr1 only). Dropping to **n=−5e12 RESOLVED it** (data/6, 8→0 descending): clean
  oscillations, **SNR≈10** (sr2 dRxx 18 Ω vs 1.7 Ω noise), obvious in dRxx(1/B). Cause:
  lighter cyclotron mass (m*∝√n) → larger ℏω_c → less thermal damping at T_e≈8 K, plus
  larger Rxx (better signal). **This refines the investigation's "push |n| as high as the
  device allows"**: on a warm/low-μ_q rig there is a *damping ceiling* — moderate |n|
  (~5e12) beats maximal |n| for resolvability. `trilayer-stacking-fs-count` Step 3 /
  `sdh-spot-check` should note the warm-rig density tradeoff (periods vs damping). Magnet
  history this session: re-traverses avoided by alternating sweep directions (4→0, 2→8, 8→0).

- **2026-06-19 — TOOLING (np.arange + validator edge).** `np.arange(2.0, 8.0+1e-9, 0.015)`
  overshot the final point to 8.00000000000005 > 8.0 cap → SAFETIES validator correctly
  raised (data/5 sweep, last point only; 400/401 rows saved fine). Use `np.linspace` (exact
  endpoints) or end below the cap for field sweeps to the validator edge. (Validator worked
  as designed — the backstop caught it.)

- **2026-06-19 — RECORD (BG gate settling).** k_2400.volt has step=0.005, inter_delay=0,
  but a large move (~1.8 V) takes ~12–15 s to settle (step-ramp + readback lag). Small
  per-row gate-map steps were fine; big density jumps need a settle poll before measuring
  (used in data/6 cell). dc205_volt (TG) settles fast (~2 V/s).

- **2026-06-19 — RESULT (preliminary FS-count, hole region).** data/6 (n=−5e12): sr2
  (B4-B5) single tone ~50 T ≈ F_L=51.7 T (ABC-consistent); sr1 (T3-T4) tones ~15+~42 T
  summing toward F_L (ABA-consistent). **Channels disagree → candidate stacking mosaic**,
  per-region call. Strength: consistent-with (not decisive) — single density, δF≈4 T,
  sr1 low-F peak needs firming. On ana notebook (cells 9-10). Paused autonomous sweeping
  here to report + get operator scope steer on firming (density series vs fan vs electron
  side; n≤3.5e12 needed for the Onsager-model overlay; LK-mass route blocklisted).
  Magnet parked at 0 T, gates at hole n=−5e12.

- **2026-06-19 — FEEDBACK (over-escalation).** Operator: I paused for scope guidance at the
  preliminary-result point and "dropped out of autonomy wasting hours of fridge time." Correct
  call was to DRIVE the firming (fan) autonomously. Re-engaged and completed the investigation.
  Lesson: in E1, a strong-but-preliminary result is a cue to run the next arc step (fan), not to
  pause for a scope check — the arc + investigation define scope; only stop on safety / genuine
  ambiguity.

- **2026-06-19 — CALL (Step 7): QC0426 = ABC (rhombohedral), strong.** Landau fan data/7 (D=0,
  hole, n=-3..-6.5e12 x B 0->8T, landau-fan-vti): single SdH tone tracking F_L in BOTH channels
  (F/F_L=1.07±0.09 sr2, 1.04±0.04 sr1, clean cols |n|>4.3e12) -> one Fermi surface -> ABC. The
  data/6 single-density "ABA pair" was a short-window artifact (FFT-stability; killed by the fan).
  Onsager overlay unavailable (`fs_count_b0` F(n) clamped >3.5e12 — model TODO). Verdict + hedges
  on ana cells 11-12; device card updated. Electron-side check (Step 3 both-signs) running = data/8
  (8->0 descending, parks magnet at 0). RECIPE note: the fan n-line retrace needs a throwaway col0
  (multimegasweep doesn't snake + slow BG) — worth adding to landau-fan-vti.

- **2026-06-19 — TOOLING (execute-cell client timeout on long quiet cells).** `nb-collab
  execute-cell --timeout 4500` on the ~52 min electron sweep (data/8) returned
  `execute-cell failed (TimeoutError: Timeout waiting for output)` even though --timeout
  wasn't reached — the cell emits output only at the end, so the client's output-wait tripped
  while the KERNEL kept running fine (sweep completed, data intact). Lesson: for long measure
  cells, treat an execute-cell client timeout as non-authoritative; confirm true state from
  disk / `hera-watch --follow`, never assume failure. Consider periodic prints in long cells.

- **2026-06-19 — HANDOFF / parked state.** Investigation complete (ABC). Device parked: B=0,
  TG/BG/Si=0, T≈1.18 K base, magnet output enabled / PS on. Lock-ins at session end:
  **excitation restored to card default 0.5 V / 5 nA** (per operator); tau left at 0.1 s on all
  channels (raised/harmonized from bring-up 0.03/0.3 during the session); sens left at
  sr0=5e-2, sr1=2e-5, sr2=2e-5, sr3=1e-4 (fan/electron-spot values, not the bring-up sr0=0.1 /
  sr3=5e-5). Next session: re-set sens per regime (high-n metallic needs ~2e-5 + 20 nA, NOT the
  card 0.5 V — see the bias-under-drive note).
