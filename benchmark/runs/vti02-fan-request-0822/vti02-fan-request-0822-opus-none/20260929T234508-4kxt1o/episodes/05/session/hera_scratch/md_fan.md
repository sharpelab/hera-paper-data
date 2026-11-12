## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — n = −1.20 … +3.20×10¹², B 1 → 10 T

**Why this, now (plan step 4).** The spot checks settled feasibility but not the
question. Run 6 (n = +3.2×10¹²) shows a ~7.1–7.5 T tone plus a ladder at
14.1 / 22.2 / 29.5 T that `sdh_onset` reads as *its harmonics*, and a 4–10 T
window peak at 33.3 T ≈ F_L(full density) = 33.1 T; run 7 (n = −1.2×10¹²) shows
12.3 T ≈ F_L = 12.4 T plus 3.4 / 4.7 / 6.6 T. Both records fit **either** one
Fermi surface carrying the full density with a harmonic ladder (→ ABCA) **or**
two independent surfaces partitioning it ~0.23/0.77 (→ ABAB/ABCB). A single
density cannot separate those: a harmonic has slope exactly k × dF₁/dn, an
independent surface does not, and independent tones must sum to n·h/4e. **The
fan measures the slopes.** Each of the 111 n-columns gets its own 1/B FFT
(`sdh_fft`), and each row additionally gives the LL period in n (= 4eB/h) as a
degeneracy cross-check.

**Design.** Fast axis is (V_tg, V_bg) co-swept along the run-5 D = 0 line
(|D| ≤ 1.4×10⁻⁶ V/nm across the row), n = −1.20 … +3.20×10¹² in 0.04 steps —
the full width the validators allow on that line, both carrier signs, so the
electron/hole asymmetry (the ABCB tell) is in the same run. Slow axis is B,
**ascending 1 → 10 T, uniform in 1/B** (d(1/B) ≤ 0.0102 → F_Nyquist 49 T,
above the 33 T we need to resolve; ΔF resolution 1.11 T), with any gap wider
than 0.4 T bisected so the high-B end is still legible as a map — 98 rows. The
magnet starts at 0 and only ever goes up: the 9 T traverse is recorded as data,
not spent as a bare ramp, and the run ends at 10 T where the next step (LK mass
ladder, plan step 5) would start.

**The dwell is a sweep-rate ceiling, not a settle rule.** `sr1` is τ = 0.3 s at
24 dB/oct — a 4-pole filter, so on a gate fast axis it averages Rxx over
σ_n ≈ 2τ·(dn/dt) in density. Washout sets in when σ_n approaches the LL period
in n, Δn_LL = 4eB/h, which is smallest at the lowest row. `fast_delay = 2.30 s`
puts σ_n = 0.0103×10¹² against Δn_LL(1 T) = 0.0967×10¹² → **80 % amplitude
retention on the bottom row, 95 % at 2 T, 98 % at 3 T**. This — not the point
count — is what sets the 4.3 min row time; 111 fast points are then nearly free.
The same filter lags features in n by ≈ 4τ·(dn/dt) ≈ 0.03×10¹² (under one n
step): a rigid shift in one sweep direction, which leaves every F(n) *slope*
— the actual discriminator — untouched, and is calibrated out against the
run-5 CNP.

**Coverage trade, stated.** Not covered: any D ≠ 0, and B below 1 T. Below 1 T
the rate ceiling above would force a proportionally slower row (row time scales
as 1/B_lo), so 0.7 T would cost ~+4 h for ΔF 1.11 → 0.78 T — not worth it when
the slopes, not the single-point resolution, carry the call. `sr1` τ is
operator front-panel and stays as set: dropping it to 0.1 s would legitimately
cut this run to ~4 h with no rejection penalty at 13.777 Hz — say the word and
I will re-land it that way.

**Preconditions the cell checks (assumed, not set):** T_sample 1.0–1.5 K,
|B| < 0.05 T, V_si = 0, gates at 0 after the handoff, PS heater on / output
enabled, thermometry logfile advancing, and the SAFETIES validators still equal
to the committed limits. Sensitivity is fixed at 100 µV (≈10.1 kΩ full scale at
10 nA) — the run-5 proven headroom; runs 6/7 peaked at 0.59 kΩ off the CNP, and
it is the near-CNP columns at high B that can clip. Clipping is counted and
reported, not aborted on. Gate leakage aborts only on **3 consecutive** points
over 1 nA (single-point flyback transients of ±200 pA are known and must not
kill a 9 h run).

**Checkpoints (`hera-watch` digests).** (1) First 2 rows, ~12 min in: signal
level, no rail, leakage, T, and R(n) at 1 T reproducing the run-5 CNP position.
(2) ~2.5 h in (B ≈ 1.35 T, ~30 rows): FFT along n on the landed rows — the LL
period in n is already resolvable and gives an early count of surfaces; abort if
no oscillatory structure in n has appeared. (3) ~6 h in (B ≈ 3 T): partial
1/B FFT on the landed columns, ΔF ≈ 1.5 T — continue or call it early.
