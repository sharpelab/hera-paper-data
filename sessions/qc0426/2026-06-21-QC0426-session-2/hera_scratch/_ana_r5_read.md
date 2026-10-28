**Read — FS-count call (electron-side region, contacts T3–T4 / B4–B5):**

**1. Per-region verdict:** `sr1 (T3–T4): consistent-with ABC (weak)` · `sr2 (B4–B5): consistent-with ABC (weak)`. A **single Fermi surface tracking F_L** is resolved across n=1.5–3.5×10¹²; this matches the ABC singleton template, but **ABA is not excluded** (see hedges). Both channels agree → a **coherent single-domain region** (no mosaic in this region).

**2. Evidence:**
- One dominant SdH tone per column, **F(n) tracking F_L** over n=1.5–3.5e12, both channels (e.g. n=2.5e12: F≈26 T vs F_L=25.8 T). Stable across cutoff (1.5–4 T) and detrender (bg-deg 3–7) — Verify FFT-stability PASS (contrast the hole side, which wandered).
- **Onsager overlay** (`fs_count_b0`): measured F(n) co-locates with the ABC single-pocket curve under a **single global density rescale λ=1.03** (well inside the plausible 0.8–1.2 band → geometry scale prior validated, no red flag).
- **Luttinger sum:** the single tone carries ≈ the full density (F ≈ F_L = (h/4e)·n) across the range → one four-fold pocket.

**3. Confidence + hedges:** **Weak ABC lean, not decisive.** The decisive hedge: the model predicts ABA's discriminating **ML pocket at only ~0.1–2.2 T** over this density range — **below this run's resolution (δf≈1.9 T) and inside the MR-background band** — and ABA's BL tone coincides with ABC's single tone (both ≈ F_L). So the ML partner is **not-resolvable, not searched-and-absent**: its non-detection cannot exclude ABA. Warm electron-T (~8 K) sets the high SdH onset (~3 T) that limits the 1/B record. Hole side was resolution-limited (run 3); call is electron-region-only. Low-n (<1e12) QH corner clipped/excluded.

**4. What would firm it:** (a) **Step-6 high-field Streda/Chern offset** — the ML Dirac band offsets the QH sequence with several-meV gaps, resolvable at this T (needs a dedicated low-n, high-B QH run with QH-appropriate sensitivity; note `fs_count_b0`'s ABC LL model is not yet built, so Step 6 is qualitative on the ABC side). (b) **Lower T (mK rig)** to resolve the ~1 T ML pocket directly. (c) Higher density (>3.5e12, where ML grows) — but the model overlay clamps above 3.5e12; extend the solver first.

**5.** This is a **bounded, evidence-cited outcome, not a confident bare call**: the FS-count method here resolves one pocket at F_L (ABC-consistent) but **cannot positively distinguish ABA from ABC at this T/field because the sole discriminator (the small ML pocket) is below resolution.** Per the investigation, that is a successful, calibrated result — and it points to the Step-6 complement as the discriminating follow-up.
