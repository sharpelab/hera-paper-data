## HERA — Run 3: fine constant-D n-linecuts (rule out an undersampled SC arc)

The survey found no candidate, but its n-resolution (BG step 0.1 V ≈ 0.83×10¹¹) is **coarser than the predicted arc width (~0.5×10¹¹)** — a narrow SC arc could have threaded between grid points. This is the decisive resolution check before any "not-SC" lean (investigation Step 1: "locate with linecuts first, n range wider than the nominal band").

**Four constant-D n-linecuts** at D = −0.35, −0.45, −0.55, −0.65 V/nm (bracketing the BBG/WSe₂ prior, both around and beyond D≈−0.5), each scanning **n = −1.5 → −9×10¹¹** (well wider than the nominal −4 to −6 band), **n-step 0.075×10¹¹ — ~11× finer than the survey**. 394 pts total; gate vectors precomputed from the confirmed calibration (c_bg/c_tg = 1.185) and clipped to validators by dropping out-of-box points (D=−0.65 line trimmed to 91 pts). Loaded from `hera_scratch/linecut_vectors.npz`; co-swept via `multisweep`.

- **Drive 1 nA** (consistent with the survey; SNR over fragile-state gentleness — the question here is *resolution*, not drive. A 0.5 nA recheck is a cheap follow-up if anything looks marginal).
- **sr830_3 → 2 mV** (resolve Rxx to ~few Ω; an SC dip to <5 Ω from the ~20 Ω metallic background is unmistakable), sr830_2 → 0.1 V. `delay=1.2` (3×tc, more averaging than the survey's 0.5).
- Magnet untouched (still nominal zero; ~2 mT trapped flux unchanged from the survey — the effective-zero-field hedge is for later field work).

**Preconditions** asserted: base T, B≈0. **Cost ~10 min.** **Read after:** any Rxx dip below the metallic background along any D-line → zoom + bias spectroscopy on it; all four flat at fine resolution → the undersampling hole is closed and I move to the field/effective-zero question and the calibrated call.
