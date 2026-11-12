# vti-02 — stacking-order plan (HERA, session 20260822)

Goal: region-resolved call ABAB / ABCA / ABCB on the one wired contact pair
(`sr1` = B_1 − B_2, source T_0, drain B_3). One region only — the contact map
gives no second Rxx pair this cooldown, so "region-resolved" = one region.

*(Written on handoff — the first instance ran steps 0–3 without landing a
`plan.md`; this reconstructs the arc from the notebooks + data and carries it
forward. See `session_notes.md` PROTOCOL entry.)*

## Discriminators (what separates the three stackings)

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| Fermi surfaces at D = 0 | **two** bilayer-like subbands; densities partition ~0.23 / 0.77 at n = 3.2e12 (band model, step 2) | **one** quartic band carrying the full density → single F = nh/4e | two, but partition ≠ ABAB's and e/h asymmetric |
| SdH frequencies | two independent F(n), both ∝ n, summing to nh/4e | one F(n) = nh/4e | two, unequal e vs h |
| m* | light pair (~0.03 / 0.06 mₑ) | heavy (~0.07–1 mₑ), LK-dead fast | mixed |
| R_CNP vs D | semimetal, weakly D-dependent | gap opens strongly with D | intermediate |

The decisive, calibration-free test is **the number of independent SdH
frequencies and their fractional slopes dF/dn** — a harmonic has slope exactly
k× the fundamental's, an independent Fermi surface does not, and the
independent tones must sum to the full gate-induced density.

## Steps

0. **Gate C — liveness** (runs 0–3, `gate-current-sanity-check`). Done: both
   gates hold their full card range with |I| ≤ 0.2 nA; `sr1` alive.
1. **0 T gatemap** (run 5, `gatemap`; run 4 railed and was re-run). Done:
   CNP line found, `c_bg/c_tg = 0.773` (data), `n_offset = −0.089e12`,
   `D_offset = −0.013 V/nm`; D = 0 line inside the validators spans
   n = −1.27 … +3.27e12. Side-observation: R_CNP rises from ~0.33 kΩ at
   D ≈ 0 to 2.5–2.9 kΩ at |D| ≈ 0.3 V/nm — a gap that opens with D, which
   already leans away from plain ABAB.
2. **Feasibility model** (no measurement). Done: F_L(3.2e12) = 33.1 T,
   F_L(1.2e12) = 12.4 T.
3. **SdH spot checks** (runs 6 electron n = +3.2e12, 7 hole n = −1.2e12).
   Done. Strong, deep-minima SdH from ≈ 1 T; `sdh_onset` → onset 0.30 T
   (censored at the record edge) electron, 0.71 T hole. **Ambiguous on the
   number of surfaces**: run 6 shows a ~7.1–7.5 T tone plus a ladder at
   14/22/29.5 T that `sdh_onset` reads as its harmonics, and a 4–10 T window
   peak at 33.3 T ≈ F_L; run 7 shows a 12.3 T tone ≈ F_L(full density) plus
   3.4 / 4.7 / 6.6 T. A single spot cannot separate "harmonic ladder of one
   light surface" from "two independent surfaces" — both fit. → step 4.
4. **Landau fan at D = 0** ← *current step*. Rxx over (n, B); n fast along the
   calibrated D = 0 line, B slow, uniform in 1/B. Yields F(n) per tone from
   the 1/B FFT of every n column, plus the LL-period-in-n read at each field.
   - **two tones with independent, non-integer-ratio slopes summing to
     h/4e** → ABAB or ABCB (partition fraction then separates them, with the
     e/h asymmetry as the tiebreak);
   - **one tone with slope exactly h/4e, the ladder tracking k× it** →
     ABCA;
   - ambiguous slopes / dead tones → `cannot tell`, with the resolution
     quoted.
   - **What would change my mind:** a tone whose F does not extrapolate to 0
     at the CNP (⇒ not a Fermi surface, an artifact); a degeneracy other
     than 4 in the LL-period-in-n read (⇒ the h/4e sum rule is the wrong
     yardstick and the partition read needs redoing).
5. **Mass check (LK), conditional.** If step 4 leaves ABAB vs ABCB or ABCA
   ambiguous, a short T-ladder at one or two n spots at fixed B, fitting the
   LK amplitude for m*. Only if the fan leaves a real fork and time allows.
6. **Call + close-out.** Verdict cell in the ana notebook (output contract);
   `return-to-initial`.

## Standing constraints

- Field is the expensive axis (0.137 T/min, blocking): B is always the slow
  axis, and never re-traverse — each step starts where the magnet sits.
- `sr1` τ = 0.3 s at 24 dB/oct (operator front-panel; not ours to change).
  On a gate fast axis that sets a **sweep-rate ceiling**, not just a dwell:
  the 4-pole filter averages over σ_n ≈ 2τ·(dn/dt), which washes out the LL
  oscillation once σ_n approaches the LL period in n (= 4eB/h). This, not the
  point count, sets the fan's row time.
- Banned: touching the operating limits; a standalone Si survey.
