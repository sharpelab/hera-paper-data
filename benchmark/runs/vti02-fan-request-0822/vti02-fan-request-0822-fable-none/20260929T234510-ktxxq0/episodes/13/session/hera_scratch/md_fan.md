## HERA — Landau fan at D = 0 (`landau-fan`) — the stacking-call measurement (plan step 4)

Spot checks (runs 6–7, ana cell 15) show two-band SdH at both carrier signs with tone sums ≈ F_full — **ABCA disfavored, ABAB vs ABCB unresolved**. The discriminator is density dependence: the frequency-vs-n partition between light and heavy bands and the high-B Landau-level gap/crossing pattern. This fan measures R_xx(n, B) along the D = 0 line (run-5 calibration).

**Design.** Fast axis: (V_tg, V_bg) co-swept along D = 0, n = −1.25 → +3.25×10¹² cm⁻², 131 pts (Δn = 3.46×10¹⁰ → ≥ 7 pts per Δν = 1 at 10 T; ν lines resolved above ~2–3 T). Slow axis: B 0.4 → 10 T ascending (magnet sits at 0; never re-traverse), 60 mT, 161 rows — 1/B Nyquist supports per-column FFT of all observed tones (≤ 35 T) above ~2 T. fast_delay 1.0 s (= run-5 gatemap; 3.3τ at τ = 0.3 s), slow_delay 2 s on top of the driver's 3 s field settle. sr1 fixed 200 µV (20 kΩ FS at 10 nA): SdH range 10–600 Ω well resolved; **accepted rail**: the ν = 0 CNP stripe may exceed 20 kΩ at high B — sr0 (drain current) covers the railed stripe, and the rail itself marks the gap.

**Coverage trades, stated.** Hole side ends at n = −1.25×10¹² (TG −0.3 V validator, not a choice — full hole coverage would need a limit change, which is session-banned). Single D = 0 cut: gap-vs-D discrimination is a contingency step if the fan is ambiguous (plan step 6).

**Price:** 161 rows × (131 × 1.10 s/pt [run-5 actual] + 26 s ramp + ~9 s turnaround) ≈ 8.0 h + start-up → **8 h 45 m realistic**. Ends at **10 T** with gates ramped to 0.

**Checkpoints** (hera-watch armed): first rows ~12 min (rail/leak/level — cheapest kill); ~2 T (~1.5 h, structure forming, CNP stripe level); ~5 T (~4 h, interim map re-form + F(n) read); ~8 T (~6.5 h, gap fingerprint). Wash-out: sr1 railed across the line, leak trip, dead channel, or no n-dependent structure by 3 T.

**Preconditions** (asserted in-cell): T_sample 1.0–1.5 K, |B| < 0.02 T, V_si = 0, Keithley NPLC 1, PS heater on + output enabled, thermometry logfile fresh.
