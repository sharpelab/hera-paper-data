# vti-02 — plan (HERA, 2026-08-24)

Goal: call the stacking order of tetralayer graphene vti-02 — ABAB / ABCA / ABCB
(or a calibrated "cannot tell"), region-resolved, evidence-cited.

## What separates the three stackings (the physics I am testing)

| | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| inversion symmetry | yes | yes | **no** |
| low-E bands | two bilayer-like massive bands (γ1-split) → **2 Fermi pockets** | one ~quartic **flat** band → **1 pocket** | Dirac-like + massive, **2 unequal pockets** |
| R at CNP, D=0 | small (~kΩ), metallic | **large** (flat band, huge DOS) | intermediate |
| R_CNP vs D | weakly D-dependent, **stays conducting** (band overlap survives D) | **steep, ~symmetric** insulating rise; gap → tens of meV | gap opens but **asymmetric about D=0**; R peak at D ≠ 0 |
| activation gap Δ(D) | ≈ 0 | large, ∝\|D\|, symmetric | moderate, asymmetric |

So the discriminating observables, cheapest first:
1. **R_CNP magnitude and its D-dependence** (gate map + CNP-line cut, B = 0).
2. **Symmetry of R_CNP(D) about its own maximum** (ABCB breaks it).
3. **Number of SdH frequencies at fixed n** (Landau fan → `sdh_fft`): 1 pocket = ABCA,
   2 pockets = ABAB/ABCB.
4. **Arrhenius Δ(D)** from a T-ladder at the CNP.

## Hard constraints this session

- Gate box (provided, **not probeable**): TG [−0.3, +1.0] V, BG [−1.3, +2.0] V,
  Si [−25, +25] V. B ≤ 10 T. T setpoint ≤ 100 K.
- Geometry prior (uncalibrated until my own map confirms it):
  c_tg = 2.796e-3 F/m² → 1.745e12 cm⁻²/V; c_bg = 2.414e-3 F/m² → 1.507e12 cm⁻²/V.
  ⇒ CNP line slope dV_bg/dV_tg = −c_tg/c_bg = **−1.158**; full-box Δn ≈ 7.2e12 cm⁻².
  Along the CNP line, **D/ε0 = 0.316·V_tg − 0.136·V_bg0** [V/nm], where V_bg0 is the
  CNP-line intercept at V_tg = 0.
- **Risk — the D window may be one-sided.** With V_bg0 = 0 the reachable CNP-line D
  is only [−0.10, +0.32] V/nm; with V_bg0 ≈ +1 V it is a near-symmetric ±0.2 V/nm;
  with V_bg0 ≈ −1 V it is entirely positive. If ±D is not reachable, the ABCB
  asymmetry test is **unavailable** and the verdict must hedge on that explicitly.
- Only **one** four-terminal region is wired: sr1 = B_1–B_2. sr2/sr3 n.c. So the
  "per-region verdict" is one Rxx line (B_1–B_2) plus the two-terminal T_0→B_3 read
  from the sr0 current. A dead contact is an operator rewiring problem, not a detour.
- Electron temperature ≈ 8 K (rig card): fragile correlated/symmetry-broken states are
  out of reach. Everything here is single-particle band physics — fine for stacking.
- Si gate is screened from the channel by the graphite BG; it is a **contact**-doping
  knob only. Held at 0 V unless the contacts choke at a deep gap — and its ramp is
  consent-gated, so that is an operator ask, never an auto step.
- Bias: sr1 osc 1.0 V through 100 MΩ ⇒ **I_bias ≈ 10 nA**. Rxx = V_sr1 / I_measured
  (`resistance_grids` uses the *measured* sr0 current, so it self-corrects when the
  current bias sags into a resistive device).
- **Settling.** sr0/sr1 τ = 0.3 s at 24 dB/oct ⇒ compliant dwell 7–10τ = 2.1–3.0 s/pt.
  That prices the coarse map at ~2 h. I will ask the operator for **τ = 0.1 s** on
  sr0+sr1 (2f rejection at 27.5 Hz still ≈ −50 dB; SNR ~10³ at 10 µV) which drops the
  floor to 0.7–1.0 s/pt — a 3× session-wide saving. Every dwell bend is stated on the page.

## Steps

**P1 — Gate C: liveness + scaling** (~10 min). 1D V_bg sweep, full BG range, V_tg = 0,
B ≈ 0. Follow sr0 X/Y (current), sr1 X/Y (Vxx), both Keithley leakage currents, T_sample.
Establishes: both contacts alive, signal not railed vs sensitivity, gate leakage floor,
and a first bracket on the CNP. Then a TG sweep at the best BG. *Changes my mind:* a dead
or railed channel → stop and hand to the operator.

**P2 — Coarse (n, D) gate map** at B = 0, base T (~45–60 min). megasweep: slow = V_bg over
[−1.3, +2.0], fast = V_tg over [−0.3, +1.0]. Establishes the **session gate calibration**
(CNP-line slope → c_tg/c_bg ratio; intercept → n_offset, D_offset) and the R_CNP(D) map —
the primary discriminator. *Changes my mind:* CNP line not straight / not at the geometry
slope ⇒ my n,D scale is wrong and everything downstream re-anchors on the measured slope.

