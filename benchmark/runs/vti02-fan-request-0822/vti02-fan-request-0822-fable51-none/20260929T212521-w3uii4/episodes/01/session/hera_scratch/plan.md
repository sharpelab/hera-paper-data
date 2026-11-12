# vti-02 — plan (stacking order: ABAB / ABCA / ABCB), written 2026-08-23 05:30 by the second HERA instance

Goal: an evidence-cited, region-resolved call on the stacking order of the tetralayer, from the single hardwired
Rxx pair (sr1 = B_1−B_2, drain B_3, source T_0). Only inputs: this session's data. The first instance left no plan
file; this reconstructs the arc it followed (steps 0–3 done) and sets the rest.

## What discriminates the three stackings (the read I am building toward)
- **ABAB (Bernal)** — two bilayer-like massive bands (light + heavy) both touching at E = 0 at D = 0. Signatures: two SdH
  frequencies at fixed n with F_l + F_h = F_L = n h/(4e) and different n-dependence; in the fan, two interpenetrating
  4-fold LL ladders → gaps of irregular strength that close and reopen along level-crossing lines. Semimetallic
  band overlap near the CNP is possible; D opens a gap (moderately).
- **ABCA (rhombohedral)** — one flat quartic-ish band, single 4-fold Fermi surface: one SdH tone at F ≈ F_L (for a
  simply connected FS; trigonal warping can fragment it at low |n| — then 3 pockets), a 16-fold zero-energy LL
  (first plateaus at ν = ±8, then ±12, ±16 …), regular monotonic gap sequence, strongly D-tunable gap (a few kΩ →
  insulating at modest D); no crossings between two ladders.
- **ABCB (mixed)** — no inversion symmetry: an **intrinsic** gap at D = 0 (~10 meV scale) and an asymmetric R_CNP(D)
  (minimum displaced from D = 0); band structure ≈ monolayer-like + trilayer-like pieces → a 2-fold-ish fast ladder
  plus a heavy set. Run 5 shows R_CNP(D) symmetric with a 297 Ω minimum at D ≈ 0 — weak evidence against, not
  decisive (mosaic/disorder can shunt a gap).
- **Confounds carried:** two series regions (A dominant, B electron-doped by 0.43×10¹² relative, same lever arms)
  → a second, shifted copy of every feature; only one Rxx pair (no Rxy, no second region); T_e ≈ 8 K claimed
  for the rig (run 6 shows QH zeros from 2 T, so the device is better than that number suggests).

## Steps
0. Gate C — liveness, gate-current sanity (runs 0–3). DONE: alive, 60–330 Ω, no leakage.
1. 0 T gatemap → CNP line + (n, D) calibration (run 4 aborted/railed, run 5). DONE: c_bg/c_tg = 0.773 (data),
   c_tg = 9.5 nm prior, n_offset −0.089×10¹², D_offset −0.013 V/nm from R_CNP(D) symmetry. D = 0 line inside the
   validators spans n = −1.28 … +3.26×10¹² (TG-limited). Second ridge B (mosaic).
2. Feasibility table (F_L, m*, LK at T_e) — done in the run 6/7 proposal markdown.
3. SdH spot checks at D = 0: e-side n = +3.2×10¹² (run 6, 0→10 T), h-side n = −1.2×10¹² (run 7, 10→0.3 T). DONE, read
   landed in ana this instance: QH regime from ≈ 2 T; run 6 zero sequence aperiodic in 1/B (paired zeros), FFT 7.1 T
   + 16/23/30 T (harmonics or a second band — undecidable from one column); run 7: 12.3 T = F_L(1.2×10¹²) to 1 % →
   density scale good to ≲ 12 %. Sensitivity 50 µV fine (max fs 0.12).
4. **Landau fan at D = 0 (this step, operator-requested).** Slow B 1.0 → 10 T (0.05 T to 3 T, 0.1 T above; 111 rows),
   fast n = −1.25 … +3.25×10¹² co-swept (Vtg, Vbg) along D = 0, 141 pts (Δn = 3.2×10¹⁰), fast_delay 1 s, sr1 100 µV
   (10 kΩ FS). Establishes: (a) ν of every Rxx minimum from the lines converging on n = 0 → the LL degeneracy
   sequence and which gaps exist (ABCA: 16-fold zero LL then 4-fold; ABAB: two ladders with crossings); (b) per-column
   sdh_fft → F(n) for each tone: a harmonic sits at exactly k×F for every n, a second band has its own F(n) slope;
   (c) the density scale from the ν-line slopes (lever-arm check closing the calibration); (d) the mosaic copy
   (second CNP at n_A = −0.43×10¹²). Ends at 10 T. ≈ 7 h.
5. Read the fan; decide the follow-up that most sharpens the call, riding the magnet down from 10 T:
   - if two ladders/crossings → ABAB-leaning; confirm with a finite-D fan or a fixed-n T-ladder (LK masses of the
     two tones — ABAB masses ~0.03/0.06 mₑ vs ABCA ~0.07+).
   - if a single ladder with 16-fold zero LL and monotonic gaps → ABCA-leaning; confirm with R_CNP(D, B) (gap vs D
     at fixed B) and the low-|n| pocket structure.
   - if the CNP is gapped at D = 0 at all B and the ladder is 2-fold-ish → ABCB candidate; test R_CNP(D) asymmetry
     and T-dependence of R_CNP at D = 0 (activated?).
6. Verdict cell in ana (per-region: only the B_1–B_2 pair is measured; region B appears only as the mosaic copy),
   evidence with run ids and numbers, hedges. Then `return-to-initial` close-out on the operator's ask.

## What would change my mind / abort criteria for step 4
- First rows: sr1 rails on more than the CNP ridge, gate current > 1 nA (guard trips), T_sample > 1.5 K, flat
  sr1 (dead channel) → stop.
- At ~3 T (row ~40): no ν-lines converging on the CNP in the re-formed fan → the D = 0 line is off (D_offset wrong)
  or the fast axis lags too much; abort, re-derive.
- Zack's withdrawal or any safety concern → interrupt (`nb-collab interrupt`), re-read field, drop to E0.
