## HERA — Step 4: Landau fan (`landau-fan-vti`), electron side, D = 0, n = +1.6 → +3.2×10¹², B 1 → 10 T

**Why the electron side, and what the spot checks already say.** Runs 6/7 are read in
the ana notebook; the design inputs are: at **n = +3.2×10¹² (run 6)** the FFT over
1.0–10 T carries three stable tones — **7.05 / 22.90 / 29.94 T** (stable across
`bg_degree` 3–7 and every cutoff from 0.8 to 2.5 T, SNR 100 / 51 / 116) — plus a
difference tone at 15.85 T and sidebands at 36.99 / 51.1 / 59.9 T. F_L(3.2×10¹²) =
33.09 T. The arithmetic that matters: **7.05 + 22.90 = 29.94 T exactly**, and
29.94/F_L = **0.905** — a single global density rescale well inside the lever-arm
prior band (0.8–1.2), our c_tg being a 9.5 nm geometry prior. On that one scale the
pair partitions **0.235 / 0.765** against the ABAB decomposition-limit 0.28/0.72, and
the model's own F(n) table at this density (7.5 / 25.6 T, rescaled 6.8 / 23.2 T)
lands on the observed pair. So the electron-side spot check already leans **ABAB with
the F_L tone as the symmetry-allowed breakdown/sum tone** — which is exactly the call
the investigation forbids making from one density: a competing decomposition reads
7.05 and 15.85 as the fundamentals with 22.90 as their sum, and that one needs a
0.692 rescale (red flag, outside the band). **Only n-dependence separates them** — a
real pocket follows its own Onsager curve, a combination tone stays an algebraic
combination at every n. That is this fan. Run 7 (hole, n = −1.2×10¹²) is excluded as
the fan side: TG-limited to |n| ≤ 1.27×10¹², i.e. inside the investigation's
near-CNP exception regime where the pair is close and balanced, and its spectrum is a
harmonic comb (tones flagged 4×, 7×, 11×, 16× of 7.1 T) — a preview, not a claim.

**Design numbers** (`landau-fan` step 1 cost-floor procedure, each lever at its floor):

- **B_lo = 1.0 T — measured, not eyeballed.** `sdh_onset` on run 6 returns the record
  edge (censored) carried by the 7.3 T tone, so a Dingle extrapolation of each tone's
  SNR(1/B) track gives the real numbers: the **heavy tone crosses SNR = 5 at 1.39 T**
  and the **F_L tone at 1.58 T** (measured onsets 1.40 / 1.76 T). Rows below 1 T can
  therefore only carry the light tone, at B_lo²-scaling row cost — so the recipe's
  "cheap low-field extension" would buy nothing for a *pair* read, and is skipped on
  that evidence rather than on convenience. Run 6's sub-1 T leg was 50 mT (f_Nyq
  6.4 T there) and is not usable for the fast tones at all.
- **B_hi = 10 T** (session cap). Uniform-1/B makes the 5→10 T half cost only **10 of
  the 145 rows**, and it is where the F_L-tone origin test lives (a breakdown tone
  strengthens with B; a real pocket keeps its own Dingle envelope).
- **Δ(1/B) = 1/160 T⁻¹ → f_Nyq = 80 T, N_B = 145.** Nyquist on F_L alone (1/(2·33.1))
  is *not* enough here: run 6 carries coherent harmonic content to ~118 T, and at
  f_Nyq = 50 or 60 T the 90.5 T harmonic folds to **9.5 / 29.5 T** — straight onto the
  light and F_L tones. 80 T is the cheapest choice that folds nothing identified below
  118 T into the 3–40 T classification band. Coverage trade, stated: content in the
  123–157 T comb (≤ 8 % of the main-tone amplitude) does fold in; those folds are
  identifiable because an alias' frequency moves **downward** as n rises, and run 6 is
  the fine-grid reproduction reference at the top column. Buying them out (f_Nyq =
  100 T) costs +36 rows ≈ **+1 h** and is not worth it at 8 %.
