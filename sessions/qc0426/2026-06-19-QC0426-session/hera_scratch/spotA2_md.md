## HERA [E1] — SdH spot-check A (re-run): proper sensitivity + magnitude readout

First attempt was under-ranged (sens 2e-5 from the kΩ CNP map → 0.25% FS on the ~tens-Ω
metallic Rxx; aborted at 2 T, data/2). Fix: per-channel sens for Rxx~tens-Ω (sr1 2e-6
[|R|~128 Ω], sr2 5e-7 [|R|~26 Ω, cleanest], sr3 5e-6 Hall, sr0 1e-2); raise sr1 τ 0.03→0.3.
Diagnostic showed the resistive signal at ~+42° — a cosmetic **reference-phase offset**
(device is resistive at 13 Hz), so **Rxx = lock-in |R|**; fp X/Y/R and use the magnitude
(phase handled offline), leaning on the cleaner sr2.

B 0→4 T, ΔB=10 mT (first point ramps 2→0). ~70 min (incl. the 2→0 down-ramp). Ends at
4 T for the electron spot check (4→0). Checkpoint ~30 min in. Auto: gates in validators,
B≤4<8 cap. Tag `sdh-spot-check`.