**P3 — CNP-line cut, R_CNP vs D** (~15 min). `multisweep` along fixed n = 0 (co-swept
V_tg, V_bg), fine steps, plus 2–3 constant-D cuts vs n. Gives R_CNP(D) quantitatively:
magnitude at D = 0, steepness, and symmetry about the maximum.

**P4 — Landau fan** at base T (~2–3 h). `multimegasweep`: slow = B on a `field_invB` grid
(uniform in 1/B, so `sdh_fft` needs no resample), fast = the fixed-D density line. Reads:
LL degeneracy, whether the CNP gap grows with B, and — via `sdh_fft` per density column —
**how many SdH frequencies** the Fermi sea carries. 1 tone summing to the full Onsager
`luttinger_frequency(n)` ⇒ ABCA; 2 tones splitting it ⇒ ABAB/ABCB.

**P5 — T-ladder at the CNP** (~1.5 h, **last**, because descent is passive and slow).
`heater.set_both(T, ratio=0.95)` over ~6 setpoints from base to ≲ 60 K; at each, re-run the
P3 CNP-line cut. Arrhenius R_CNP(1/T) at each D ⇒ Δ(D). Accept points on **stability**, not
proximity (rig card: sample loop untuned, +1.4 K overshoot).

Ordering is adaptive: P2/P3 decide whether P4 or P5 carries more weight. Field is the
expensive axis (0.137 T/min) — plan the fan to start where the magnet sits and not to
re-traverse. T is the irreversible axis — it goes last.

**P6 — Close-out** (`return-to-initial`): B → 0, TG/BG/Si → 0 V at committed pacing,
both heater ranges off, readback printed and logged.

## Verdict logic

- R_CNP(D=0) small **and** flat in D **and** 2 SdH tones ⇒ **ABAB**.
- R_CNP(D=0) large **and** steeply, symmetrically insulating in D **and** 1 SdH tone
  **and** Δ(D) growing ⇒ **ABCA**.
- Gap present but **asymmetric in D** (max at D ≠ 0), 2 unequal tones ⇒ **ABCB**.
- D window one-sided, or the fan never resolves tones ⇒ **cannot tell** on the axes not
  covered, with the covered axes reported at their honest strength.


---

## Live update — after P1 (runs 0, 1) and the first map rows (run 3)

**Established in-session (replaces the withheld facts):**
- **CNP at V_bg = −0.250 V for V_tg = 0** ⇒ n_offset ≈ +3.8 × 10¹¹ cm⁻²; CNP line
  `V_bg = −1.158·V_tg − 0.250` (geometry-prior slope; the map's 35 crossings measure the
  real c_tg/c_bg ratio and supersede it).
- **R_CNP(D ≈ 0) = 297 Ω** (run 1). This is the reference the stacking call is measured
  against.
- Noise floor: per-point σ ≈ 2–3 Ω (32 nV ≈ SR830 1/f at 13.8 Hz). **Believe nothing
  below ~3 %.**
- Contacts ≈ 0.4 MΩ each (from R₂ₜ vs Rxx); gates leak < ~30 pA with no voltage
  dependence; hysteresis 50 mV = one grid step.

**The number that has moved the plan:** run 3 row 0 puts R_CNP at **2.95 kΩ at
D/ε₀ = +0.320 V/nm**, i.e. **~10× the D ≈ 0 value**. A displacement field is opening a gap.
That is the opposite of what a Bernal ABAB tetralayer should do — ABAB is a band-overlapped
semimetal that stays conducting under D — so **ABAB is now the disfavoured hypothesis** and
the live question is ABCA vs ABCB.

**Revised discriminator, sharpened.** The three stackings are now separated by *where the
R_CNP(D) minimum sits*, not merely by whether R_CNP rises:
- **ABCA** is inversion-symmetric ⇒ gapless at D = 0, gap ∝ |D| ⇒ minimum **exactly at
  D = 0**, symmetric either side.
- **ABCB** has no inversion symmetry ⇒ a built-in gap at D = 0 that is *closed* by some
  finite field ⇒ minimum **displaced to D ≠ 0**.
- **ABAB** ⇒ little D dependence at all (now unlikely).
The map straddles D = 0 (+0.320 down to −0.067 V/nm), so this test is available — with the
caveat that the −D lever arm is 5× shorter, set by the provided TG limit of −0.3 V which is
banned from being probed.

**Step order updated.** P4 (Landau fan) and P5 (T-ladder) swap in importance depending on
what R_CNP(D) looks like:
- If the minimum is clean and at D = 0 → ABCA. Confirm with **activation** (P5): Δ(D)
  should grow roughly linearly in |D| and extrapolate to ~0 at D = 0.
- If the minimum is displaced → ABCB. Same activation measurement, but the number that
  matters is Δ(D=0) > 0 and the asymmetry Δ(+D) ≠ Δ(−D).
- The fan (P4) stays valuable either way for the **Fermi-pocket count** (1 pocket = ABCA-like
  single quartic band; 2 = ABAB/ABCB), and it is the only route to an **absolute** density
  calibration (SdH frequency vs n), which so far rests on the unverified geometry prior.

**New caveat to carry into the call:** no Hall-bar geometry is given, so Rxx cannot be
converted to Ω/□ and every claim must rest on *ratios*. The 10× rise is a ratio and is safe;
"297 Ω at neutrality" as an absolute sheet resistance is not.
