## HERA — SdH spot check A: electron n=+8e12, D=0, B 0->8T

Investigation `trilayer-stacking-fs-count.md` step 3 / `sdh-spot-check.md`. First of
two fixed-(n,D=0) field sweeps from zero. Pins the **onset**, the **tone content**
(FFT in 1/B vs F_L=82.7 T), and which density side gives cleaner SdH. A clean spot
check can be decisive on its own.

**Acquisition** (locked here, inherited by spot B + the fan): AC drive boosted to
**50 nA** (device R ~30 ohm at this n; 5 nA gave ~0.1uV, SdH buried), sens 20uV
(Rxx) / 50uV (Rxy, quantized Hall up to ~630 ohm at 8T), dwell 2.5 s (~8 tau, the
weak-tone settling floor), **B-step 12.5 mT** (Nyquist on F_L to ~1.7 T). 641 pts.

**Cost ~90 min** (blocking magnet ramp 0->8T ~58 min + 641x2.5s dwell ~27 min +
overhead). **Checkpoint at ~B=4T (~45 min):** confirm SdH emerging above onset, SNR
adequate, no overload; continue / adjust sens / abandon. Field is **left at 8T** so
spot B (hole, n=-8e12) descends 8->0 with no wasted return traverse.
E1 auto (in-envelope: |B|<=8T cap, gates within validators, D=0).
