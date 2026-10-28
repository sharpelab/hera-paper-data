# vti-02 — stacking-order campaign plan (HERA)

Goal (brief): decide **ABAB / ABCA / ABCB** for vti-02 (tetralayer graphene),
region-resolved, evidence-cited, or a calibrated "cannot tell".
Only input data = this session's `./data/`. Written 2026-08-23 by the second
instance (the first ran steps 0–3 without landing a plan file — see
session_notes PROTOCOL entry).

## What discriminates the three stackings (the physics the plan is built on)

At `D = 0`, in the (n, B) plane, with Onsager `F_i = n_i·h/(4e)` per 4-fold
Fermi surface and `F_L(n) = |n|·h/(4e)`:

| | Fermi-surface families at D=0 | fan signature | CNP at D=0 |
|---|---|---|---|
| **ABAB** (Bernal) | two bilayer-like subbands, masses ≈ 2× apart, each 4-fold | **two** frequency families, `F1 + F2 = F_L`, a **band-edge onset density** where the second family appears; two interleaved LL line families + crossings | semimetallic band overlap → e- and h-pockets coexist near n=0 |
| **ABCA** (rhombohedral) | one quartic flat band, 4-fold | **one** family, `F = F_L` over most of n; possible low-n fragmentation (trigonal warping) / annular FS; symmetry-broken states at low n | sharp high-DOS CNP, strong D-induced gap |
| **ABCB** (mixed) | hybridized, e–h asymmetric | partition that closes on neither limit; asymmetric e vs h fan | intrinsic gap already at D = 0 |

**Decision rule.** (a) Count families vs n and test closure `Σ F_i = F_L(n)`;
(b) read fan-line slopes `dn/dB = ν·e/h` → degeneracy per family; (c) e–h
symmetry; (d) ν = 0 behaviour at the CNP; (e) do this separately for the two
regions the gate map found (below). Ambiguity escalates to step 5.

**Region structure.** Run 5 found **two CNP ridges** in one gate map — ridge A
(`c_bg/c_tg` = 0.773) and a fainter ridge B (0.691), B neutral at
`n_A = −0.43×10¹²`. The single provided probe pair (`sr1` = B_1 − B_2) spans
both, so this is a series mosaic, not a choice of pair. In a fan this is a
**feature**: the two regions have two distinct fan origins, so one map resolves
both — which is how the brief's "per-region verdict" gets answered with one
hardwired pair.

## Steps

- **0. Bring-up / gates A,B,C.** Done (see session_notes). E1 engaged.
- **1. `gate-current-sanity-check`** — runs **0–3**. Both gates to both card
  limits at B=0. Done: leakage ≤ 2×10⁻¹⁰ A everywhere, device alive, 1D R peaks
  ≤ 330 Ω. Establishes: contacts live, limits safe to use.
- **2. `gatemap` → `cnp-and-dline-calibration`** — run **5** (run 4 aborted,
  railed). Done: ratio 0.773, `c_tg` = 2.796 mF/m² (9.5 nm geometry prior),
  `n_offset` = −0.089e12, `D_offset` = −0.013 V/nm; two ridges; D = 0 line
  realized over `n = −1.27 … +3.27e12`. Establishes: where n and D are, and
  that the absolute n scale is still only a geometry prior.
- **3. `sdh-spot-check`** — runs **6** (e-side, n = +3.2e12, B 0→10 T, 10 mT)
  and **7** (h-side, n = −1.2e12, B 10→0.3 T, 20 mT). Done; analysed
  2026-08-23 by this instance. Establishes **feasibility**: SdH is strong and
  clean — onset below 1 T, per-point noise ≈ 2.5 Ω against 50–300 Ω
  oscillations, no clipping, no leakage. Frequency content is rich but
  **fundamental-vs-harmonic ambiguous at a single density** (run 6: a 7.1 T
  fundamental with 2×/3×/4× harmonics; is the 22–30 T content a harmonic or the
  heavy ABAB partner near `F_L − F1 ≈ 26` T?). That ambiguity is precisely what
  a fan resolves: harmonics sit at exactly `k·F₁(n)` at every n, a second
  Fermi surface has its own n-dependence, its own onset density, and must
  close `ΣF = F_L`.
- **4. `landau-fan` (this step, run 8).** R_xx over the full D = 0 line
  (n = −1.20 … +3.20e12, 119 pts) × B = 0 → 10 T (0.125 T, 81 rows), 1.2 K.
  Establishes: family count vs n, closure, ν sequence from line slopes, e–h
  symmetry, ν = 0 CNP behaviour — **for both regions at once** (two origins).
  Bonus: the ν lines are an absolute quantum-Hall lever-arm check, which
  upgrades `c_tg` from geometry prior to measured and makes the closure test
  quantitative rather than relative. Ends at 10 T.
- **5. Contingent follow-ups** (pick from the fan's read; the magnet will be at
  10 T, so the cheap ones ride it down):
  - **5a — fine 1/B line cuts** (`field_invB`) at 2–3 densities the fan flags
    (e.g. just below / just above a suspected subband onset), for precise
    `ΣF = F_L` closure. ~45 min each on the way down.
  - **5b — `landau-fan` at D ≠ 0** (e.g. D = +0.15 V/nm, where run 5 shows the
    CNP gap growing) if the D = 0 read is degenerate between ABAB and ABCB.
  - **5c — temperature dependence / LK mass** at one density, if and only if
    the family partition is ambiguous and masses are the tiebreak
    (ABAB predicts a specific mass pair). Expensive: rig card says
    closed-loop settles 2–5 min but descents are ~27 min τ.
- **6. The call** — final ana cell, in the brief's output-contract form, one
  verdict line per region (A and B), evidence with run ids and numbers,
  hedges.

## What would change my mind

- **Fan shows one family with `F = F_L` closing to a measured lever arm** →
  ABCA, and step 5a is a confirmation not a rescue.
- **Two families closing to `F_L` with a visible onset density** → ABAB;
  5c only if the partition is off the expected mass ratio.
- **Neither closes, or e- and h-sides disagree, or a ν = 0 gap is already
  open at D = 0 and B → 0** → ABCB or "cannot tell"; escalate to 5b + 5c
  before calling.
- **Region B never resolves** (its ridge too faint in field, its fan lines not
  separable) → per-region verdict for B is "cannot tell", stated, not guessed.
- **Any leakage > 1 nA, clipping that the sensitivity can't fix, or the
  calibration failing its own closure check** → stop, re-measure, and do not
  carry a density scale forward.

## Standing constraints

- Gate limits, field cap (10 T), T cap: committed, **never** touched.
- Si gate stays at 0 V (a standalone Si survey is banned; nothing in this plan
  needs it).
- The magnet is the expensive axis (0.137 T/min, blocking): never re-traverse —
  each step starts where the last one left the field.
