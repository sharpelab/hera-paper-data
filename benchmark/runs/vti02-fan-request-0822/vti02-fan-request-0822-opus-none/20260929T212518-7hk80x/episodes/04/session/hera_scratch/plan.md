# vti-02 — plan (stacking order of tetralayer graphene: ABAB / ABCA / ABCB)

*Written 2026-08-23 05:30 on picking the session up mid-flight; steps 0–3 were
run by the prior instance and are recorded here from the notebooks + `data/`.
Kept current as data lands.*

## The question, operationally

Four-layer graphene at D = 0:

| stacking | band structure | D = 0 Fermi surfaces at finite n | CNP at D = 0 | D-induced CNP gap |
|---|---|---|---|---|
| **ABAB** (Bernal) | two bilayer-like blocks, m\* ≈ 0.03 / 0.06 mₑ | **two** FS → **two SdH frequencies**, F₁ + F₂ = F_full | semimetallic band overlap | weak / none (inversion-symmetric) |
| **ABCA** (rhombohedral) | one quartic flat band | **one** 4-fold FS → **single** F = F_full (trigonal warping may split at low n) | flat-band, high DOS | **strong** — D opens a real gap |
| **ABCB** (mixed) | one bilayer-like + one monolayer-like block, inversion broken | two FS, **unequal** and **asymmetric in ±D** | mixed | asymmetric in D sign |

So the discriminators, in order of decisiveness on this rig:

1. **How many Fermi surfaces carry the density, and do their SdH frequencies
   sum to the full-density Onsager value** F_full = |n|h/4e. One frequency ⇒
   rhombohedral-like; two ⇒ Bernal-like. Requires F tracked **vs n**, so
   harmonics (exact integer multiples, fixed ratio) separate from genuine
   second pockets (own slope dF/dn, own intercept at CNP).
2. **Landau-level gap sequence** — slopes dn/dB of the fan's minima give ν
   directly; the degeneracy pattern (multiples of 4 for one 4-fold FS, two
   interpenetrating families with crossings for two FS) is a second,
   FFT-independent read of the same thing.
3. **CNP gap vs D** — strong and symmetric ⇒ ABCA; weak ⇒ ABAB; asymmetric in
   D sign ⇒ ABCB.
4. **Electron–hole asymmetry** of all of the above.

## Steps

- **Step 0 — gate C liveness** (`gate-current-sanity-check`, runs 0–3, done).
  Four 1D gate legs to the committed limits, B = 0. Contacts live, leakage at
  the pA floor, R scale 60–330 Ω.
- **Step 1 — 0 T gate map** (`gatemap`, run 4 aborted → **run 5**, done).
  TG × BG map. Establishes the CNP line, the lever-arm ratio, and the first
  look at discriminator 3. *Result:* CNP ridge R climbs from ≤ 330 Ω at D ≈ 0
  to > 2.2 kΩ at D ≈ +0.3 V/nm (run 4 railed there at 2 kΩ FS; run 5 at 10 kΩ
  FS peaked 2.5–2.9 kΩ) — **a strong D-induced CNP gap**, which already leans
  away from pure ABAB.
- **Step 2 — (n, D) calibration** (`cnp-and-dline-calibration`, done, run 5).
  c_bg/c_tg = 0.773 (data), c_tg = 2.796 mF/m² (geometry prior), n_offset
  −0.089e12, D_offset −0.013 V/nm. The D = 0 line inside the committed gate
  box spans **n = −1.27 … +3.27e12 cm⁻²** — that box is the whole session's
  reach in n.
- **Step 3 — SdH spot checks** (`sdh-spot-check`, runs 6 + 7, done, analysis
  pending). n = +3.2e12 (0 → 10 T) and n = −1.2e12 (10 → 0.3 T), D = 0.
  *Result:* strong, well-developed SdH — minima reaching R ≈ 0 Ω on both
  carrier signs, oscillations tracked down to **0.3 T** (electron) / **0.71 T**
  (hole) by `sdh_onset`, SNR up to 100. Multiple tones on each side (electron:
  7.1 T carrying, plus 3.0/4.2/5.2/9.5 and the 14.1/22.2/29.5 harmonic ladder;
  hole: 6.6 T carrying, plus 4.7/8.5/9.4/12.3/14.8). **Tone multiplicity at a
  single density cannot separate a second pocket from a harmonic** — that is
  exactly what step 4 is for.
- **Step 4 — Landau fan at D = 0** ← *next, this proposal.*
  R_xx(n, B): n = −1.20 → +3.20e12 along D = 0 (177 pts, Δn = 0.025e12),
  B = 1.0 → 10.0 T uniform in 1/B (71 rows, F_Nyquist 38.9 T > F_full(3.2e12)
  = 33.1 T, δF = 1.11 T). Serves discriminators 1 + 2 + 4 in one run, and
  ends at 10 T so the next step rides the magnet down.
  **What would change my mind / what I expect to see:**
  - a single family of minima with slopes ν = 4, 8, 12 … all extrapolating to
    one CNP, and F(n) = F_full(n) on every column → **ABCA**;
  - two families with different dF/dn summing to h/4e, crossing in the fan →
    **ABAB**;
  - two families with unequal weights plus e/h asymmetry → **ABCB**;
  - if the tones at 7.1 / 22.2 T on the electron side keep an exactly integer
    ratio and a common intercept as n varies, they are harmonics of one FS,
    not two FSs — the run-6 multiplicity is then not evidence for ABAB.
- **Step 5 — D axis, riding 10 T → down** (planned, design after step 4).
  Either a fan at finite D, or R_xx(n, D) at fixed high B plus a CNP-gap-vs-D
  cut across **both D signs** — discriminator 3 + the ABCB asymmetry test.
  Step 4's result picks which.
- **Step 6 — the call** in the ana notebook, per the brief's output contract
  (one line per measured contact pair — here only `sr1` = B_1–B_2 is wired, so
  one region), evidence with run ids and numbers, confidence + hedges.
- **Step 7 — close-out** `return-to-initial`.

## Standing constraints

- One Rxx pair only (`sr1` = B_1–B_2); sr2/sr3 n.c. → **no Hall channel**, so
  ν comes from fan slopes and SdH frequencies, never from R_xy plateaux. This
  is the session's main structural limitation and goes in the hedges.
- T_e ≈ 8 K on this rig ⇒ effective-mass (Lifshitz–Kosevich) work is not
  available as a discriminator at these frequencies; excluded by design.
- Magnet 0.137 T/min, blocking: field is the expensive axis. Never
  re-traverse — alternate fan directions across steps.
- Lock-in τ = 0.3 s at 24 dB/oct ⇒ ≈ 1.2 s of filter memory; fast_delay 1.0 s
  (run-5 calibrated, 1.172 s/pt) leaves ≈ 0.8-point lag along n. Constant and
  one-directional, so it shifts the fan's apex, not the slopes ν.
