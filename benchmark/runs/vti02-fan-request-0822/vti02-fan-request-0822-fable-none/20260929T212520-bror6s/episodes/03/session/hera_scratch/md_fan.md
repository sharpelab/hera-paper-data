## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n × B, the stacking discriminator

Plan step 4 (`hera_scratch/plan.md`); operator-requested next move. The spot checks
(runs 6–7, ana cells 14–17) read multiband on both carrier signs — e-side F ≈ 7.4 T
matching the ABAB light band with the heavy partner unresolved, h-side pair
4.7 + 6.6 ≈ F_full — i.e. ABAB-consistent / ABCA-disfavored, ABCB open. The fan
resolves it: **F(n) family structure per gate column** (two parabolic-band families
summing to nh/4e → ABAB; a single nh/4e line → ABCA; a light ~√n monolayer-like
family → ABCB weight) plus the **LL gap sequence / crossing pattern** in (n, B).

**Design.** Fast axis: (V_tg, V_bg) co-swept along the calibrated D = 0 line
(run-5 cal), n = −1.25 → +3.25×10¹² cm⁻², 141 pts (Δn = 0.032×10¹²). Slow axis:
B = 1 → 10 T ascending (magnet sits at 0; opening ramp ~7 min), **120 rows uniform
in 1/B** — constant sampling per SdH period, per-column `sdh_fft`-ready with no
resample (F_Nyquist 66 T covers the 29.5 T 4× harmonic; window resolution 1.1 T
separates 22.2 (3×7.4) from a real 25.6 T partner). B < 1 T is already covered at
two densities by runs 6–7 at finer sampling. sr1 at 100 µV (10 kΩ FS): sized to the
high-B CNP stripe per the run-4 lesson; oscillation amplitudes (10–100 Ω) read at
0.1–1 % fs, demonstrated clean in runs 5–6.

**Coverage trade:** hole side reaches only n = −1.25×10¹² (TG −0.3 V limit) — the
hole fan is shallow; D = 0 only (a D ≠ 0 wedge is plan step 6, only if the call
stays ambiguous). Full hole-side coverage is not purchasable inside the committed
gate box.

**Checkpoints** (armed `hera-watch --next --follow`): first 3 rows — rail/leak/row
rate vs the 165 s/row prediction (run-5 per-point calibration, 1.17 s/pt); then
~hourly — partial fan re-form + per-column FFT; abort if the gate current trips,
sr1 rails over a wide n-band (not the CNP stripe), or rows run > 30 % over price.
Ends at **10 T with gates at 0**; the next step rides the field down.
