# vti-02 — stacking-order plan (HERA)

*Written 2026-08-23 by the second agent instance. The first instance ran steps
0–3b without landing a plan file (see session_notes PROTOCOL). This file
reconstructs the arc from the notebooks + data and carries it forward.*

**Goal**: region-resolved stacking call for tetralayer vti-02 — ABAB / ABCA /
ABCB / cannot tell, evidence-cited, in the ana notebook's final cell.
**One region only**: the hardwired configuration gives a single Rxx pair
(`sr1` = B_1 − B_2, source T_0, drain B_3). So the contract's "per-region"
list has exactly one line, plus whatever the data says about the two series
sub-regions inside that pair (see the confound below).

---

## The discriminator

At D = 0 the three candidates partition the carrier density among Fermi
surfaces differently, and SdH frequency is the direct probe:

| stacking | Fermi surfaces at D = 0 | expected F(n) |
|---|---|---|
| **ABCA** (rhombohedral) | one quartic band touching per carrier sign | a **single** tone on the full-density line `F_L = n·h/4e` |
| **ABAB** (Bernal) | two bilayer-like subbands (γ1 → γ1·(√5±1)/2) | **two** tones, `F₁+F₂ = F_L`, partition ≈ 0.23 / 0.77, roughly **the same on both carrier signs** (inversion-symmetric) |
| **ABCB** (mixed) | two subbands, no inversion symmetry | **two** tones summing to `F_L`, partition **electron–hole asymmetric** |

So the measurable is **F vs n at D = 0**: how many tones, do they sum to
`F_L`, what is the partition, and is the partition the same for n > 0 and
n < 0. This is why the fan sweeps n over both signs.

**The confound the fan must beat.** Run 5 showed two parallel CNP ridges in
the pair — two series sub-regions, B electron-doped by 0.43×10¹² relative to
A. Series regions also produce two tones. They are separable by **slope**:

- series mosaic → two tones with the **same** `dF/dn = h/4e`, offset by a
  constant (0.43×10¹² → 4.4 T);
- band partition → tones with **different** `dF/dn` (0.23·h/4e and
  0.77·h/4e), converging to 0 at the CNP.

A single-density FFT cannot tell these apart; F(n) over a wide n range can.
That is the whole case for the fan over more spot checks.

## Steps

| # | step | slug | status |
|---|---|---|---|
| 0 | Gate C liveness / leakage on the provided pair | `gate-current-sanity-check` | done — runs 0–3, Rxx 60–330 Ω, no leak |
| 1 | 0 T gate map → CNP line, capacitance ratio, D = 0 line | `gatemap` → `cnp-and-dline-calibration` | done — run 4 (railed, aborted), **run 5**; c_bg/c_tg = 0.773, D_offset −0.013 V/nm, D = 0 window n = −1.27 … +3.27×10¹² |
| 2 | Feasibility / model table (F_L, candidate masses) | — | done (in-cell, measure 39) |
| 3 | SdH spot checks at D = 0, both signs, to set the fan's B_lo and prove resolvability | `sdh-spot-check` | done — **run 6** (n = +3.2e12), **run 7** (n = −1.2e12). Oscillations strong, onset ≲ 0.5 T (e) / 0.71 T (h), tones ambiguous at a single density → fan needed |
| 4 | **Landau fan at D = 0**, B slow (uniform in 1/B) × n fast | `landau-fan` | **next — this step** |
| 5 | Read: F(n) per tone (slopes vs h/4e), filling-factor sequence, e–h symmetry of the partition | ana | after step 4 |
| 6 | Contingency, only if step 5 is ambiguous: a measured ride-down 10 → 0.9 T at one fixed n with fine 1/B sampling (sharper δF at the best density), or a second fan at finite D | — | conditional |
| 7 | Call + close-out (`return-to-initial`) | ana / measure | last |

## Step 4 design (and what would change my mind)

- **Fast**: (V_tg, V_bg) co-swept along D = 0, n = −1.20 … +3.20×10¹² cm⁻²,
  89 points (Δn = 0.05×10¹²). Both endpoints sit inside the committed
  validators (V_tg −0.277 … +0.984 of [−0.3, +1.0]).
- **Slow**: B = `field_invB(0.9, 10.0, 102)` — uniform in 1/B, so `sdh_fft`
  needs no resample. δ(1/B) = 0.010 1/T → Nyquist 50 T (F_L max 33.1 T);
  δF = 0.99 T.
- B_lo = 0.9 T from the step-3 onsets (0.3 T censored-at-edge on the electron
  side, 0.71 T on the hole side) — 0.9 T keeps the measured-signal band
  without paying the row count that 0.7 T would cost.
- **Ascending**, ending at 10 T: the magnet sits at 0 now, and ending high
  turns the close-out ramp into a possible step-6 measured ride-down.

**What would change my mind / abort:**
- CNP column rails and bleeds into neighbours at high B → keep, but the
  F(n) read restricts to |n| > 0.2×10¹².
- No oscillation content by ~2 T anywhere in n (contradicts runs 6–7) →
  something moved; stop and re-check the spot.
- Gate leakage > 1 nA → leak guard interrupts, gates parked.
- If F(n) shows two tones with **equal** slopes → that is the series mosaic,
  not a band partition; the stacking read then rests on the single
  common slope (h/4e ⇒ one surface per region ⇒ ABCA-like) and step 6
  becomes mandatory.
