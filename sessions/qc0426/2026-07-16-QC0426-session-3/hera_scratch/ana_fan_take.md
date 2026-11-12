**Read (run 9 — investigation step 5):**

1. **Partition robustness (the algebraic check): PASS.** f_ML(n) + f_BL(n) = λ·F_L(n) across |n| = 2.5–6.0e12 (74/87 columns, sr1) with a **single global scale λ = 1.048** and rms residual 1.92 T ≈ δF (2.0 T) — resolution-limited, no systematic bow. sr2's clean columns (16, high-|n| where it isn't clipped by design) give λ = 1.077, rms 0.78 T — same partition, second region. A coincidental one-density match is now excluded: the pair sums to the Luttinger frequency at every density tested.
2. **Scale coherence**: λ = 1.05 (fan partition) ≈ 1.07 (SC1 sum) ≈ Hall (n_Hall/n_gate = 1.02–1.10). One in-band scale satisfies the whole peak set — the "pin the scale before you reject" discipline closes with everything consistent.
3. **Grid-change reproduction (alias screen): PASS.** The fan's −6e12 column (uniform-1/B) gives {11.3, 53.5} vs SC1's uniform-B {11.1, 55.3} at the same density — both tones survive the sampling-scheme change within δF; neither is a grid alias.
4. **ML fraction** 12–26% across density (broad-brush constant, mild wiggle) — consistent with the survey's hole-side ML/BL balance; the f_ML branch never vanishes and never merges with f_BL.
5. **Both branches track their own smooth F(n)** (continuity-locked across 74 columns) — harmonics of one fundamental cannot do this while also partitioning F_L (a k·f harmonic would sum to (1+k)·f ∝ f_BL, not to F_L, and the measured f_ML/f_BL ratio varies with n).
6. **Hedges**: model overlay is qualitative here (electron-only solver — model gap logged); LK mass split unavailable (temperature-dependence blocklisted) → the f_ML-is-a-band vs exotic-mixing residual is carried as a stated fork, though the n-tracked partition leaves it little room.

**Next**: ride-down spot check at +3.0e12 (run 10, in flight) supplies the one model-quantitative Onsager point (electron side, inside the clamp), then the step-7 call.
