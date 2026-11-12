## Run 5 — calibration Landau fan (V_bg = 0): the measurement that unstuck the session

`recipe: measurements/landau-fan-vti.md`. B slow 0 → 6 T × 13 rows (0.5 T),
V_tg fast [−0.3, +1.0] × 201 (6.5 mV) at V_bg = 0, dwell 0.70 s, I_bias = 49.2 nA.
Complete, 2613/2613, 80 min.

**Not** the investigation's Step-4 FS-count fan — the 0.5 T rows are far too
coarse for a 1/B FFT. This exists because the zero-field calibration did not
close, and field is the only thing that closes it: at fixed B, adjacent Landau
minima are separated by Δn = eB/h *exactly*, from degeneracy alone, so LL
geometry gives the lever arm with no band model and no assumed capacitance.
