# vti-02 stacking-order campaign — plan (recreated at 2026-08-23 pickup; plan.md absent at handoff)

Goal: ABAB vs ABCA vs ABCB, one wired region (sr1 = B_1−B_2), evidence-cited call in ana.

## Done
1. **Gate C liveness** — runs 0–3: contacts alive, R(CNP, D≈0) ≤ 330 Ω, no leakage. ✓
2. **0 T gatemap + (n,D) calibration** — run 5 (run 4 railed, aborted): ratio c_bg/c_tg = 0.773,
   c_tg anchored 9.5 nm prior, n_offset −0.089e12, D_offset −0.013 V/nm. D=0 window inside
   validators: n = −1.27…+3.27e12 (TG-limited). Second parallel ridge B: mosaic region at +0.43e12.
   D-tunable CNP gap on ridge A (240 Ω at D≈0 → 2.4 kΩ at |D|≈0.25 V/nm) — parent-ambiguous, not a
   stacking read alone. ✓
3. **SdH spot checks** — run 6 (e-side n=+3.2e12, B 0→10 T), run 7 (h-side n=−1.2e12, 10→0.3 T).
   Analysis landed 2026-08-23 (this pickup): e-side dominant F≈7.1 T + harmonics ×2,3,4 and
   independent weight ~22–26 T; total expected 33.1 T. Two-band (light+heavy) partition plausible
   (ABAB-like) but harmonics vs genuine heavy band unresolved at one density → fan. h-side tones
   4.7 / 6.6 / 8.5 / 12.3 T vs expected total 12.4 T — multi-tone, near-CNP regime. ✓

## Now
4. **Landau fan at D = 0** (operator-requested, the stacking dataset) — run 8:
   slow B uniform-in-1/B 0.5→10 T, 220 rows (ΔF res 0.53 T full-window, Nyquist 58 T);
   fast n co-swept (TG,BG) along calibrated D=0, −1.26…+3.24e12, 91 pts (Δn=0.05e12);
   sr1 100 µV (10 kΩ FS; CNP column may clip at high B — accepted, positional info kept).
   ~9 h. Deliverables: per-column FFT → F(n) tone map; slopes vs h/(g e)·n → per-band degeneracy;
   harmonics separate from bands by slope; band-edge kinks; high-B filling-factor sequence; CNP
   gap vs B. Mosaic ridge-B tones at ×1.13 n — watch for doubled slopes.

## Then (contingent on fan)
5. Discriminators the fan read is expected to set up: which model's F(n) partition fits
   (ABAB: two bilayer-like bands; ABCA: single heavy band + flat-band onset; ABCB: mixed
   monolayer+trilayer-like partition). If masses needed: LK T-dependence at chosen (n, B window)
   riding the field down. If CNP parentage needed: R_CNP(D) at fixed high B (cheap, gatemap subset).
6. **Close-out**: `return-to-initial` (B→0, gates→0, heaters off, readback → session_notes).

## Would change my mind
- Fan first-rows railing/leakage → abort, resize sensitivity (lesson of run 4).
- No resolvable second tone anywhere in n → the e-side "heavy band" was harmonic; fall back to
  LK masses + CNP-gap phenomenology, call may be weaker.
- F(n) slopes inconsistent with any 4-fold partition → consider mosaic contamination (ridge B);
  restrict columns or re-fit with two-region model.
