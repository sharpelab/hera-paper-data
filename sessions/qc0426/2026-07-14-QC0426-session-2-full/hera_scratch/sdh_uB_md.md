## HERA — spot-check redesign validation: uniform-B collection, electron point (E0 — operator runs)

Head-to-head against run 6 (same point, n = +6×10¹², D = 0): sweep **uniform in B**, 1.33 → 8 T, **ΔB = 9.5 mT (703 pts)** — chosen so the 1/B Nyquist still holds at the low-B end (ΔB ≤ Δ(1/B)·B_lo², Δ(1/B) = 1/(3·F_L)). High-B sampling goes from ~2.8 to ~100 pts/period; no blind multi-minute ramps between points; the live trace should read like a normal MR sweep. Analysis path unchanged — `sdh_fft` resamples internally; I'll compare FFTs and peak stability against run 6 when it lands.

**Cost**: ~703 × (4.2 s ramp + 2.3 s dwell/read) ≈ 76 min + ~10 min positioning (0 → 1.33 T) → **~1.4–1.5 h**. Ends at 8 T with gates at the electron point — if we want it back down afterwards, say so and I'll stage a ride-home.

Preconditions: magnet at ~0 (parked), T < 2 K, Si 0. Sensitivities re-asserted to spot-check values in-cell. Tag: `sdh-spot-check` (+ uniform-B variant note in the comment).
