# Session notes — QC0426 / vti

Operational log (not a science notebook).

## 2026-06-21

- **E1 GRANT** — operator (Zack) said "go for autonomy" at session start, after
  Gate A (instruments alive) and Gate B (SAFETIES committed = device-card limits,
  B cap 8.0 T) were green. Bring-up state: magnet 0.003 T, sample T 1.16 K, all
  instruments connected (measure exec [1]->[14], clean single run-through). Engaging
  E1; first execute = read-only kernel-binding probe (measure cell 28).

- **CAL ESTABLISHED — Run 0** (`data/0`, gatemap, measure cell 34). 0 T TG–BG
  map located the CNP cleanly: `V_tg = −1.306·V_bg + 0.225`. sr1/sr2 agree to
  0.2%, ratio 1.306 matches geometry prior 1.300 to 0.5%. Calibration written
  to device card + ana notebook (cells 10–13). Gate C (contact liveness) passed
  at the start. Analysis in `hera_scratch/cnp_analysis.py`. Next: SdH spot
  checks (investigation Step 3). Run priced 34 min vs 35 min actual (+3%).

- **RECIPE FIX — sdh-spot-check / field-sweep-1d (and gatemap)**: recipe Step 4
  says "fp the temperature(s)". On the **VTI this is forbidden** — the LS335 has
  two masters (Grafana logger + measurement kernel) and per-point Lakeshore
  polling has killed a run (rig card "Known quirks"). I record T once in
  `meas_config` instead and do NOT fp `heater.sample_temperature`. The
  rig-agnostic recipes should carry a "VTI: do not fp the Lakeshore" note or a
  `-vti` variant.

- **RECIPE FIX — sdh-spot-check (sensitivity vs MR)**: Run 1 (hole n=-3e12,
  D=0, 2V/20nA) **clipped sr1/sr2 above B≈2.76 T** — they railed at 546 Ω
  (1e-5 FS) while true Rxx climbs to ~1920 Ω at 7.9 T (strong, super-linear
  MR). The clip killed the high-field/high-SNR SdH and the FFT was muddy. The
  recipe's "set sens so FS ≈ I_bias·R_target" must use **R at B_hi (MR-inflated),
  not the low-field R** — at 20 nA over 0.2→7.9 T the dynamic range is ~30×
  (65 Ω → 1920 Ω), so a single sens must be set from the high-field end (1e-4
  here). Recipe should add: "for a strong-MR device size sens to R(B_hi); the
  low-field signal will sit at a few %FS — acceptable, the high-field SNR is
  what matters." Re-run (Run 2) descending 7.9→0.2 T at 1e-4 (traverse-free,
  field already up). Onset/low-field detail preserved from Run 1's finer range.
  Hint from Run 1 clean window: sdh_onset consensus ≈ 9 T and a possible
  9+22≈F_L(31 T) pair — needs Run 2 to confirm.

- **RESULT — hole SdH (Run 2, data/2)**: clean, onset 0.31 T. **Hall slope
  confirms density** n_Hall=2.96e12 vs gate 3.00e12 (1.3%) → F_L=31 T solid
  (lever-arm upgrade candidate — see below). FFT: robust tones ~11.8 & ~16 T
  (sr1+sr2 agree) + weaker ~30 T + harmonic ~34 (=2×16); low-F ~4 T is MR-bg
  artifact. **≥2 Fermi surfaces → simple ABC disfavored, ABA-leaning, NOT
  decisive** (rich spectrum, harmonic-vs-pocket ambiguous at one density).
  Forward model @3e12: ABA [1.5,29.5], ABC [31] — exact freqs param-dependent;
  count+Luttinger-sum are the robust read. Recorded ana cells 14-16.
- **CAL UPGRADE candidate**: the low-field Hall slope (n=2.96e12) independently
  confirms the geometry-prior absolute scale to ~1.3%. Device-card (n,D) scale
  can be upgraded from "geometry prior" toward "Hall-confirmed" — will firm with
  the QH lever-arm (ray slopes dn/dB=νe/h) from the fan.
