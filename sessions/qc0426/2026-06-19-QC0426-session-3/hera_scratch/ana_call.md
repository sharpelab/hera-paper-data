## STACKING CALL — QC0426 trilayer graphene: **ABA (Bernal)** — strong, hedged

Per `investigations/trilayer-stacking-fs-count.md` Step 7 output contract. Region = the two
four-terminal Rxx pairs probed at D=0: **sr1 = T3-T4**, **sr2 = B4-B5**.

### 1. Per-region verdict (STYLE strength scale)
- **sr1 (T3-T4): ABA (strong)**
- **sr2 (B4-B5): ABA (strong)**
- ABC-singleton **excluded** on both (a second, density-summing pocket is resolved).
- Both pairs agree -> no stacking mosaic detected **among these two regions** (limited sampling: 2 pairs).

### 2. Evidence (each tone: frequency, (n,D) side, artifact, Luttinger)
- **Two coexisting SdH frequencies, both Rxx channels, both density sides** (the FS-count signature):
  - **f_high ~ 44 T** and **f_low ~ 8 T** at **n=+5e12, D=0** (electron, run 3, clean full-settling
    [1,4] T FFT) and reproduced at **n=-5e12** (hole, run 2). **f_low + f_high = 52.5 ~ F_L = 51.7 T**
    -> Luttinger partition Sum f = n satisfied. (ana run 2/3 cells.)
  - **Harmonic screen:** 44/8 = 5.5 (non-integer) -> neither tone is a harmonic of the other; both
    are fundamentals. f_low is a real fundamental (its real-space period = ~7 slow oscillations over
    [1,2.3] T matches 8 T; it is not a beat difference — a 40/48 beat would violate Luttinger).
  - **Fan dispersion (run 4, electron, n=1.0-4.5e12):** the high-F ridge **disperses linearly through
    the origin** (F = 8.76*n[e12]), **detrend-stable** (orders 3/5/7 identical -> real), tracking the
    **Onsager model f_BL / ABC F_tot curves at ~0.89*F_L**. The density-carrying pocket is confirmed as
    a real Fermi surface area ∝ n.
  - **Amplitude consistency (supporting, not a count):** the *light* low-F tone is amplitude-DOMINANT,
    the *heavy* high-F tone weaker — exactly the ML(Dirac, light, less Dingle-damped) vs BL(heavy,
    damped) ordering ABA predicts. Frequencies do the classification; this is a corroborating prior.

### 3. Confidence + specific hedges
- **Strong** that >=2 Fermi surfaces coexist at D~0 (decisive on "two pockets" from the clean spot
  checks) -> **ABA**. Hedges:
  - **ML partner fraction (~15% of F_L) is ~2x the SWMcC-model nominal (~6%)** — a quantitative fork
    (lever-arm and/or model-parameter, NOT a count error). The n-scale is geometry-prior (~10-15%); a
    QH lever-arm upgrade would pin it and the partition fractions.
  - The **ML pocket is resolved only at high |n| (spot checks, ~8 T)**; in the fan it sits at the model's
    0-2 T (n<=3.5e12), below clean resolution and inside a low-F detrend-artifact band — so the fan
    **confirms BL dispersion but does not independently resolve the ML partner**. Per the recipe, the
    cleaner spot checks carry the ML evidence; the noisier fan does not overturn them.
  - **Searched-and-absent:** no ABC-singleton-only column (every clean column shows the partner in the
    spot checks); no third pocket / mosaic disagreement between sr1 and sr2.
  - **Not-resolvable:** lowest-n fan columns (n<~2e12) clipped at high B (sensitivity ceiling) -> the
    low-F_L overlay anchors are degraded.

### 4. What would firm the call
- **LK effective-mass split** (the deciding ML-vs-BL cross-check: light ML vs heavy BL -> two distinct
  masses confirm two bands; `temperature-dependence` Flavor B). **Not available this session —
  temperature-dependence is blocklisted.** Highest-value next step (another session/rig).
- **QH lever-arm upgrade** (dn/dB = nu e/h) to pin the absolute n-scale and the ML/BL partition fraction.
- More Rxx pairs (mosaic check beyond 2 regions); a clean high-n spot check on additional channels.

### 5. Statement
A confident binary would be a protocol violation without feature-level evidence — we HAVE it (two
resolved tones partitioning F_L, reproduced across channels and density sign, with the BL pocket
dispersing on the model curve). The call is **ABA (Bernal), strong**, with the ML-fraction fork and the
missing LK-mass cross-check as the stated reasons it is not "decisive." This is **not** a "cannot tell."

*(QC0426 / VTI, 2026-06-19/20 session. Runs: 0-1 (n,D) cal; 2 hole spot; 3 electron spot; 4 fan.
n-scale geometry-prior; absolute frequencies inherit ~10-15% lever-arm uncertainty.)*
