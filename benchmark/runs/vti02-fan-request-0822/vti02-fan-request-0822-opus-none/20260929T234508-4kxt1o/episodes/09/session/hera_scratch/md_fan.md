## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — n fast, B slow, 1.5 → 10 T

**Plan step 4.** Runs 6/7 established that SdH here is strong and survives to ≲ 0.7 T,
but a single-density trace cannot answer the stacking question. Run 6's high-B FFT
(n = +3.2×10¹²) is a **harmonic comb on ≈ 6.7 T** — 6.7 / 13.3 / 20.0 / 26.7 / 33.3 /
40.0 T — and 33.3 T is exactly the full-density Luttinger frequency F_L = 33.1 T at that
density. Two readings fit that one trace: **(a)** a light surface carrying x ≈ 0.20 of n
plus a heavy partner at x ≈ 0.80 whose 26.6 T tone hides under the 4th harmonic —
**ABAB**; or **(b)** a single x = 1 surface at 33 T whose spiky, well-developed
lineshape generates the entire comb — **ABCA**. This fan is built to separate them.

**Why this geometry.** Fast axis = density along D = 0 (cheap: 0.9 s/point), slow = field
(expensive: 0.137 T/min, hard-ramped). Sweeping n densely at fixed B makes the
**density-space FFT** the primary read: a Fermi surface carrying fraction xᵢ of the total
density oscillates with n-period (4eB/h)/xᵢ, so each row returns xᵢ directly, and
**Σxᵢ = 1** is the ABAB-vs-ABCA discriminator — 50 independent measurements of it, one
per row. Windowing that FFT along n gives xᵢ(n): two genuine subbands repartition n as
n moves, a harmonic tracks its fundamental at exactly k× forever. And the map itself
gives the fan lines n = ν·eB/h — their **n-intercepts** separate run 5's two CNP ridges
(A and B, offset 0.43×10¹²), making the verdict region-resolved rather than
trace-averaged, while the ν sequence gives the session's first **absolute** lever-arm
check on the 9.5 nm geometry prior.

**Grid.** Fast: n = −1.20 → +3.20 ×10¹² cm⁻² at D = 0, step 0.02×10¹² (221 points) —
(V_tg, V_bg) co-swept −0.277…+0.984 / −0.465…+1.166 V, 5.7 mV per point on TG, 16 mV
clear of the +1.0 V limit and 23 mV clear of −0.3 V. The full D = 0 line inside the
validators: **both carrier signs and both CNPs in one pass.** Slow: 50 rows **uniform in
1/B** (`field_invB`) from 1.5 to 10.0 T ascending — Δ(1/B) = 0.0116 T⁻¹, Nyquist 43 T, so
the along-B FFT (the cross-check on the n-FFT) resolves the whole comb including the
40 T harmonic. Uniform-1/B weights rows toward low field, which is where the n-FFT is
richest: at 1.5 T the ν = 4 period is 0.145×10¹² (7.3 points, 30 periods across the
sweep), so a 1×10¹²-wide window still holds ~7 oscillations. Ascending from 1.5 T
because the magnet sits at 0 T — no wasted traverse; ends at 10 T.

**Dwell — a stated bend.** `fast_delay = 0.8 s` against τ = 0.3 s at 24 dB/oct is 2.7τ,
below the k ≈ 7–10 settling floor. Justified because the fast axis is a smooth monotonic
ramp, not a step train: for the *worst* row (1.5 T, shortest n-period = 7.1 s of sweep
time) the 4-pole response costs **13 % oscillation amplitude and a rigid 1.2-point lag**
in n (0.024×10¹², 5 % of the A/B ridge offset — irrelevant to the frequency and
intercept reads this run is for), and both shrink at every higher-B row. The cost of
buying it back at 3τ-per-point would be ~35 min. **Consequence:** amplitudes from this
fan are not Dingle/LK-grade — mass fits come from the fixed-(n, B) temperature ladder in
step 5, not from here.

**Sensitivity.** sr1 at **200 µV = 20 kΩ full scale** at 10 nA. Applying the run-4
lesson in `session_notes.md`: size for the map's largest R, not the trace peak. The
fan crosses the CNP at 10 T, where a ν = 0 state could go far above the 587 Ω (run 7)
and 530 Ω (run 6) maxima and the 3.07 kΩ of the run-5 gapped ridge; 20 kΩ FS is 6.5×
the largest R seen anywhere this cooldown. Oscillation amplitude (≈ 63 Ω rms, run 6) is
0.3 % of FS — at ENBW ≈ 0.26 Hz that is still SNR ≳ 100, so the headroom is nearly free.
If the CNP does rail it will be a narrow, obvious n-window, not the run-4 failure.

**Leak guard** trips on **two consecutive** points over 1 nA rather than one: run 5 ran
4158 points at identical gate pacing with a 123 pA maximum, but its row-start flyback
transient reached ±200 pA (the `hera-watch` warning noted in `session_notes.md`), and a
single spurious sample must not kill a 4-hour run. A real leak is persistent, so the
trip still lands within ~2 s; the first strike prints.

**Price: ≈ 4 h 30 m** (bracket 3.9–4.3 h + the session's own 5–10 % over-run margin).
Arithmetic from run 5's measured overhead — 4158 points in 4873 s at `fast_delay = 1.0`
⇒ 0.10 s/point of read on top of the dwell: 50 rows × (221 × 0.902 s + 1.5 s gate
flyback + 5 s slow_delay + 3 s magnet settle) = 2 h 54 m, plus the 8.5 T traverse at
0.137 T/min = 1 h 02 m. 11 050 points. Ends at **10 T, gates parked at 0 V**.

**Checkpoints** (`hera-watch` armed on the run before it starts): **first 2 rows**
(~20 min in, after the 0 → 1.5 T ramp) — signal scale, no railing, leakage, and
oscillations actually present along n; **row ~12** (B ≈ 1.85 T, ~1 h) — partial re-form,
per-row n-FFT, are there one or two tone families and does Σx approach 1; **row ~30**
(B ≈ 3.0 T, ~2 h 20 m) — the same plus the xᵢ-vs-n drift test. Abort conditions: the
channel rails across more than a narrow CNP window; no resolvable n-periodicity by row
12 (then the fan is resolution-limited and the step-5 ladder is the better spend).
