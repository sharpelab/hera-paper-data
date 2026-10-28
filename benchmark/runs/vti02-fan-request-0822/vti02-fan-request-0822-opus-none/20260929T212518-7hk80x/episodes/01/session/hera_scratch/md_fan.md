## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — the stacking read

**Why this, now (plan step 4).** Runs 6/7 (`hera_scratch/ana_spot.py`, landing in ana
next) came back with strong SdH: onset **below 1 T** (0.40 T censored at the record
edge, electron side; 0.65 T, hole side), 20–100 Ω pk-pk against a 12–460 Ω
background. The electron spot's tone ladder is **7.1 / 14.1 / 22.2 / 29.5 / 57.9 /
89.2 T** against F_Luttinger = 33.1 T — and a 1D FFT cannot tell whether that is
*one* anharmonic fundamental at 7.1 T with its harmonics (⇒ ABCA-like, one Fermi
surface carrying the full density, once the ~10 % lever-arm prior is absorbed) or
*two* Fermi surfaces at 7.1 + 22.2 ≈ 29.3 T (⇒ ABAB-like). A fan separates them by
construction: a harmonic subdivides the *same* family (same n-intercept, slopes in
integer ratio), a second Fermi surface is its own family with its own carrier
fraction. That is the measurement the stacking call rests on.

**Read table (what each outcome means).** Two fan families with carrier-fraction
ratio ≈ 2.6 (the λ = 2cos(π/5) : 2cos(2π/5) Bernal decomposition) → **ABAB**; one
family carrying the full density, 4-fold, with a strong ν = 0 at CNP → **ABCA**; two
families at a ratio that is *not* 2.6, with an asymmetric / already-gapped CNP at
D = 0 → **ABCB**. Closure test at every row: Σν_i = n·h/eB — which also re-calibrates
the absolute lever arm, still the 9.5 nm geometry prior (c_bg/c_tg = 0.773 is
data-calibrated from run 5, the overall scale is not).

**Mosaic caveat, stated up front.** `sr1` (B_1−B_2) spans run 5's two parallel CNP
ridges in series, B electron-doped by 0.43×10¹² relative to A. Expect the same family
template twice, offset in n. **Two fan origins ⇒ mosaic; two slope families sharing
one origin ⇒ two bands.** The distinction is read off the B → 0 intercepts, so it is
decidable from this run and not a confound I have to design around.

**Grid.** Fast axis is the full realized D = 0 window, **n = −1.25 … +3.25×10¹²**
(113 pts, Δn = 0.040×10¹²), co-swept (V_tg, V_bg) — 9 mV / 15 mV inside the TG
validator at the two ends, both signs of carrier, CNP included as the fan origin.
Δn resolves 6 points per filling factor at 10 T (eB/h = 0.242×10¹² per ν) and a
4-fold gap down to B ≈ 2 T. Slow axis is B, **uniform 0.25 T from 0 to 10 T** (41
rows) — uniform in B, not 1/B, because the read is line-tracing in (n, B); at
0.25 T a ν = 13 line moves 2 fast points per row, so the lines are traceable.
The magnet ramp (73 min for 10 T) is a fixed sunk cost of *any* fan to the session
cap, so the n sampling and the row count are priced against it, not against zero.

**Coverage trade.** Excluded: |D| ≠ 0 (a second fan at D ≈ +0.2 V/nm is plan step 5b,
contingent), and B > 10 T (the session cap). Finer rows — 0.2 T, 51 rows — would cost
+23 min for structure that is already resolved at 0.25 T above ~3 T, which is where
individual fillings separate; declined.

**Sensitivity — the run-4 lesson applied.** `sr1` at **500 µV = 50 kΩ full scale**,
sized for the one corner nobody has measured: the CNP column at 10 T, which can be
insulating. That headroom is free here — the measured point noise is ≈ 27 nV
(2.6 Ω at 100 µV in run 5, 2.8 Ω at 50 µV in run 6, i.e. **the same in ohms,
independent of the range**) against 20–100 Ω of SdH. Buying range costs resolution
only if the noise scales with full scale, and on this channel it does not.

**Preconditions the cell checks before anything moves** (it sets none of them):
thermometry logfile advancing; T_sample 1.0–1.5 K; |B| < 0.05 T (the fan starts at
0); V_si = 0; PS heater on and output enabled; **both heater ranges 0**; and the
computed (V_tg, V_bg) vectors inside the committed operating box via
`sanitize_tg_bg` — an out-of-box fast axis stops the cell before the first set.
Leak guard at 1 nA on either Keithley, **debounced to 2 consecutive points** so the
row-start flyback charging transient (a few hundred pA — session_notes TOOLING)
cannot kill a 3-hour run on one sample.

**Checkpoints** (I am watching via `hera-watch`, not by eye): **(1) rows 0–1, ~6 min
in** — signal present, nothing railed, leakage clean, and the B = 0 row must
reproduce run 5's D = 0 cut (CNP ≈ 240–330 Ω at n ≈ 0); a mismatch there means the
calibration drifted and I stop rather than spend three hours on a wrong line.
**(2) B ≈ 4 T, ~1 h 20 m** — partial re-form; are fan lines resolvable and how many
families. **(3) B ≈ 7.5 T, ~2 h 20 m** — interim family assignment. Abort criteria:
rails across the window, leak trip, or no resolvable fan structure by B ≈ 5 T — in
which case the read is T_e/disorder-limited and the fallback is the LK mass ladder
(step 5a), not more field.

**Ends at B = 10 T** with the gates at the electron edge; the ride down is the next
step's to spend, not a wasted traverse.
