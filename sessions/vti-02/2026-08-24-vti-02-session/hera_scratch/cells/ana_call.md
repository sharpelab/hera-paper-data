# The call — vti-02 stacking order

## 1. Per-region verdict

| region (contact pair) | verdict | strength |
|---|---|---|
| **B_1 – B_2** (the only four-terminal region wired this cooldown) | **ABCA — rhombohedral** | **moderate** |
| T_1, T_2, T_3, T_4 | *not measured* — dead contacts, not wired to instruments | — |

"Region-resolved" is one region. The device card's provided configuration wires exactly one
four-terminal pair; T_1–T_4 are dead. Stacking domains elsewhere in the flake are untested,
and per the brief that is an operator rewiring matter, not a detour I could take.

## 2. Evidence

**(a) A displacement field opens a gap at charge neutrality — `data/3`.**
R_CNP rises **10.4×**, from **296 Ω** at D ≈ 0 to **3074 Ω** at D/ε₀ = +0.307 V/nm, measured
over ~30 crossings of the neutrality line. The session's own gate calibration comes from the
same run: the CNP-line slope over 26 unambiguous rows gives **c_tg/c_bg = 1.2737 ± 0.0470**
(the geometry prior was 1.1579), and every later cell used the measured ratio.

**(b) The gap is centred on D = 0 — `data/3` and `data/6`–`data/12`.**
Two independent observables locate the minimum:
- R_CNP at base temperature: **D = 0.000 ± 0.008 V/nm**, with the folded branches agreeing to
  within 7 % — R(+D)/R(−D) = 1.07, 1.01, 1.03, 0.96 at |ΔD| = 0.02, 0.04, 0.06, 0.08 V/nm,
  against a ~3 % per-point noise floor. Robust to ±1σ on the capacitance ratio (moves it
  < 0.001 V/nm).
- The activation gap Δ(D): minimum at **D = +0.016 ± 0.004 V/nm**.

**(c) Neutrality crosses from metallic to insulating under D — `data/6`–`data/12`.**
Δ = **−0.62 ± 0.17 meV** at D ≈ 0 (R_CNP *rises* with T: 249 → 360 Ω from 1.2 to 40 K) and
**+1.36 ± 0.14 meV** at D = +0.238 V/nm (R_CNP falls 2975 → 1175 Ω). dR/dT changes sign at
**D = +0.126 V/nm**; all seven isotherms cross there. +D flank slope 7.9 meV per V/nm.

**(d) A single Fermi pocket — `data/5`, corroborated by `data/4`.**
Four of five densities return exactly **one** unflagged SdH tone and **none returns two**; the
two highest-contrast traces (n = +0.99 and +1.49 × 10¹² cm⁻²) give f/f_full = **0.835** and
**0.834**. Two pockets would put the dominant tone near 0.7× the full Onsager value *and* add
a second near 0.3×, both scaling linearly with n. Neither is present. Cross-check: the density
scale implied by the SdH slope (α = 1.199) agrees with the Landau fan's independent
minima-ladder (α = 1.166) to **2.8 %**.

**Why not ABAB.** Two independent disqualifications. A Bernal tetralayer is a band-overlapped
semimetal whose neutrality point stays conducting under displacement field — but (c) shows a
clean D-driven metal→insulator crossover. And its two bilayer-like bands both cross E_F at
D = 0, which must produce two SdH tones at a fixed ratio — but (d) finds one.

**Why not ABCB.** ABCB lacks inversion symmetry, so it carries a built-in gap at D = 0 that is
closed by a field of one particular sign; its gap minimum must sit at finite D. Both
independent estimates put the minimum within ~4 % of the accessible D range of zero.

## 3. Confidence and hedges

**Moderate, not strong.** Five things hold it back, in order of how much they matter:

1. **The −D lever arm is only 0.26 of +D.** Negative D at neutrality requires V_tg < 0, and
   the provided top-gate limit stops at −0.3 V — an operating limit the brief bans me from
   probing. Symmetry is therefore demonstrated over |D| ≤ 0.10 V/nm, not the full range. An
   ABCB asymmetry that only develops beyond that would be invisible here. **This is the single
   biggest limitation on the call.**
2. **The two estimates of the gap-minimum location do not perfectly agree**: 0.000 ± 0.008
   (base-T resistance) versus +0.016 ± 0.004 V/nm (activation). Taken at face value the second
   is displaced from zero by several times its own fit error. I do not read that as evidence
   for ABCB — the two are different observables, the bootstrap error captures only fit noise,
   and 0.016 V/nm is 4 % of the accessible range — but a *weak* inversion-symmetry breaking
   cannot be excluded by this dataset.
3. **The gap's magnitude is not a band-structure number.** Δ_max = 1.36 meV is one to two
   orders of magnitude below a clean rhombohedral gap at D ≈ 0.25 V/nm, and R_CNP saturates
   near 3 kΩ rather than continuing up. Transport is disorder- and parallel-channel-limited.
   The gap's *existence and D-dependence* are established; its *size* is not.
4. **No absolute density calibration.** The SdH frequency and the LL ladder both depend only on
   the product α·g (measured consistently as 4.78 and 4.67), so the density scale and the
   Landau degeneracy cannot be separated. Breaking the degeneracy needs R_xy = B/(n·e), and no
   Hall pair is wired — sr2 and sr3 are n.c. Assuming the standard g = 4 gives c_tg = 2.40
   mF/m² (11.1 nm equivalent hBN against the card's 9.5 nm). **Nothing above depends on this**:
   the evidence is a ratio, a symmetry point, and a tone count.
5. **No Hall-bar geometry**, so every resistance here is in ohms, not ohms per square, and no
   absolute sheet-resistance or mobility claim is made. Electron temperature ~8 K also puts
   correlated and symmetry-broken states out of reach and restricts the activation fit to
   T ≥ 8 K.

**What was not measured, and why.** The Si contact-doping gate stayed at 0 V all session (the
graphite back gate screens it from the channel, so it was never needed; its ramp is
consent-gated). No field above 6 T, because the magnet's fixed 0.137 T/min made every extra
tesla ~7 min each way and 6 T already put ν = ±8 inside the density window. No measurement
below 8 K carries independent information.

**What would overturn the call.**
- Extending the top-gate range past −0.3 V to lengthen the −D lever arm, and finding the gap
  minimum genuinely displaced → **ABCB**. This is the decisive follow-up.
- A second SdH tone below ~1.5 T, which the degree-5 background removal would have eaten →
  would reopen a two-pocket (ABAB-like) reading. A lower-field, finer 1/B record would test it.
- A Hall pair, giving an absolute density and hence the true Landau degeneracy — this would
  not touch the D-symmetry or tone-count arguments, but it would let the LL sequence be read
  independently instead of assumed.

## 4. One correction to the record

The proposing cell for the Landau fan (measure notebook, idx 41) claimed the LL degeneracy
would discriminate ABCA from ABAB — that a rhombohedral tetralayer's 4-fold orbital zero level
(16 states, first gaps at ν = ±8) would look different from a Bernal one. **That is wrong.**
ABAB tetralayer decomposes into two effective bilayers, each with a 2-fold orbital zero level
× 4 spin/valley = 8 states, and both sit at exactly E = 0 — so ABAB also has 16 zero-energy
states. The zero-LL degeneracy is 4N for N layers **regardless of stacking order**: it counts
layers, not stacking. The measure notebook is append-only so the claim stands there; this is
the correction. The fan's actual contribution to the call is the **pocket count**, not the
degeneracy.
