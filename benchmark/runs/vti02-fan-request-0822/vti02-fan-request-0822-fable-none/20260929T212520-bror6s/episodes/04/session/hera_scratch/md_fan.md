## HERA — Step 4: Landau fan at D = 0 (`landau-fan`), n = −1.25 → +3.24×10¹², B 0.2 → 10 T

**Why (plan step 4):** the spot checks (runs 6/7, ana read) show multi-band light-mass SdH on both carrier signs — ABCA is disfavored, and the ABAB-vs-ABCB call now needs the fan: ν-line slopes and intercepts (harmonics have no independent ν lines), the LL-crossing pattern (two bilayer-like bands → a crossing lattice), the filling sequence, and the CNP gap vs B.

**Geometry:** fast axis = co-swept (V_tg, V_bg) along the run-5-calibrated D = 0 line (`multimegasweep`), n = −1.25 → +3.24×10¹² cm⁻² in 205 pts (Δn ≈ 0.022×10¹²; V_tg −0.291 → +0.995 V, V_bg −0.484 → +1.181 V, asserted inside the validators). Slow axis = B, 0.2 → 10.0 T in 0.1 T steps (99 rows), ascending from the parked 0 T (magnet never re-traverses; ends at 10 T). Si gate stays 0.

**Coverage trade:** hole side stops at n = −1.25×10¹² — the TG −0.3 V limit ends the D = 0 line there (full coverage is not purchasable inside the committed box). D ≠ 0 is not covered by this run; a D ≠ 0 fan riding B back down is the contingency if crossings are ambiguous (plan step 5a).

**Settings:** sr1 sensitivity 200 µV → 20 kΩ FS at 10 nA (run-5 lesson: size to the gapped-CNP expectation — B = 0 CNP peak 330 Ω, ν = 0 grows steeply with B; railing accepted only at the highest-B CNP points, censoring gap magnitude there, never ν-line positions). fast_delay 1.0 s = run-5 precedent (3.3 τ at τ = 0.3 s, 24 dB/oct — below the 7–10 τ floor, bent knowingly: single sweep direction makes the filter lag a constant ~2-pt shift along n, slopes unaffected). slow_delay 3 s. Leak guard trips at 1 nA; T guard trips above 1.8 K.

**Expected warnings:** sustained ≈ −100 pA TG current on the negative-V_tg half of each row (run-7 signature, benign) — hera-watch LEAK lines there are expected; the trip is 10× above it.

**Price:** 99 rows × (205 × 0.945 s [run-5 cal] + ~4 s flyback + ~47 s ramp+settle) ≈ 6.8 h nominal; with the session's 5–10 % overrun evidence → **≈ 7 h 15 m**. Ends at B = 10 T, gates at n = +3.24×10¹².

**Checkpoints:** first rows (~15 min): rail/leak/dead-channel + CNP peak visible per row; ~2 T (~1.5 h): partial fan re-form — ν lines emerging, sensitivity verdict; ~5 T (~4 h): interim crossing-pattern read — continue / abandon (an abort at 5 T still leaves a usable 0.2–5 T fan; the 5–10 T half prices at ~3.5 h).
