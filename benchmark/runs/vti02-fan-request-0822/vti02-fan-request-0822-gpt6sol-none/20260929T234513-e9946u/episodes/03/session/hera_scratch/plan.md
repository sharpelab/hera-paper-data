# vti-02 stacking campaign plan — updated after runs 0–7

Goal: call ABAB / ABCA / ABCB, or cannot tell, for the hardwired T_0→B_3,
B_1−B_2 contact configuration. Keep the distinction between a contact-pair
read and two spatial CNP ridges visible in the 0 T map; there is no mux.

1. Bring-up and gates A/B/VERIFY. Done: measure cells 2–32, grant recorded
   in session_notes.md. Reconfirm the live kernel, committed validators, base T,
   field, Si, and hardwired route before each long run.
2. Gate C liveness. Done: runs 0–3 in the provided configuration, leakage low.
   A dead channel would require operator rewiring, not a software detour.
3. CNP and (n,D) calibration. Done: run 5 (run 4 clipped and was stopped).
   Ratio c_bg/c_tg = 0.773 from the A ridge; absolute c_tg uses the geometry
   prior. A second parallel ridge B has a 0.426e12 cm^-2 offset. D=0 from
   the CNP resistance vertex. Recheck the absolute density scale with Landau
   slopes; preserve the mosaic ambiguity until resolved.
4. SdH feasibility. Done: electron run 6, hole run 7. Both oscillate; multiple
   peaks/harmonics and two spatial ridges make a fixed-density FFT insufficient
   for a stacking verdict. The hole side is gate-limited at -1.27e12.
5. Landau fan, electron side at D=0. Next: co-sweep TG/BG on the calibrated
   D=0 line at each B row, B=2–10 T. Start at the present 0 T, ramp once to
   2 T and sweep upward. Fast density 0.5–3.2e12 in 0.05e12 steps; slow B
   0.2 T steps. This captures low filling and the electron-side tones in run 6
   while keeping the gapped CNP outside the main scan. Use measured current for
   R, monitor leakage and clipping at the first rows and periodically. If the
   fan is clipped or flat, stop early; if LL ridges resolve, use their slopes
   to verify the absolute lever arm and test one vs two ladders/offsets.
6. Follow-up only if required by the fan: a focused higher-resolution sector,
   opposite-D cut, or temperature dependence to separate intrinsic bands
   from the A/B mosaic. Choose from the run-8 map, within all committed limits.
   Do not spend hours on a second fan without a specific ambiguity to resolve.
7. Final ana cell: one verdict for the measured B_1−B_2 contact pair, cited
   run ids and numbers, confidence, what would overturn it, and unmeasured
   contacts/regions. Close out on request: field/gates zero, heaters off,
   readbacks in session_notes.md.
