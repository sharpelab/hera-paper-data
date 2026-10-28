## HERA — Step 4: Landau fan at D = 0 (`landau-fan`) — the stacking read

**Why this, now (plan step 4).** Steps 1–3 got us a calibrated D = 0 line and two 1-D SdH
spot checks (runs 6, 7), and those spot checks are exactly as far as a fixed-density
measurement can take the stacking question. Their spectra (analysed at the handoff,
`hera_scratch/ana_sdh_spots.py`, landing in ana alongside this run) contain two families:
a branch **near the full-density Onsager value** — 29.6 T at n = +3.2×10¹² where
F_L = 33.1 T (run 6), 12.2 T at n = −1.2×10¹² where F_L = 12.4 T (run 7) — and a dominant
**~7.0 T tone that appears at *both* densities** with its 2×/3×/4× harmonics. A real Fermi
surface of the gated channel cannot hold frequency while n changes by 2.7×, so one of these
families is not a band. A 1-D spot cannot tell which. Sweeping n *is* the discriminator, and
it is the same measurement that answers the campaign question, so it is the next step and not
a detour.

**What the fan decides.** All three candidate stackings carry total chirality 4, so the
CNP zero-LL degeneracy (16) is *not* a discriminator — the partition of density among Fermi
surfaces is. Per-column FFT in 1/B gives F(n) directly: **one** branch on F = |n|h/4e →
ABCA; **two** branches summing to it → ABAB (comparable fractions, two J = 2 bands) vs ABCB
(strongly asymmetric, J = 1 + J = 3). Three things come free and are worth as much as the
headline: (i) any density-*independent* branch — the ~7 T tone — shows up as a horizontal
line in the F–n plane and is diagnosed rather than guessed; (ii) the **series mosaic**
(runs 0–3, 5: two CNPs between B_1 and B_2, Δn ≈ 0.43×10¹²) resolves into one apex or two,
which is the standing confound on any two-frequency read; (iii) the LL line slopes
dn/dB = νe/h **calibrate n absolutely**, retiring the 9.5 nm geometry prior that is currently
our largest systematic (and is the natural explanation for run 6's 11 % F-vs-F_L shortfall).

**Geometry and why each number.** n fast along the D = 0 line, −1.25 … +3.24×10¹² cm⁻²,
113 points (0.040×10¹² steps — 23 points per ν = 4 period at 10 T); the span is the whole
D = 0 line the validators allow, TG-limited at both ends, and it is deliberately both carrier
signs so the apex and both fans are in one map. B slow, **uniform in 1/B** (`field_invB`) —
SdH is periodic in 1/B, and uniform-in-B sampling fine enough to Nyquist a 33 T fundamental
at the low-field end would need ~5 mT steps and 1700 rows. 109 rows over 1.0 → 10 T gives
d(1/B) = 0.00833 /T → **Nyquist 60 T** (above the 33.5 T largest fundamental *and* above the
37.9 T a 1.13×-density mosaic region would sit at, so the two cannot alias onto each other)
and **FFT resolution Δf = 1.11 T** — 3–4× finer than the splittings any of the three
stackings predicts here. One extra **B = 0 anchor row** leads the fan: it reproduces the run-5
D = 0 cut for ~2 min of beam time and is the first-rows checkpoint below.

**Coverage trade, stated.** Two things are bought out of this fan deliberately. (1) The
window starts at **1.0 T, not 0.8 or 0.6** — lower B_lo buys frequency resolution (Δf 0.87 T
at 0.8 T) but at fixed Nyquist costs rows that land where oscillation amplitude is smallest;
1.0 T sits just above the measured onsets (0.71–1.3 T for the strong tones, runs 6–7) and saves
~50 min. (2) **Sensitivity is fixed at 100 µV (10 kΩ FS)**, run-5 gatemap parity — this favours
SdH contrast at 1–3 T (noise σ ≈ 7 Ω at this range, against oscillations of a few tens of Ω)
over headroom at the CNP column at high B, where a ν = 0 state could exceed 10 kΩ and clip.
That is the right way round: the evidence lives in the LL lines away from the CNP, run 5
already locates the CNP at B = 0, and the fan lines extrapolate to the apex anyway. If the CNP
column does clip, the magnet is already at 10 T and a short high-B top-up at 500 µV is cheap;
buying that headroom up front would cost the low-field signal, which is not recoverable.
Ascending in B (the magnet is at 0) also means we never re-traverse — the fan pays the 10 T
traverse once, and the next step starts from 10 T.

**Price.** 12 430 points × 0.92 s (fast_delay 0.8 s = 2.7 τ at τ = 0.3 s / 24 dB — run-5
parity within 10 %, knowingly under the 7–10 τ floor; the resulting lag is a common-mode shift
along n, identical for every row, and does not touch the line *slopes* the call rests on)
= 3.2 h, plus the 10 T traverse 73 min, plus 110 × ~9.5 s row turnaround = 17 min →
**≈ 4 h 40 m**, quoted at 5 h 15 m against this session's habit of running 5–10 % over.
Ends at **10 T, gates at 0**.

**Checkpoints.** (1) **Row 0, B = 0, ~4 min in** — must reproduce run 5's D = 0 cut: CNP within
±0.15×10¹² of n = 0, R_CNP ≈ 240–330 Ω, no clipping, gate currents at their pA offsets. A CNP
off that mark means the calibration moved across the handoff and the fan is mis-centred —
abort there, it is the cheapest kill. (2) **~1.5 T (row ~40, ~1.2 h)** — first per-column FFT on
the landed rows: is there frequency content that *moves with n*? If nothing tracks n by 1.5 T,
the fan is answering a different question than we think and I stop and reassess. (3) **~3 T
(row ~80, ~2.6 h)** — partial F(n); check the CNP column for clipping and decide on the high-B
top-up. (4) Completion. Leak guard trips the run at 1 nA on either gate (the ±200 pA row-start
flyback transient noted in session_notes is well clear of it).
