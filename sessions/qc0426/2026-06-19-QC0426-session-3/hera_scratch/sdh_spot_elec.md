## HERA — Step 3b: SdH spot check, ELECTRON side (E1 auto, ~74 min)

`sdh-spot-check` / investigation Step 3, clean run. Fixed **(n = +5e12, D = 0)** (Vtg = +2.43,
Vbg = +1.88), B swept **4 -> 0 T** — descends, riding the magnet home from the hole spot check
(no wasted re-traverse); onset read at the low end.

**Clean-acquisition fixes from run 2 (hole):** FIXED sensitivities sized for the HIGH field so
nothing clips over 0-4 T — sr1/sr2 = 1e-5 (covers ~500 Ω), sr3 = 2e-5 (covers the ~500 Ω
classical Hall at 4 T, which clipped on the hole run). bias 2 V/20 nA, dwell 2.2 s (7*tau).
NO LS335 fp. **FFT window [1, 4] T** — alias-free (8 mT Nyquist at 1 T ~ 62 T > F_L = 52 T; the
hole run's <1 T data under-sampled F_L). Full unclipped [1,4] T gives ~30 periods, delta(1/B) =
0.75, deltaF ~ 1.3 T.

**Why this matters:** the hole run (run 2) hinted at an ABA-like pair (~8.5 T dominant + ~44 T,
summing to F_L) but was clipped at 2.3 T and partly aliased -> suggestive, not decisive. A clean
electron-side spot check tests whether the same partition appears (per-channel, per the FS-count
combinatorics) and which side gives cleaner SdH for the fan.

**Cost** ~74 min (8.7 s/pt). **Checkpoint at ~B=2.5 T (~30 min):** SdH visible, no clipping,
leakage <1 nA. Ends with the **magnet at 0 T**. hera-watch armed on the next run.
