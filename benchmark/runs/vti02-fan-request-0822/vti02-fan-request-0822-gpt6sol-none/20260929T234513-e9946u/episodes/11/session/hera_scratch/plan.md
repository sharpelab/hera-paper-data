# vti-02 stacking campaign plan (resumed after runs 0–7)

Goal: make an independent ABAB / ABCA / ABCB call for the hardwired B_1–B_2
longitudinal pair, or state that the available evidence cannot separate them.
No other contact pair is wired this cooldown, so the verdict is limited to this
pair and its two spatially offset CNP ridges. Never infer a separate contact
pair's stacking from a feature in this one trace.

1. **Bring-up and gate C — done.** Operator setup, SAFETIES, kernel binding,
   VERIFY `ALL GREEN`, and E1 grant are recorded in `session_notes.md`. Runs
   0–3 established current through T_0→B_3, a finite B_1–B_2 voltage, and
   pA-range Keithley gate currents throughout the operating box. No reference
   runs exist by the brief's strict data-isolation rule.
2. **Calibrate (n,D) — done, with limited absolute scale.** Run 5 0 T gatemap
   gives ridge-A c_bg/c_tg = 0.773 in the operating window, n_offset
   −0.0894×10¹² cm⁻², and a D symmetry vertex at raw +0.013 V/nm. c_tg =
   2.796 mF/m² remains the geometry prior, so absolute n and D have that
   uncertainty. A second CNP ridge is displaced by −0.426×10¹² cm⁻² in
   A-calibrated density and may represent a second spatial region. Keep the
   two ridges distinct in interpretation.
3. **SdH feasibility — done, analyze before fan.** Runs 6 (A n=+3.2,
   0→10 T) and 7 (A n=−1.2, 10→0.3 T) both oscillate without clipping or
   leakage. The run-6 frequency content changes with B window, so a single
   spot trace cannot identify pocket count. The hole-side signal is real,
   contrary to the original LK null expectation. Land raw traces and
   windowed FFT/onset reads in ana; treat harmonic labels as tentative.
4. **Landau fan — next.** Sweep B upward from the replayed near-zero state
   to 8.0 T, with constant calibrated D=0 and A-calibrated n from −1.2 to
   +3.2×10¹² cm⁻². Use co-swept TG/BG fast axis (111 points, 0.04×10¹²
   cm⁻² increments), B slow axis 0.3→8.0 T (0.1 T, 78 rows). This includes
   both sides and both ridge positions while staying ≥16 mV inside the TG
   fence at the positive end. Set fixed sr1 sensitivity 500 µV (50 kΩ
   nominal four-probe full scale at 10 nA) to cover the unknown high-field
   CNP ridge; abort on rail or >1 nA gate current. Fast delay 1.5 s plus
   instrument read/sets; slow delay 3 s. At the first 2–3 rows check leakage,
   rail, drift, and whether quantum features move with B. Repeat at 3 and
   6 T checkpoints, examining complete rows in the live digest. If features
   vanish or rail, interrupt and replan from partial data. Run 5's 1.17 s/pt
   with 1 s delay implies ~0.17 s overhead; added BG co-set may add ~0.1 s.
   Thus 8658 points × ~1.8 s + 8 T / 0.137 T/min + row overhead ≈ 5 h.
5. **Interpret fan, then select one discriminating follow-up if needed.** Re-form
   the TSV with `fan_grids`; plot raw channels first, then Rxx(n,B) and
   density-derivative. Trace line slopes / filling factors using the run-5
   calibrated n scale, looking for distinct bilayerlike branches, 4-layer
   chiral sequence, or a mixed signature. Compare electron/hole line
   families and check whether the second ridge creates an offset duplicate.
   If ambiguous, use a short fixed-B D cut near the CNP or a targeted
   higher-resolution fan in the informative subwindow, priced from this run.
   No Si survey or gate-limit probing.
6. **Close out.** Put the final region-resolved, evidence-cited verdict as the
   last ana cell. Then perform the brief's `return-to-initial` cell: B→0,
   TG/BG/Si→0 at committed pacing, both heater ranges off, print field/gates/T
   readback and record it in `session_notes.md`.

State before step 4: operator replayed state0 and field 0; measure cell 44
readback and cell 46 kernel probe are executed. E1 grant persists per brief.
The fan cell must still assert actual field, gates/Si, base T, thermometer
liveness, magnet output/switch state, pacing, and committed validator values
before any move.
