## HERA — Step 4: Landau fan, ELECTRON side, D=0 (`landau-fan-vti`)

FS-count fan: n vs B at D=0, per-column SdH FFT → **F(n) vs F_L** to resolve single-pocket (ABC, one tone tracking F_L) vs partition (ABA, f_ML+f_BL=F_L). **Side = electron:** run 4 resolved a robust dominant tone at ~34 T ≈ F_L (clean, both channels, stable across extraction) — de-risking this fan; the hole side (run 3) was resolution-limited (no robust tone).

**Grid:** n ∈ [0.5, 3.5]×10¹² cm⁻² (40 pts, **fast**, D=0 line; ≤3.5e12 keeps the Onsager overlay valid) × B ∈ [7.95, 1.0] T (96 pts, **slow**, uniform-1/B, Δ(1/B)=1/(3·F_Lmax=36 T), inherited from the spot check). B **descending** (rides home from run 4 at 8 T — no re-traverse). Dwell fast 2.5 s / slow 2 s (settled, 24 dB/oct). Sensitivities sr1/sr2=1e-4, sr3=5e-5 (clean, no clip at the ~kΩ high-field MR). 3840 pts.

**Cost ~4.5 h** (field traverse ~51 min + 96 B-rows × ~40 n-pts × ~3.3 s). **Checkpoint ~50 % (~2.2 h, B~2.5 T):** per-column FFT on the high-field rows landed — is F(n) tracking F_L (ABC) or partitioning (ABA)? continue/adjust/abandon. Ends at 1 T.

**Reads (Steps 4–5):** per-n-column SdH FFT → F(n); test Σf = n (Luttinger), overlay on the Onsager forward model (`fs_count_b0`, ≤3.5e12); per channel (sr1, sr2) separately (mosaic check). Single tone on F_L → ABC; pair → ABA.