- **Both-axis Nyquist.** B-axis: uniform-1/B gives a *constant* **4.8 rows per LL
  period at n_max** and 9.7 at n_min (floor 2, prefer 3) — no high-n corner to
  undersample, which is the 2026-06-14 uniform-B failure mode. n-axis: Δn = 0.040×10¹²
  = **2.4 points per LL ray spacing** (0.0967×10¹²) at B_lo = 1.0 T. Resolution
  δF = 1/(1/1 − 1/10) = **1.11 T** against a 7→23 T split, i.e. 14 δF.
- **n = +1.6 → +3.2×10¹², 41 points.** n_max is gate-limited (V_tg +0.9836, 16 mV
  under the limit — the same point as run 6, so the top column reproduces it). The low
  edge is set by partner resolvability: periods = f_light × 0.9 falls to **3.3 at
  n = 1.6** and below 3 under it, so columns below 1.6×10¹² cannot carry the partition
  and are excluded by design (including down to 1.0×10¹² would cost ~15 columns ≈
  +50 min of uninformative data). The window is a factor-2 in density — enough for the
  F(n) trajectory that Step 5 and the adjacent-N dual overlay need.
- **Dynamic range, worst corner = low n × high B.** R(B = 0, n = 1.6×10¹²) = 84 Ω
  (run 5) × MR ≈ 10–12 (run 6: 530/52 Ω at n = 3.2) + SdH maxima ≈ **1.5 kΩ = 30 % of
  the 5 kΩ full scale** at sr1 50 µV, fixed for the whole fan. Headroom, not precision
  — and a `rail_guard` kills the run at 0.95 × FS, since a flat-topped column is
  unrecoverable for the FFT.
- **Settling.** τ = 0.3 s at 24 dB/oct. `fast_delay = 1.8 s` = 6τ, the recipe's number
  for a per-column-SdH-FFT fan; `slow_delay = 3.0 s` = 10τ after each flyback, so the
  first column of every row is fully settled rather than carrying the flyback step.

**Price — from this session's own timing, not inherited constants.** The model
(per-point = `fast_delay` + 0.10 s at NPLC 1; magnet set = ramp + 3.0 s settle; bare
ramp 0.137 T/min) reproduces run 5 (81.0 vs 81.1 min), run 6 (120.6 vs 120.3) and run
7 (95.9 vs 95.6) to **under 1 %**. Here: 5945 points → grid 3.14 h + row turnaround
0.26 h + 9 T traverse 1.09 h = **4.5 h**, called at **4 h 45 m**.

**Preconditions the cell asserts** (state it assumes but does not set): thermometry
logfile advancing and T_sample 1.0–1.5 K; magnet at or below the fan start field (it
refuses to start if something left the field high — no re-traverse); V_si = 0;
Keithley NPLC 1/1; PS heater on and output enabled; and all three SAFETIES validators
still reading the device card's limits.

**Checkpoints** (`hera-watch` armed on the run dir before the cell starts):
(1) **first 3 rows, ~15 min in** — leakage against the 1 nA trip (runs 6/7 peaked at
2.2 × 10⁻¹⁰ A), no railing, sr1/sr0 alive and not flat, T holding, field readback
tracking the setpoints, and R at the top column matching run 6 at B = 1 T; abort here
if any fail. (2) **row ~72, B ≈ 2 T, ~2 h in** — per-column FFT on the landed rows
(1/B span 0.5, δF 2.0 T): the heavy and F_L tones must already be separating at the
high-n columns, as run 6 says they do. If the top columns show no tone structure by
B ≈ 2.5 T the disagreement with run 6 is instrumental, not physics — abort and
re-check the configuration rather than spend the remaining 2.5 h.
(3) **row ~110, B ≈ 4 T** — δF 1.33 T; first honest look at the n-dependence of the
15.85 T tone, the fork this fan exists to settle.

**Ends at B = 10 T with the gates parked at 0 V** — deliberate, not drift: the LK mass
split (`temperature-dependence-vti` Flavor B, the investigation's Verify and the next
step) rides the magnet back down instead of re-traversing.
