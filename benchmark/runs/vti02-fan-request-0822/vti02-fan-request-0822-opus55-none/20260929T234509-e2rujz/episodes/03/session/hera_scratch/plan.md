# vti-02 stacking call — plan

*(Written 2026-08-23 ~05:30 by the incoming instance at the handoff. The previous instance ran steps 0–3 without committing a plan.md; steps 0–3 below are reconstructed from the notebooks and session_notes.)*

## Goal
ABAB vs ABCA vs ABCB for the single measured pair (sr1 = B_1−B_2, source T_0 → drain B_3), an evidence-cited verdict in the ana notebook.

## Discriminators (what each stacking predicts, as accessible on this rig: T_e ≈ 8 K, |B| ≤ 10 T, D limited to roughly −0.08…+0.30 V/nm on the CNP)
- **ABAB (Bernal)**: two bilayer-like bands (λ = 1.618 / 0.618 → heavy / light). This gives **two SdH tones** at every n (light pocket F_l ≪ F_L, heavy F_h ≈ F_L − F_l) and **two interpenetrating LL families** in the fan, meaning many LL crossings and ν-dependent gap closings. The light pocket reaches its **quantum limit at B ≈ F_l**, which shows up as a feature line in the fan. D does not open a large CNP gap (semimetal overlap), so R_CNP stays modest.
- **ABCA (rhombohedral)**: a single band (E ~ k⁴), **one tone at F_L** (m* ~ 0.07 at n = 3e12). A clean single-family fan above the zero-energy manifold, a **16-fold zeroth LL (robust ν = ±8 first gaps)**, and a **large D-induced CNP gap** (R_CNP going insulating by 0.3 V/nm at 1.2 K).
- **ABCB (mixed)**: an intrinsic gap / polarization at D = 0, so R_CNP(D) is asymmetric with its minimum at finite D. Its LL spectrum mixes a bilayer-like and a monolayer-like/trilayer-like set.

## Steps
0. **Gate C** (runs 0–3). Done: alive, no leakage, Rxx 60–330 Ω.
1. **0 T gatemap + calibration** (run 5; run 4 aborted). Done: ratio 0.773, c_tg 2.796 mF/m² (prior anchor), n_offset −0.089e12, D_offset −0.013 V/nm. There is a second parallel ridge B at n_A ≈ −0.43e12 (a series region). R_CNP climbs from 297 Ω (D ≈ 0) to 2.4–3.1 kΩ (D ≈ +0.25–0.3): about 10×, not insulating.
2. **Feasibility table** (previous instance, in the cell 39/41 markdown).
3. **SdH spot checks at D = 0** (run 6: n = +3.2e12, 0→10 T; run 7: n = −1.2e12, 10→0.3 T). Done, analysed in scratch (`ana_sdh67.py`). The run 6 SdH analysis shows **two independent tones, 7.2 T (onset < 0.5 T, light) + ~30–31 T (heavy)**, plus Rxx zeros (QH) from ~3.5 T. There is an Rxx step-up at 7.5–8 T ≈ F_l, a plausible light-pocket quantum limit. Run 7 has a 6.8 T tone with harmonics, near the ABAB model (5.3/7.1). **Leans ABAB.** Not yet landed in ana; land it while step 4 runs.
4. **Landau fan at D = 0** (`landau-fan`) ← **NOW**. multimegasweep: B slow 0→8 T (0.05 T to 1.5 T, 0.1 T to 8 T; 96 rows), (Vtg, Vbg) co-swept fast along D = 0, n −1.25…+3.25e12 in 0.025e12 steps (181 pts). ≈ 7 h. This step establishes:
   - Is it one LL family or two (crossings)? This is the primary ABAB/ABCA discriminator.
   - Does the light-pocket quantum-limit line B_QL(n) ≈ F_l(n) run across the whole electron side?
   - The ν sequence near the CNP (ν = ±8 robust → ABCA; lower-ν gaps with crossings → ABAB).
   - Whether a second fan origin comes from region B (n_A ≈ −0.43), which is the region caveat.
   - A cross-check of the capacitance scale: fan-line slopes give c_tg directly (Luttinger), fixing the ~12% F_L mismatch in run 6.
   - Ends at 8 T. Next steps start there; no re-traverse.
5. **Finite-D follow-up at high field** (planned, depends on 4). Either an (n, D) map at 8 T over the accessible D window (LL crossings vs D; the ABCA zeroth-LL layer-polarization transitions), or a descending fan 8→0 T at D ≈ +0.2 V/nm. Pick from 4: if crossings are rich, the (n, D) map at 8 T (cheaper, ~2 h). If 4 already shows a single family, the descending finite-D fan tests the gap.
6. **Verdict** in ana (output contract), then close-out `return-to-initial`.

## What would change my mind
- The fan shows **one LL family** with ν = ±8 as the first robust gaps and no crossings → ABCA, overriding the run 6 two-tone read (the 7.2 T tone would then have to be region B or a harmonic artefact).
- R_CNP(D) minimum demonstrably offset / asymmetric plus a D = 0 gap in the fan (ν = 0 insulating at low B) → ABCB.
- The fan dominated by two offset origins (A and B regions) at comparable weight → the per-region verdict splits, or becomes "cannot tell" for B.
