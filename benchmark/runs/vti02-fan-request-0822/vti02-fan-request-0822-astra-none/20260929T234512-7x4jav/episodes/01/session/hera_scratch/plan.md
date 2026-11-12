# vti-02 stacking campaign — handoff plan, 2026-08-23

Scope: only this session's data; hardwired B_1–B_2 voltage pair, T_0 source,
B_3 drain. E1 grant and VERIFY stand; measure cells 44/46 confirm restored
bring-up state and bound kernel. SAFETIES cell 18 executed [10]: TG [-0.3,1],
BG [-1.3,2], Si [-25,25] V, field [-10,10] T, heater setpoints [0,100] K.
These agree numerically with the card and fit the rig limits. No safety edits,
Si survey, contact rerouting, or gate-pacing changes.

1. **Done — bring-up / Gate C.** Runs 0–3 establish liveness and leakage within
   the provided operating box. The current-carrying pair is B_1–B_2 only.
2. **Done with limitations — CNP and relative gate calibration.** Run 5:
   dominant ridge slope -0.772765, intercept 0.051215 V; secondary ridge
   near nominal density -0.426e12 cm^-2. Use c_tg=0.002796059309 F/m²
   (geometry prior), c_bg=0.002160696465 F/m² (ratio from data),
   n_offset=-0.08937933224e12 cm^-2, D_offset=-0.013 V/nm.
   The resistance minimum is an operational D origin, not independent proof
   of zero internal D. Absolute density remains provisional. Ridge A/B
   are transport features, not independently wired spatial regions.
3. **Done — SdH feasibility, analysis being promoted.** Runs 6/7 span nominal
   n=+3.2/-1.2e12 at nominal D=0. Both complete; current 9.81–9.94 nA,
   R peaks <590 Ohm, gate current magnitude <216 pA. Oscillations justify a
   fan. Multiple FFT features alone cannot separate subbands, harmonics, or
   differently doped series regions. Preserve signed R to avoid rectification
   artifacts; no stacking inference from the inherited model numbers alone.
4. **Next — landau-fan.** Start at actual handoff zero field. Nominal D=0,
   n=-1.2..+3.2e12 cm^-2 in 0.04e12 steps (111 points). B=0,1,1.5 T then
   65 points uniform in 1/B from 2 to 10 T (68 rows, 7548 points). Both
   carrier signs and both neutrality features lie on this line. Hold Si=0,
   heaters off, base temperature; 3 s point dwell for tau=.3 s at 24 dB/oct.
   Sensitivity 100 uV, unchanged 10 nA excitation. Record measured field,
   gate currents, both temperatures, X and phase of sr0/sr1, and gate
   readbacks. Plot every followed channel. Guard leakage, clipping, current,
   temperatures/freshness and field/readback agreement at measurement points.
   First 0-T row repeats a baseline; compare its extrema with run 5 before
   continuing. Check first points and first 3 rows, then each ~30 min and at
   ~4/6 T. Land clean interim/final raw maps and analysis in ana.
   Budget ~9h15 including 73 min bare magnet traverse and conservative
   measured overhead (run 5 gate points 1.10 s at 1 s dwell; runs 6/7 magnet
   points agree with fixed 3 s settle + 438 s/T). Stop on hardware anomaly;
   re-read state and drop E0 if safety-related. Kernel interrupt does not
   stop this supply's active ramp; operator action is required for ramp abort.
5. **Conditional — interpret / targeted discriminant.** Re-form physical
   gate/B maps and measured-current R. Track branches versus density and
   test whether extra features are harmonics or shifted copies across the
   two CNPs. Infer an absolute lever arm only with supported LL degeneracy;
   do not fit a preferred stacking by assuming its degeneracy. ABAB-like
   multi-band branches, ABCA-like single-band behavior, and ABCB-like mixed
   behavior require consistency across density and confounds, not tone count
   alone. If D=0 is non-discriminating, propose a focused D-dependent return
   fan starting from 10 T with explicit rationale/budget; do not auto-commit
   a second full fan. If unresolved, calibrated cannot-tell is acceptable.
6. **Final verdict / close-out.** Final ana cell gives B_1–B_2 verdict and
   strength, run-cited quantitative evidence, overturn conditions and missing
   observations. No separate stacking labels for unisolated ridge domains.
   Ask return-to-initial per brief, then execute authorized close-out and
   record readbacks; Si pacing remains committed.

Coverage trade: excludes dense field sampling below 2 T (existing spot traces
cover it) and D dependence away from the chosen operational origin. At 2 T,
fourfold LL spacing is 0.193e12 cm^-2, ~4.8 density samples; inverse-field
spacing 0.00625 T^-1 gives ~4.2 samples per 38 T oscillation and Fourier
resolution 2.5 T. Harmonics above 80 T alias; narrow broken-symmetry features
are not guaranteed resolved. Extending equally sampled 1/B coverage to .5 T
would require ~240 extra rows and roughly another day of acquisition. The
gate-safe D=0 line spans ~-1.28..+3.26e12; chosen endpoints retain margins.