- **PLAN**: electron-side spot check next (Step 3), then the Landau fan for F(n)
  (Step 4/5 partition robustness — the decisive test). Also need: locate D=0
  (D_offset unexamined) and LK mass (temp-dep, blocklisted this session — flag
  for operator).

- **RESULT — electron SdH (Run 3, data/3) + Step-3 conclusion**: electron side
  lower quantum mobility (onset 1.5 T vs hole 0.31 T), short record, FFT peaks
  wander → dominant ~30.6 T ≈ F_L (cleaner at cut 1.5: 30.4 dominant + 22.4).
  Hall n=3.30e12 (gate 3.0; +10%, mild e/h asymmetry). **Both sides show a
  ~30 T (≈F_L) tone; hole side additionally has robust ~12 & ~16 T → ABC
  disfavored, ABA-leaning, NOT decisive.** Recorded ana cells 17-19.
  **Step 3 done: cleaner side = HOLE** (onset 0.31 T). LK-mass route blocked
  (temp-dep blocklisted).
- **PLAN — Landau fan (Step 4, the decisive F(n) test)**: per-column SdH-FFT
  fan, hole side, D=0. Magnet at 7.9 T (Run 3 end) → fan DESCENDS 7.9→0.31 T
  (no re-traverse). Cost (VTI measurement-dominated, ~1.4-2.0 s/pt): a
  Nyquist-sampled fan to n_max≤3.5e12 is ~15-20 h; trimming n_max→2.5e12 and
  reading n=3e12 from the spot check (per recipe) gives ~10-13 h. Key design
  knots: B-Nyquist Δ(1/B)≤1/(3·F_L(n_max)); single fixed sens sized for the
  low-n×high-B worst corner (high R) — big dynamic range; B_lo=onset=0.31 T.
  Telegraphed to operator; design + launch next tick.

- **RESULT — Landau fan (Run 4, data/4) + STACKING CALL**: 250×100, B 7.9→0.3T,
  n=-0.7..-2.5e12, D=0, 11.0h, clean (no clip, no streak, 20nA steady). F(n):
  a **dominant SdH tone tracks F_L(n)** across the fan (dom/F_L median 0.95) →
  one Fermi surface carries the full Luttinger density. Sub-F_L structure
  present (fan F_L/2-ish w/ ~2:1 to F_L; spot-check 11.8&16T at 3e12). Streda
  LL-filling inconclusive (no clean integer-ν ladder).
  **CALL (sr1/sr2 region, ana cells 20-22): ABA (Bernal) — WEAK** / ≥2 FS
  indicated → simple ABC disfavored, ABA not decisive, spin-split-ABC not
  excluded. Binding limits: ML partner (~1-2T) below resolution (MR-bg artifact
  <6T); **LK-mass test blocklisted (temp-dep)**; D_offset unexamined.
- **FIRMING (operator decisions needed)**: the single most decisive remaining
  test is **LK effective-mass at the two frequencies → temperature-dependence,
  which is BLOCKLISTED this session**. Recommend operator unblock temp-dep
  (Flavor B) next session. Also: low-F-resolved ML-partner hunt (better bg
  removal on existing Run 2, or a dedicated finer-low-F spot check); locate D=0;
  uniform-B Streda fan for the high-field Chern complement.
- **END STATE**: gates parked 0,0; field 0.3T; sens 2e-3, 2V/20nA. Decisive
  measurement (fan) DONE + analyzed. Holding from new measurements pending
  operator steer (esp. unblocking temp-dep for the decisive LK-mass test).

- **TOOLING — hera-watch ETA on uniform-1/B sweeps**: the row-rate ETA is
  optimistic early (low-field rows are fast/dense, high-field rows are
  ramp-limited and slow). Run 1 showed "ETA 6m" at row 380 but took ~45 more
  min. Judge remaining time by the field span left, not the row ETA.

- **TOOLING**: `hera-watch data --next --follow` + backgrounded
  `nb-collab execute-cell --timeout` is a clean E1 long-run pattern — the watch
  digests rows live (gain-divided, ETA) and both tasks notify on completion.
  Worked first try.
