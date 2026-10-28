### Take — Step 3a: SdH spot check, hole n=-5e12 D=0 (run 2)

**SdH present; suggestive of an ABA-like partition, but acquisition-compromised -> not decisive.**

- Clear SdH oscillations on a rising positive-MR background from onset ~1 T. Both Rxx channels
  (sr1, sr2) agree.
- 1/B FFT (window [1.0, 2.31] T, deltaF ~ 1.8 T): a **dominant ~8.5 T tone** + a secondary
  **~44 T** feature. **8.5 + 44 = 52.5 T ~ F_L = 51.7 T** — i.e. f_ML + f_BL = F_L, the ABA
  two-pocket Luttinger partition. The ~8.5 T tone is **real** (the real-space ΔRxx shows ~7 slow
  oscillations over the window, matching 8.5 T, not the ~36 a 44-52 T tone would give).
- **Two acquisition flaws keep this from being a call** (both fixed on the electron side, run 3):
  (1) sr1/sr2 **clipped** at the 2e-6 sensitivity (109 Ω) above 2.31 T -> window capped, deltaF
  coarse; (2) the 8 mT B-step **under-samples F_L below ~1 T** (Nyquist ~40 T at 0.8 T) so the
  fast (~44-52 T) tone aliases there -> window floored at 1.0 T. sr3 (Rxy) clipped throughout
  (its B=0-set sensitivity was far too fine for the ~500 Ω classical Hall) -> unusable here.
- Amplitudes are NOT used for the count (per the FS-count recipe): the read is 8.5 + 44 -> F_L,
  a frequency partition. The unusually strong ML-side amplitude is noted, not weighed.

**Status:** hole side *consistent-with ABA* (a resolved pair partitioning F_L), pending a clean
confirmation. Electron-side run 3 (fixed high-field sensitivities, full [1,4] T window) is the
clean test; then pick the cleaner side for the fan.
