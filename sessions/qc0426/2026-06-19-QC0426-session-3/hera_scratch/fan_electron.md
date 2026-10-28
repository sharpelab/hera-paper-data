## HERA — Step 4: Landau fan, ELECTRON side D=0 (E1 auto, ~8 h)

`landau-fan-vti` / investigation Step 4. The electron side (run 3) gave the clean,
low-onset (~0.4 T) SdH with a reproduced two-pocket structure -> take the fan here.
Field = **slow** axis (magnet ramps once, monotonically 0.4 -> 4.0 T); paired-gate
**n-line at D=0** = fast axis, via the run-1 calibration.

**Design / Nyquist.** n = 1.0 .. 4.5e12 (41 pts): spans the model-overlay range (<=3.5e12,
for ML/BL Onsager labeling, Step 5) up to high-n where the ~8 T ML partner is resolvable.
B = 0.4 .. 4.0 T, **8 mT** (451 rows): per-column FFT window [1,4] T is alias-free (8 mT
Nyquist at 1 T ~ 62 T > F_L) and Nyquist-resolves the B-period down to n~4.5e12 (>=2 rows/period
at B>=1 T) -- measurement-dominated regime, so n_max capped at 4.5e12 rather than coarsening B
(per the -vti cost note). **fast_delay 1.0 s** (~3 tau): a deliberate amplitude-for-time trade --
under-settling attenuates SdH *amplitude* but not *frequency* (the FS-count observable); the
spot checks (runs 2-3, full 2.2 s settling) hold the amplitude reference. Fixed sensitivities
sr1/sr2=1e-5, sr3=2e-5 (no autorange -> row-to-row comparability); the lowest-n columns may clip
near the high-B CNP corner (overlay anchors, not the count target) -- flagged.

**Cost** ~8 h (min-duration 5.3 h delays + ~2.6 h measure overhead + magnet stepping); ETA ~08:50.
NO LS335 fp. **Checkpoint at ~B=1.5 T (~30%, ~2.5 h):** re-form 3-4 n-columns, FFT, confirm the
two-pocket structure tracks F(n) and leakage <1 nA -> continue / adjust / abandon. Ends with gates
parked at 0 and the magnet ramped to 0. hera-watch armed; client timeout set well above 8 h.
