# vti-02 stacking investigation — live plan (2026-09-29 pickup)

## Established

1. Bring-up, SAFETIES and E1 VERIFY passed in the instrument kernel (measure cells 2–32; session_notes grant). The handoff readback at measure cell 44 returned gates/field to zero; cell 46 re-probed the same kernel. Recheck actual state in each executed cell.
2. Gate C, data/0–3: the hardwired T₀→B₃ current path and B₁–B₂ voltage pair are alive; TG/BG currents are below the 1 nA trip.
3. Zero-field map, data/5: two nearly parallel CNP ridges are offset by ~0.43×10¹² cm⁻². Ridge A gives c_bg/c_tg = 0.773, n_offset = −0.089×10¹² cm⁻², D_offset = −0.013 V/nm. The absolute capacitance scale still uses the 9.5 nm TG geometry prior. Ridge A's D≈0 valid density window is −1.27 to +3.27×10¹² cm⁻².
4. SdH spots, data/6 (+3.2×10¹², D≈0) and data/7 (−1.2×10¹², D≈0): both show oscillations without rail. Data/6 has ~7.5 T and ~15/22.5/30 T peaks, plausibly harmonics. Data/7 has ~5–6 T and 12–15 T structure. Neither is a stacking verdict; the two series ridges can also make two tones.

## Next: electron Landau fan at D≈0

5. Sweep field as the slow axis at B=0 for a baseline row, then 1.5 to 10 T in 0.1 T steps (87 rows). At each field co-sweep TG/BG along the calibrated D=0 line for ridge A, n_A = +0.35 to +3.20×10¹² cm⁻² in ~0.040×10¹² steps (72 points). This uses TG +0.167 to +0.984 V, BG +0.110 to +1.166 V, Si=0, all inside committed validators. The n_B ridge offset is tracked as a possible second series region, not treated as an independent contact pair. Gate currents, current-channel X, Rxx-channel X and sample T are followed. A fixed 200 µV SR1 range provides ~20 kΩ nominal headroom at 10 nA; check first rows and periodically. The magnet starts at 0, ends at 10 T; its 0.137 T/min bare ramp floor is 73 min. 6,264 gate points at ≥7τ=2.1 s dwell, plus ~0.2 s reads/point, field settles and gate flybacks imply ~5.5–6 h. The first few rows and rows near 2, 5, 8 T are checkpoints; abort on sustained >1 nA leakage, clipping, dead current/Rxx, or a fan that washes out. Because the magnet keeps ramping after an interrupt, verify its actual field and supply status before changing course.

6. Analysis for each fan: plot raw Rxx(B,n) and gate current first, then remove a smooth density background only for feature tracking. Track resistance minima/maxima as n(B); compare branch slopes and intercepts with 4eB/h filling, the full-density SdH frequency, and the ~0.43×10¹² series-region offset. Harmonics of one pocket share their parent trajectory; distinct Fermi pockets and series regions have different n offsets/slopes. Do not call ABAB/ABCA/ABCB from a single peak or a gapped CNP alone. Check the absolute lever arm against fan filling slopes, then revise the calibration if warranted.

7. The first fan covers the electron side where data/6 has clear oscillations and the D=0 gate line reaches high density. It excludes the hole side and displaced-field behavior; after reading it, use a descending-field hole or D-dependent cut only if the electron fan leaves the stacking call ambiguous. Alternate field directions to avoid an unpriced 10 T return. Any elevated-T ladder would require measured settling and the sanctioned `heater.set_both(T, ratio=0.95)` path, and is not committed now.

8. Finish with a region-resolved ana verdict for the measured B₁–B₂ pair, evidence with run ids and numbers, and explicit unresolved physical regions and missing discriminants. Then execute `return-to-initial` and record final readback in session_notes.
