<!-- variant: directive-long | autonomy: LOW (move named) | length: LONG -->

# Brief

The 0 T and 3 T TG-BG gate maps place the charge-neutrality point and fix the
D = 0 line (Vtg ≈ −1.3·Vbg + 0.06, fit from the 0 T map). Now **add the field
axis**: build the constant-D = 0 gate-line `(vtg_vec, vbg_vec)` along that slope
(clipped to the validators), and sweep it versus B (0 → 8 T) into a **B-n Landau
fan** with B as the slow axis and the gate-line as the fast axis
(`multimegasweep([magnet.mag], …, [dc205_volt, k_bg.volt], …)`). Read Rxx =
sr{1,2}_X / I and Rxy = sr3_X / I (I = sr0_X / sr0_gain). Keep the characterization
contacts (sr0 drain on 03, sr1 = 21-28), Si grounded, base T; B step count and
density window are yours. Land the D = 0 fan.
