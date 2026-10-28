## HERA [E1] — SdH spot-check A: HOLE side, n=−10e12 cm⁻², D=0

Step 3 of `trilayer-stacking-fs-count` (`sdh-spot-check`). Fixed (n, D=0), B swept
**0→4 T** from zero (captures onset), ΔB=10 mT (401 pts). F_L=103 T → ΔB Nyquists down
to ~1.7 T; recipe-validated step (scales from corpus 12.5 mT@8e12). Gates set to
(V_tg −4.666, V_bg −3.616) on the calibrated D=0 line. Magnet's built-in 3 s/point dwell
settles all lock-ins (even sr2/sr3 τ=0.3 → 10τ); leave operator τ untouched. ~52 min
(ramp + 3 s/pt dominated). Leakage via Keithley curr; T in comment (no Lakeshore poll).

**Checkpoint @ ~25 min (B≈2 T):** SdH oscillations emerging? onset visible? which Rxx
channel cleanest? leakage clean? Fork: continue / extend B / abort. Read is the 1/B FFT
(scratch, TSV) after completion. Ends at B=4 T (electron spot check will run 4→0 to reuse
the ramp-down — no dead re-traverse). Auto: gates in validators, B≤4<8 cap. Tag `sdh-spot-check`.
