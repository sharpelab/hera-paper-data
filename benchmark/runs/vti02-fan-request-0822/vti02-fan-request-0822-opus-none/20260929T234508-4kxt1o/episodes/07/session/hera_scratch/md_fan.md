## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — the decisive measurement for the stacking call

**Why now (plan step 4).** Steps 0–3 are done and the spot checks have said all they can.
Run 6 (n = +3.2×10¹², D = 0) gives onset 0.30 T (censored at the record's low edge), robust
tones from 1.3 T, and a tone set {3.0, 4.2, 5.2, 7.1} T riding a clean harmonic ladder
7.1 → 14.1 → 22.2 → 29.5 T against F_Luttinger = 33.1 T; run 7 (n = −1.2×10¹²) gives onset
0.71 T and {4.7, 6.6, 8.5, 9.4, 12.3, 14.8} T against F_L = 12.4 T. **A fixed-n trace cannot
close the call**: it cannot separate a genuine second Fermi surface from a harmonic of the
first, and it cannot separate a second *band* from run 5's second *region* (ridge B,
electron-doped by 0.43×10¹² and in series along this pair). The fan does both — LL minima
follow n = ν·eB/h, so two *bands* appear as families with **different slopes converging on one
CNP**, while two *regions* appear as families with **equal slopes and offset n-intercepts**.
The tone/degeneracy pattern is the stacking read: ABCA → one tone at n·h/4e with a ν = 4N
family; ABAB → two comparable tones summing to n·h/4e; ABCB → two strongly unequal ones.

**Grid.** Fast axis is density along D = 0, co-swept (V_tg, V_bg) via `multimegasweep`:
n = −1.25 … +3.25×10¹² in 139 points (Δn = 0.0326×10¹²) — the full window the validators
allow on the D = 0 line (TG-limited at both ends, 2 mV of margin at the top). That resolves a
ν = 4 gap with 5.9 points at 2 T and 30 at 10 T. Slow axis is B, uniform in B (LL lines are
straight in (n, B)): **50 mT below 3 T, 100 mT from 3 → 10 T, 131 rows**, starting at 0 T where
the magnet sits. The step is set by 1/B Nyquist for the FFT read, not by the line read:
Δ(1/B) ≤ 0.0125 T⁻¹ everywhere above 2 T, i.e. unaliased to F = 40 T, comfortably past the
F_L = 33 T ceiling of this n window. Sweep goes **up**, ends at 10 T — the magnet never
re-traverses, and steps 5–6 spend that field rather than paying for it again.

**Settling — τ is moved from 300 → 50 ms, deliberately, and restored in `finally`.** sr1 is at
24 dB/oct, where the 1 % settling floor is ~10 τ. At the bring-up τ = 0.3 s that is a 3 s dwell
= 15.7 h for this grid, and the alternative the gatemap used (1 s dwell = 3.3 τ) leaves a **57 %
step residual** — a lag of ~2.4 points ≈ 0.08×10¹² in n, which is a quarter of a ν = 4 period at
2 T and would smear exactly the feature the call rests on. At τ = 50 ms the dwell of 0.5 s is a
full 10 τ: **fully settled, not a bent rule**, at 4.5 h. The price is noise ×2.45 (ENBW
5/64τ) — from the measured per-point scatter in runs 6/7 (σ_V ≈ 20–35 nV at 50 µV FS,
σ_R ≈ 2–4 Ω) that puts this fan at σ_R ≈ 5–10 Ω per point, against SdH tone SNR of 40–120 in
those same runs. Nothing else on the panel is touched; τ (both sr0 and sr1) goes back to 0.3 s
when the cell ends, including on an interrupt.

**Sensitivity — sized for the LL lines, not for the CNP.** sr1 at **500 µV = 50 kΩ full scale**
at I_bias = 10 nA (runs 6/7 peaked at 590 Ω ≈ 1 % of this). Run 4's lesson was to size for the
map's worst corner; here that corner is the CNP column at 10 T, whose resistance is *unmeasured*
and could exceed 50 kΩ if a ν = 0 gap opens. Rather than de-tune the whole fan for one column,
the **coverage trade is stated**: if the CNP clips at high B, plan step 5 recovers it with a
short gate cut across the CNP at 10 T on a larger FS, costing gate time only (~15 min) because
the magnet is already there. Sizing the fan at 5 mV FS instead would cost every line ~10× in
relative resolution for that one column.

**Preconditions the cell asserts (not sets):** thermometry worker live (logfile advancing),
T_sample 1.0–1.5 K, |B| < 0.05 T (the sweep starts at 0), V_si = 0, Keithley nplci = 1 and
volt.step = 5 mV, PS heater on + output enabled, drive 1.0 V @ 13.777 Hz → 10 nA. Gate leakage
trips the run at 1 nA (well above the ±100–200 pA flyback transient); a sustained T excursion
above 2.0 K also trips it; clipping is counted and reported per row but does **not** trip.

**Checkpoints** (`hera-watch data --next --follow` armed as a background monitor before the
cell starts): **(1) first 3 rows, ~4 min in** — signal present, sr1 fs fraction sane, no leak,
T flat, and the B ≈ 0 row reproducing run 5's D = 0 cut; abort there if any of those fail.
**(2) ~2 T, ≈1 h 15 m in** — SdH structure visible in the landed rows, and the CNP column's fs
trend extrapolated to 10 T to set step 5's sensitivity; abandon if there is no oscillatory
content by 2 T (then the read is T_e-limited and the fan is not the right instrument).
**(3) ~5 T, ≈2 h 40 m in** — first quantitative pass on the landed half: LL-line slopes → ν,
and whether one or two families are present. Continuing past there is the cheap half (the
ramp is already paid); the call to stop would be a device or thermometry problem, not physics.

Gates park at 0 V when the cell ends; the field is left at 10 T on purpose.
