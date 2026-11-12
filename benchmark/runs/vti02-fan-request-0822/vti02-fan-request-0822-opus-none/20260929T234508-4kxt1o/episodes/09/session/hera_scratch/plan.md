# vti-02 — stacking-order plan (live; rewritten 2026-08-23 05:25 at the instance handoff)

**Goal.** Region-resolved call: ABAB / ABCA / ABCB (or a calibrated "cannot tell"),
evidence-cited, in the ana notebook's final cell.

**One Rxx pair only** (`sr1` = B_1−B_2, source T_0, drain B_3; sr2/sr3 n.c., hardwired,
no mux). So "region" = the electrical regions *in series within that pair* — run 5's
gatemap already resolves two: **ridge A** (the dominant CNP) and **ridge B**
(parallel, 0.43×10¹² electron-doped relative to A). Any per-region verdict has to come
from separating those two families inside the same trace. No Hall channel — no
independent n or ν sign check. That is a standing hedge.

## What discriminates the three stackings (the physics the plan is aimed at)

At D = 0 the decisive observable is **how the total density partitions across Fermi
surfaces**, read as SdH tone fractions xᵢ with Σxᵢ = 1:

| stacking | low-energy bands at D=0 | fan signature |
|---|---|---|
| **ABAB** (Bernal) | two bilayer-like subbands, different m*, band overlap (semimetal) | **two** tone families, x₁+x₂ = 1, ratio drifting with n; ungapped CNP at D=0; gap opens with D |
| **ABCA** (rhombohedral) | one quartic flat band (+ trigonal-warping pockets at low n) | **one** family with x = 1 (F = nh/4e); Lifshitz/×3-pocket structure at low n; strong D-gap |
| **ABCB** (mixed) | inversion-broken, **gapped at D = 0**, asymmetric in ±D | insulating CNP at D = 0; ±D asymmetry |

Run 5 already says the CNP at D = 0 is **not** strongly gapped (R_CNP ≈ 240 Ω, vs
2.4 kΩ at D ≈ +0.25 V/nm) — that leans away from ABCB and is the main reason the
partition question (ABAB vs ABCA) is now the load-bearing one.

## Steps

1. **DONE — gate C liveness** (runs 0–3): provided pair alive, gate currents ≤ 120 pA.
2. **DONE — 0 T gatemap** (run 5, after run 4 railed): CNP line, ratio c_bg/c_tg = 0.773
   (data), D_offset from the R_CNP(D) vertex, two ridges A/B. Absolute n scale is still
   the **9.5 nm geometry prior** — uncalibrated. Realized D = 0 window: n = −1.27 … +3.27.
3. **DONE — SdH spot checks** (runs 6 e-side n=+3.2, 7 h-side n=−1.2): oscillations are
   **strong and survive to ≲ 0.7 T** (`sdh_onset`: run 7 onset 0.71 T; run 6 censored at
   the 0.3 T record edge). Run 6's high-B FFT is a **harmonic comb on ≈ 6.7 T**
   (6.7/13.3/20.0/26.7/33.3/40.0) — and 33.3 T is exactly the full-density Luttinger
   F_L(3.2×10¹²) = 33.1 T. **This is the session's central ambiguity:** either
   (a) one light surface x ≈ 0.20 plus a heavy partner at x ≈ 0.80 whose 26.6 T tone is
   degenerate with the 4th harmonic → **ABAB**, or (b) a single x = 1 surface at 33 T
   whose spiky lineshape generates the whole comb and the 6.7 T is a sub-feature →
   **ABCA**. A single-density trace cannot separate them.
4. **NOW — Landau fan at D = 0** (this step). Fast axis = n (cheap), slow = B (expensive).
   Breaks the ambiguity three ways:
   - **n-FFT per B row** gives xᵢ directly (a surface with fraction xᵢ has n-period
     (4eB/h)/xᵢ). The **sum rule Σxᵢ = 1** is the ABAB-vs-ABCA test.
   - **xᵢ(n)** windowed along the fast axis: two real subbands partition n differently as
     n moves; a harmonic tracks its fundamental exactly at k×, forever.
   - **fan-line convergence**: LL gaps are n = ν·eB/h, straight through each region's own
     CNP. Two n-intercepts separated by ≈ 0.43×10¹² ⇒ the A/B mosaic resolved, and the
     **ν sequence** (4, 8, 12 … vs 12 at low n vs symmetry-broken) read directly.
   - Covers both carrier signs and both CNPs in one pass.
5. **NEXT (planned, not committed)** — decided by step 4:
   - If two families with Σx = 1: **LK temperature ladder** at one fixed B on the
     electron spot to get m*₁, m*₂ (the ABAB mass pair is a second, independent
     fingerprint) — and it also kills the harmonic reading outright (harmonics carry
     k·m*).
   - If one family with x = 1: a **low-n fine fan** looking for the trigonal-warping
     ×3-pocket / Lifshitz structure of ABCA.
   - Either way, a **D ≠ 0 arm** (fan or gap-vs-D) if time allows: ±D asymmetry is the
     ABCB check and the gap-vs-D slope separates ABAB from ABCA.
6. **Close-out** — `return-to-initial`, readback to `session_notes.md`.

## What would change my mind

- Fan shows **one** family with x = 1.00 ± 0.05 across the whole n range → ABCA, and the
  6.7 T comb is lineshape. (Currently I lean ABAB, weakly, on the 6.7 + 26.7 = 33.3 sum.)
- A **gapped CNP at D = 0 in field** (R_CNP diverging at all B with no ν=0-only character),
  plus ±D asymmetry → reopen ABCB.
- Fan lines converging on **three or more** distinct n-intercepts → the mosaic is worse
  than two regions and the tone decomposition is not region-resolvable; the call
  degrades to "cannot tell" with the evidence stated.
- Absolute-n error: everything above is a *ratio* argument (xᵢ, Σxᵢ), which is immune to
  the geometry-prior scale error. The fan's own ν sequence gives the first **absolute**
  lever-arm check of the session (n = ν·eB/h at a known B) — if it disagrees with the
  9.5 nm prior by more than ~10 %, the prior is rescaled and F_L targets move.
