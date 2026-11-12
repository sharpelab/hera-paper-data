## HERA — electron-side Landau fan at D = 0, uniform in 1/B, τ = 300 ms

`recipe: measurements/landau-fan-vti.md` — the investigation's **Step 4/5** fan.
Operator-directed: τ = 300 ms, B 1 → 8 T sampled in 1/B, much finer B, 4–6 h,
to firm the call. This is the measurement run 7 could only gesture at.

**What run 7 left unresolved, and how each parameter here attacks it.**

The spot check gave *ABAB (consistent-with)* — a pair at n = +3.0 summing to F_L
within 2% with partition 0.245/0.755 (model ABAB: 0.215/0.785; trilayer excluded
5×), and an F_L tone that is the pair's sum. Three things stopped it being a
call, and this fan is built against them:

1. **Partner tones reproduced in only 3–9 of 18 extraction choices** (vs 15–16/18
   for the dominant tone). → **τ = 300 ms** is the fix. Measured on this device
   at 5 V drive: point-to-point scatter 0.14% of R_xx at τ = 0.3 s vs 0.35% at
   τ = 0.1 s (cells 39/41) — **2.5× the SNR**, aimed precisely at the weak
   partner. Costs 2.1 s/point at the 24 dB/oct settling floor, which is what the
   4–6 h budget buys.
2. **The Luttinger sum closed at only 2 of 4 densities.** → **81 density columns**
   instead of 5. f₁(n) + f₂(n) = F_L(n) across density is *algebraic* — no model —
   and a coincidental match cannot hold across 81 columns. This is the
   investigation's Step-5 partition-robustness test, and it is the strongest
   evidence available without a mass measurement.
3. **The F_L-tone origin split was resolution-limited and therefore unreadable.**
   My high-B half had δF = 10 T against an 8 T tone separation, so "only the F_L
   tone survives at high B" could not be distinguished from "the two tones merged".
   → **Uniform 1/B sampling fixes this structurally.** Splitting the record at
   the 1/B midpoint (B = 1.78 T) gives the two halves **equal** Δ(1/B) span and
   therefore **equal δF = 2.29 T** — against an ABAB pair separation of 17.7 T,
   which is 7.7× that. **Both fundamentals and the sum tone are resolved in both
   halves**, so the breakdown test (does the F_L tone strengthen with B relative
   to the fundamentals?) becomes decisive rather than suggestive.

**Grid — descending, ≥ 100 rows.** B: `field_invB(8.0, 1.0, 101)` — **101 rows
sweeping 8 → 1 T**, uniform in 1/B at Δ(1/B) = 0.00875 T⁻¹. That is finer than
the recipe's *preferred* 1/(3·F_L) = 0.01057 at the top density, giving **57 T
resolvable = 1.81 × F_L** — comfortable headroom above the fastest expected tone.
ΔB runs 0.0088 T at the low-field end to 0.62 T at the top, which is the point:
constant points-per-period in 1/B, and `sdh_fft` receives an already-even record
with no resampling. Usable-record resolution **δF = 1.143 T** against run 7's
2.00 T; the partner tone (6.67 T predicted at n = 3×10¹²) gets **5.8 periods**,
clearing the recipe's ≥ 5.

**Direction is the operator's call and it is the right one.** Starting high and
sweeping down means the traverse home *is* the measurement — the fan ends at 1 T,
a 7 min ramp from parked, instead of ending at 8 T and owing a 58 min ramp. Net
saving against the ascending plan is roughly half an hour of magnet time, and it
is exactly the base recipe's "plan the direction so the fan ends where the next
measurement needs it".

n: 57 columns from **+1.20 to +3.05 × 10¹²** cm⁻² along the measured D = 0 line
(V_bg = V_tg/0.8324), spanning from below into the |n| ≳ 2–3×10¹² window where
the ABAB and ABCA templates separate — so the *trajectory* of the partition is
measured, not just its value at one point. The low end stops at +1.2×10¹² rather
than at the CNP because below that the top of the field range enters low filling
factor (ν ≈ 6 at 8 T) where the SdH frequency picture degrades into quantum Hall,
and those columns would cost time without carrying frequency content.

**Acquisition re-established.** Close-out restored bring-up values, so the cell
sets drive back to 5.0 V (I ≈ 49.2 nA — linearity verified to 0.84% over a 5×
current range, cell 41), τ = 0.3 s / 24 dB/oct on both channels, `sr0` at 200 mV
and `sr1` at **100 µV** (R ceiling ≈ 2 kΩ; the electron flank runs 10–400 Ω, so
the signal sits at ~10% of range rather than the fans' 2% — the recipe's
grainy-FFT warning).

**Cost:** ramp-in from wherever the interrupted close-out left the field up to
8 T ≈ 47 min, traverse 8 → 1 T ≈ 51 min, 101 magnet settles ≈ 5 min, grid
101 × 57 × 2.25 s ≈ 3.6 h. **Estimate 5.43 h, ETA 5h45m** with this rig's
habitual 5–10% over-run. **Ends at 1 T**, leaving a 7 min ramp to close out.

The column count (57, down from the 81 of the ascending plan) is what pays for
the ≥ 100 field rows and the 47 min ramp-in. Δn = 0.033×10¹² between columns is
still far finer than any structure in F(n), so the trajectory test loses nothing.

**Carried caveat, with a useful sharpening.** R_xx still contains ~1% R_xy
admixture and this is again a single field polarity, so no ±B symmetrisation.
But R_xy is periodic in 1/B at the *same* fundamental as R_xx — it distorts the
waveform, adding harmonic content, and does **not** create new fundamental
frequencies. So the pair positions and the Luttinger partition (fundamentals)
are robust to it; the harmonic structure, including the 50.2 and 55.5 T tones
left unexplained in run 7, is not. Any claim resting on harmonics stays hedged.

**Recovering the magnet.** The close-out cell was interrupted mid field-ramp, so
the supply is still heading for 0 T — on this rig an interrupt stops the *cell*,
not the supply, and the only recovery is a fresh blocking set with a new target.
The cell issues that set explicitly (rather than letting the sweep's first slow
point do it silently) so the redirect and its cost are on the page.

**Checkpoints:** first rows for railing/leakage and a per-point re-price against
the 2.25 s assumption; then periodically. Note the descent means the *high-field*
rows land first, so early columns will show the sharpest LL structure but the 1/B
record only becomes long enough to resolve the pair once the sweep has worked
down past ~2 T — per-column FFT is a late-run read, not a halfway one.
