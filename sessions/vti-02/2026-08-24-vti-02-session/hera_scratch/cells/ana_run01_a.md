## Run 0 — `gatec-liveness`: back-gate cut at V_tg = 0 (Gate C)

**Why / what we're testing:** the brief withholds the CNP location, and every later step —
the gate map's window, the fixed-D cuts, the Landau fan's density axis — is anchored on it.
This is the cheap liveness check on the provided hardwired configuration (source T_0,
drain B_3, Rxx across B_1–B_2) plus a first bracket on neutrality: one 1D V_bg cut at
V_tg = 0 across the whole committed back-gate range, which sweeps
Δn ≈ 5.0 × 10¹² cm⁻² on the geometry prior.

Conditions: V_tg = 0, V_si = 0, B = 0, T = 1.170 K, I_bias = 10.0 nA (1.0 V through
100 MΩ at 13.777 Hz), 133 points at 25 mV, dwell 2.1 s = 7τ at the then-current τ = 0.3 s.
`sr1` was at 2 µV sensitivity going in — knowingly too tight, and it clipped.
