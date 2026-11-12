# vti-02 stacking investigation — current plan

## State and calibration
Gate A/B and VERIFY passed; E1 grant is recorded in `session_notes.md`. Gate C passed in runs 0–3. Run 5 supplied two near-parallel CNP ridges. Ridge A sets the working calibration: c_bg/c_tg = 0.773, n_offset = -0.0894 (10^12 cm^-2), D_offset = -0.013 V/nm; absolute density still uses the 9.5 nm TG geometry prior. Ridge B has a relative offset about +0.43 (10^12 cm^-2), so this hardwired B_1–B_2 pair may contain a series mosaic. Runs 6–7 probed SdH at n_A = +3.2 and -1.2 at D_A = 0, with visible oscillations and no clipping/leakage.

## Step 1 — bring-up and calibration: done
Use cheap gate checks, then a 0 T TG/BG map to locate the CNP lines and D = 0 symmetry. Revise the calibration if fan line slopes disagree with the run-5 ratio. Do not treat the geometry-prior absolute density as fully calibrated until fan filling slopes test it.

## Step 2 — spot SdH: done
Runs 6 and 7 bound useful field onset and tone content at both density signs. The electron trace has ~7 and ~30 T structure; the hole trace has ~5 and ~12.5 T structure. Distinguish distinct pockets from harmonics and from the second CNP region by their density dependence in a fan; a spot FFT alone does not determine stacking.

## Step 3 — Landau fan: next
At base T, Si = 0, sweep B from 1.5 to 10 T while co-sweeping TG/BG along the run-5 D_A = 0 line from n_A = -1.2 to +3.2 x 10^12 cm^-2. Use 0.04 density spacing and 0.2 T field spacing (plus 10 T end point). This covers both carrier signs and both offset CNP lines within the committed gate validators. Read first rows for leakage, signal and clipping; then review periodically at ~3, 5, 7, 10 T. If high-field R rails, stop and repeat the remaining segment at higher sensitivity range. If features are absent or too blurred, analyze the partial fan before spending the rest of the traverse. B-axis sampling is for LL trajectory tracking in density cuts; field FFT resolution comes from runs 6–7. **Landed as measure cells 47–48. The CLI PreToolUse hook returned `episode complete` when E1 execution was attempted, so the cell is unexecuted and no fan data exists yet.**

## Step 4 — interpretation and follow-up
Re-form the raw fan via `fan_grids` and `resistance_grids`; plot raw Rxx and current before subtraction/derivatives. Extract LL line slopes, neutrality crossings, approximate degeneracy and sequence, and compare A/B ridge offsets. The decisive distinctions are whether the fan has two bilayer-like ladders (ABAB), a single chiral-4 ladder (ABCA), or mixed monolayer/trilayer-like ladders (ABCB). Check whether frequencies and line families move with the ~0.43e12 ridge-B offset. If ambiguous, choose the least costly targeted density/D cut or an elevated-T check justified by the observed gap; otherwise write a calibrated `cannot tell` with the resolution limit. Do not infer stacking from a D-tunable gap alone.

## Step 5 — close-out
Return field and TG/BG/Si to zero with committed pacing, turn both heater ranges off, print actual field/gate/T readbacks and record them in `session_notes.md`.
