# vti-02 — stacking-order plan (HERA)

*Reconstructed 2026-08-23 at the handoff: the pre-handoff instance's `plan.md`
did not survive into the measurement dir (see session_notes TOOLING). Steps 1–3b
are reconstructed from the measure-notebook markdown (cells 33–42), which cites
them; step 4 onward is this instance's.*

## Goal

Region-resolved stacking call for tetralayer vti-02: **ABAB** / **ABCA** /
**ABCB** / `cannot tell`, evidence-cited, per the brief's output contract.

## The discriminator

At D = 0 the three candidates differ in **how many Fermi surfaces share the
carrier density, and in what proportion**:

| stacking | bands at D = 0 | SdH signature |
|---|---|---|
| ABAB (Bernal) | two bilayer-like subbands, distinct m* | **two** frequencies, fixed ratio, F1 + F2 = &#124;n&#124;h/4e |
| ABCA (rhombohedral) | one quartic flat band | **one** frequency = &#124;n&#124;h/4e; strong gap at CNP |
| ABCB (mixed) | monolayer-like + trilayer-rhombohedral-like | two frequencies, **different** partition than ABAB |

So the measurement is: **frequency content vs density along D = 0**, plus the
sum rule as the internal consistency check (it also calibrates the lever arm
absolutely, independent of the geometry prior).

## Steps

- **Gate C — liveness** (runs 0–3, `gate-current-sanity-check`). DONE. Four 1D
  gate legs at B = 0; no leakage trip; R peaks <= 330 Ohm.
- **Step 1 — 0 T gatemap** (run 4 aborted / run 5, `gatemap`). DONE. One dominant
  CNP ridge (A) + a fainter parallel ridge (B) 0.19 V lower in V_tg → the channel
  is a **two-region series mosaic**, B electron-doped by 0.43e12 vs A.
- **Step 2 — `cnp-and-dline-calibration`** (ana cell 13). DONE. c_bg/c_tg = 0.773
  (data), c_tg = 9.5 nm geometry prior (**absolute scale unvalidated**),
  n_offset = −0.089e12, D_offset = −0.013 V/nm. Realized D = 0 window inside the
  validators: n = −1.27 … +3.27e12.
- **Step 3 / 3b — SdH spot checks** (runs 6, 7). DONE, analysed here 2026-08-23
  (`hera_scratch/ana_spot67.py`, `ana_index67.py`). Both spots oscillate strongly
  (Rxx → 0 minima) from < 1 T. **Consecutive-index fits fail** (rms 87 % / 52 % of
  a period) ⇒ more than one frequency. Provisional two-tone read with the sum rule
  nearly closing at both spots and a **stable ~3:1 partition** — the ABAB template.
  Single-spot FFT alone cannot separate fundamentals from the (strong, because the
  minima are square) harmonics.
- **Step 4 — Landau fan** (NEXT, `landau-fan`). B slow × n fast at D = 0, both
  carrier signs, across the CNP. Establishes: (a) per-density frequency content
  F_i(n), (b) the sum rule / absolute lever arm, (c) the partition fraction and
  its n-dependence, (d) the CNP vs B behaviour. **This is the decisive run.**
- **Step 5 — the call.** Land the per-region verdict in the ana notebook.
- **Close-out.** `return-to-initial` per the brief.

## What would change my mind

- **One family, F = &#124;n&#124;h/4e across the whole n range** → ABCA, not ABAB.
  The provisional two-tone read would then be harmonics I mis-split.
- **The sum rule missing by more than the lever-arm uncertainty** → either the
  calibration is wrong or a family is unresolved; hedge to `cannot tell`.
- **A partition that drifts with n** → not two rigid parabolic subbands; points
  away from clean ABAB.
- **Doubled/extra tones at a fixed ~1.13 ratio** → the ridge-B mosaic region
  contributing in series, not a band. Must be excluded before any call.
- **Electron/hole asymmetry beyond band-structure expectation** → ABCB (it is
  non-centrosymmetric) rather than ABAB.

## Standing hedges

- **One Rxx pair only** (`sr1` = B_1 − B_2); T_1..T_4 dead. No Hall, so no
  independent density from R_xy, and no second region to compare. "Region-resolved"
  is therefore limited to what the two-ridge mosaic lets us say about the single
  measured pair.
- **Absolute n scale rests on the fan**, not the geometry prior.
