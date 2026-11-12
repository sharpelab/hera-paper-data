## HERA — Step 3a: SdH spot check, HOLE side (E1 auto, ~50 min)

`sdh-spot-check` / investigation Step 3. Fixed **(n = -5e12, D = 0)**, B swept **0 -> 4 T from
zero** (reads the onset directly). Gate point from the run-1 (n,D) calibration:
Vtg = -2.28 V, Vbg = -1.76 V (Si = 0), both well inside validators.

**Design.** High-|n| metallic regime -> **bias 2 V / 20 nA** (device card; the 0.5V/5nA default
would put the four-terminal signal near the ADC floor). Lock-in **dwell 2.2 s** = 7*tau at
tau=0.3/24 dB/oct (the settling floor — under-settling buries a small tone). **B-step 8 mT**:
Nyquist-resolves F_L = (h/4e)*n ~ 52 T at n=5e12 down to ~1 T (oscillation spacing in B at 1 T
~ B^2/F ~ 19 mT). Sensitivity set adaptively (~2x headroom) after settling at the gate point.
NO LS335 fp (the run-1 lesson). FFT read (1/B, MR background subtracted) happens post-run.

**Cost:** ~501 pts; magnet 8 mT/step blocking ramp (3.5 s) + 2.2 s dwell ~ 5.7 s/pt ->
**~48 min** + gate ramp. **Checkpoint at ~B=2 T (~25 min):** read the hera-watch digest for
visible SdH structure, leakage <1 nA, no sensitivity clipping -> continue / adjust. Leaves the
magnet at **4 T** for the electron-side spot check (4 -> 0 T descent — no wasted re-traverse).
hera-watch armed on the next run.
