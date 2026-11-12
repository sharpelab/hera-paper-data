## Electron Landau fan (run 6): F(n) partition-robustness test

The FS-count refinement (fs-count step 5). Per-column SdH FFT across the D=0 fan
(n=[2,10]e12 x B 1.5-8T). For each density column, extract the low tone (f_ML) and
high tone (f_BL) and test **f_ML(n)+f_BL(n) = lambda*F_L(n)** with lambda constant.
Low-n columns whose high-B Rxx railed (overload) are excluded. Result: lambda ~ 1.06-
1.08, **constant across density** (5-7% scatter), in both Rxx channels -> the Luttinger
partition holds at every resolvable density -> **two Fermi surfaces -> ABA**. lambda is
the SdH-based lever-arm and agrees with the Hall n-scale (the geometry n was ~7% low).
f_BL ~ 0.85*F_L, f_ML ~ 0.20*F_L (BL dominant, ML small ~20% - the ABA expectation).
