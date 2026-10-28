## Run 5 — Landau fan, ELECTRON side, D=0 — FS-count (`landau-fan-vti`)

Step 4/5 of `trilayer-stacking-fs-count`: n vs B at D=0 (electron, the clean side), per-column SdH FFT → F(n) overlaid on the Onsager forward model (`fs_count_b0`). n ∈ [0.5,3.5]×10¹² (40, fast), B ∈ [1.0,7.95] T (96, slow, uniform-1/B), sens 1e-4. 3840 pts, complete. **Clipping note:** low-n (<~1e12) × high-B (>~6 T) corner saturates (deep-QH Rxx >5 kΩ at the 100 µV FS) — that corner is QH-regime (SdH-FFT invalid there) and is excluded; the decisive n≥1.5e12 columns are clip-free.
