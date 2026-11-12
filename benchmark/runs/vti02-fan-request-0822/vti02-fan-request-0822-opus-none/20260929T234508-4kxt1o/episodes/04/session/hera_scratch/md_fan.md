## HERA — Step 4: Landau fan (`landau-fan`), D = 0, n = −1.20 … +3.20×10¹², B 0.8 → 9.0 T

**Plan step 4 — the decisive run.** Runs 6/7 are worked up for the first time this
turn (`hera_scratch/ana_spot67.py`, `ana_index67.py`; ana cells to follow). Both
spots oscillate hard — Rxx → 0 minima from below 1 T — but a **consecutive-Landau-index
fit fails at both** (rms residual 87 % of a period at n = +3.2, 52 % at n = −1.2),
so neither spot is a single frequency. The provisional two-tone read is
F ≈ 7.0 + 24.6 T = 31.6 T against F_L = 33.1 T at n = +3.2, and ≈ 3.4 + 9.5 = 12.9 T
against F_L = 12.4 T at n = −1.2: the **sum rule nearly closes at both signs with a
stable ≈ 3 : 1 partition** — the ABAB (two bilayer-like subbands) template rather
than the ABCA singleton. But a single spot cannot separate fundamentals from
harmonics, and these minima are square (Rxx → 0), so the harmonic content is strong:
7 / 14 / 22 / 29.5 T is equally readable as one tone plus 2×/3×/4×. **Only F(n)
resolves it** — fundamentals scale through the CNP and obey the sum rule at every
density; a mis-split does not. That is this run.

**Geometry.** B slow × n fast at D = 0 (`multimegasweep`, co-swept V_tg/V_bg). Field
is the blocking axis, so it is swept once, monotonically, ascending from where the
magnet sits (0 T) — a descending fan would cost an extra 66 min ramping to 9 T first,
and its partial data (high-B only, dF = 7.2 T) could not separate the tones, whereas
this one's partial data can from ~2.5 T onward. **111 rows uniform in 1/B** (not in B):
that is what `sdh_fft` wants un-resampled, it puts the rows where the oscillations are,
and it sets F_Nyquist = 48.3 T — above 2×F1 ≈ 50 T only marginally, so a 2nd harmonic
of the heavy tone at the electron end may alias near 38 T and will be labelled, not
read. FFT resolution dF = 0.88 T, set almost entirely by B_lo = 0.8 T (B_hi buys
almost none: 6 T would give 0.92 T) — B_hi = 9.0 T is bought for the low-filling-factor
physics at the CNP instead, and costs only 22 min of ramp and ~5 % of the rows.
**89 fast points, Δn = 0.05×10¹²**; the endpoints are *exactly* runs 6 and 7's spot
densities, so the fan's two end columns are a direct cross-check against a
3 s/point, fully-settled record.

**Coverage trade, stated.** n stops at +3.20 and −1.20 (not the realized ±window
edges +3.27 / −1.27): V_tg is the binding limit at both ends and +3.25 would sit
1.5 mV from the +1.0 V validator. The excluded slivers are 2 % of the range and
carry nothing the rest does not. Nothing is excluded in D — this is a D = 0 cut only,
and the D-dependence (the other stacking lever) is deliberately **not** measured here;
pricing it is a separate call after this lands.

**Sensitivity — 500 µV (50 kΩ FS), the run-4 lesson applied forward.** Run 4 railed
because the *map's* worst corner, not the 1D peak, sets R_max; here the worst corner
is the CNP at 9 T, which arrives **last** and is unmeasured. Headroom is therefore
bought up front: 50 kΩ is 16× the largest R this device has shown (3.07 kΩ, run 5 at
high D). The usual cost of over-ranging does not apply — measured σ_V is 20 nV at
100 µV (run 5) and 37 nV at 50 µV (run 6), i.e. **noise here is environment-limited,
not range-limited**, so σ_R should stay ≈ 2–4 Ω against SdH amplitudes of 50–500 Ω.
That extrapolation is 5× beyond the measured points, so the first-rows checkpoint
measures σ_R directly and kills the run inside 10 min if it is wrong.

**Dwell.** `fast_delay = 1.0 s` — run 5's value (calibrating run: 1.098 s/pt measured),
which resolved the CNP ridge to 19 mV rms. It is 3.3τ at τ = 0.3 s / 24 dB/oct, i.e.
**under the settling floor, knowingly**: the primary read is the per-column FFT along
1/B, and the fast-axis lag is a near-identical function of column position in every
row, so it largely cancels there. It costs fast-axis sharpness at the low-B end —
where ν = 4 lines are 1.5 fast steps apart (B = 0.8 T) and unresolvable on any dwell.
`slow_delay = 2.0 s` covers the 1.26 V flyback at the start of each row (3.2 s total
before the first fast point ≈ 10τ).

**Price.** 438 s/T × 9.0 T of traversal (measured: run 6 fit dt = 437.6·dB + 3.09 s)
= 66 min, + 111 × 89 × 1.10 s = 3 h 1 m, + 111 × 7.6 s row overhead = 14 min →
**4 h 21 m nominal, ≈ 4 h 40 m realistic** (this session's runs have come in 5–10 %
over). Ends at **9.0 T with the gates at n = +3.20** — the electron spot, matching
run 6, so a follow-up rides the magnet down rather than re-traversing.

**Checkpoints** (all read off the armed `hera-watch` digest):
1. **First 2 rows** (~10 min, after the 6 min ramp-in to 0.8 T): σ_R at 500 µV — abort
   and re-run at 200 µV if σ_R > 15 Ω; plus rail check, leakage, and the CNP visible
   near column 24 (V_tg ≈ +0.067).
2. **≈ 2.5 T** (~1 h 20 m): per-column FFT on the landed rows — is the two-tone
   structure resolving, and is the CNP column trending toward the 50 kΩ rail?
3. **≈ 5 T** (~2 h 50 m): sum-rule check on landed data, extrapolate the CNP
   resistance to 9 T; continue / stop with the remaining cost priced.

Leak guard as in runs 6/7 (1 nA) but requiring **two consecutive** over-threshold
points: run 5's flyback transient reaches ±200 pA on the TG current every row
(session_notes TOOLING), and a single-point spike must not kill a 4 h 40 m run.
