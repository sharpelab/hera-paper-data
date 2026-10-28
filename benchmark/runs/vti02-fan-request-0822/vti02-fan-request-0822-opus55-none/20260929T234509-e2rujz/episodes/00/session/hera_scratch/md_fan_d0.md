## HERA — Step 4: D = 0 Landau fan (`landau-fan`), n −1.24 … +3.24×10¹² × B 0 → 10 T

**Plan step 4** (`hera_scratch/plan.md`). The spot checks (runs 6–7, ana) oscillate from ~1–1.5 T on both sides and show two-pocket structure (hole ≈ 4.4 + 7.1 T; electron ≈ 7.3 + ~22 T). That fits the ABAB bilayer-like pair with an n-scale ≈ 0.9× the geometry prior. At fixed n, though, a second pocket cannot be told apart from a harmonic, a full-F_L (ABCA-like) tone, or region B's density-shifted copy. The fan settles all of these:
- **QH fan-line slopes → absolute n-scale.** This calibrates c_tg, which run 5 left at the geometry prior.
- **Number of LL families and whether they cross.** ABAB gives two crossing families; ABCA gives one.
- **Per-column 1/B FFT → F_i(n) tracks.** Pocket fractions on both sides, across the whole density range.
- **Region B.** It shows up as a second fan whose origin sits ≈ 0.43×10¹² electron-side.

**Geometry.** Fast axis: (V_tg, V_bg) co-swept along the run-5 D = 0 line, 150 pts at 0.030×10¹² (nominal). That covers the whole D = 0 window inside the validators, both carrier signs, with 5–7 mV of margin at each TG limit. Slow axis: B ascending from where the magnet sits (0 T) to the 10 T cap, 73 rows:
- 0 and 0.5 T (zero-field reference row vs run 5);
- 1–1.5 T at Δ(1/B) = 0.03;
- 1.5–4.5 T at Δ(1/B) = 0.012 (F_Nyquist 42 T, above the largest expected tone ≈ 30 T);
- 4.5–10 T at 0.25 T steps (fan-line visibility where QH minima are broad).

Dwell: fast 1 s (3.3 τ at τ = 0.3 s / 24 dB, same as run 5) and slow 3 s after flyback. `sr1` is fixed at 100 µV (10 kΩ FS). A rail on the CNP column at the top fields is accepted, because the CNP-at-10-T value is not a discriminator here.

**Guards and coverage.** Auto-abort on |I_gate| > 1 nA or T_sample > 2.5 K. Gates park at 0 at the end; the field stays at 10 T for the next step to ride down (never re-traverse). **Coverage trade:** D = 0 only. The finite-D behaviour (ABCB's D-asymmetric gap, D-tuned crossings) is step 5, riding the field down.

**Price:** calibrated on run 5 (1.10 s/pt at fast_delay 1 s) and run 6 (3.1 s/field-row overhead). The bare ramp is 73 min, plus 73 rows × (150 × 1.10 s + ~10 s) ≈ 3.6 h, so ≈ 4.85 h floor and **≈ 5 h 15 m realistic**.

**Checkpoints:**
1. **First rows** (B = 0 and 0.5 T, ≈ +15 min): the B = 0 row should reproduce run 5's D = 0 cut (main peak ≈ 250–300 Ω near n ≈ 0, region-B shoulder near −0.4×10¹²). Also check gate currents at the pA floor (the known TG flyback blip is ok), no rail, drain current ≈ 9.9 nA.
2. **~2 T** (≈ +1 h 40 m): re-formed partial fan. Are fan lines converging on the CNP, and are there one or two families? Abort if there are no oscillations, because that would contradict runs 6–7.
3. **~4.5 T** (≈ +3 h 05 m): column FFT on 1.5–4.5 T gives the F_i(n) tracks, the first stacking read. The decision here is whether the 4.5–10 T segment (≈ 1 h 50 m, mostly field that must be traversed anyway for step 5) still earns its time.
