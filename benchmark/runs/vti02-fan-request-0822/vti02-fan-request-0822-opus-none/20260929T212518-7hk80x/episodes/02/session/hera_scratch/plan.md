# vti-02 — stacking-order plan (`hera_scratch/plan.md`)

*Reconstructed at the 2026-08-23 handoff (the pre-handoff instance left no
plan file — see session_notes PROTOCOL). Steps 0–3 are done; the numbering
below is the one already cited in the measure notebook's markdown.*

**Goal.** Region-resolved call on the stacking of tetralayer vti-02:
ABAB / ABCA / ABCB / cannot tell, evidence-cited, per the brief's output contract.

**Discriminator physics (what any step is trying to buy).** All three stackings
carry total chirality 4, so the zero-LL degeneracy at the CNP (16) is *not* a
discriminator. What separates them is how the four layers partition into bands,
i.e. how the total density partitions among Fermi surfaces:

| stacking | band decomposition | SdH signature at density n |
|---|---|---|
| ABCA | one J = 4 (quartic) band | **one** frequency, F = \|n\|h/4e — the full-density Onsager value |
| ABAB | two J = 2 (bilayer-like) bands, unequal m\* | **two** frequencies summing to F_L, comparable fractions |
| ABCB | J = 1 (monolayer-like) + J = 3 | **two** frequencies summing to F_L, strongly asymmetric partition |

So the call rests on *counting Fermi surfaces and measuring their density
partition* — and every branch must scale with n (dF/dn = h/4e per unit
fraction, through the CNP). A branch that does **not** move with n is a
parallel/fixed-density path, not a band of the gated channel.

## Steps

- **Gate C — `gate-current-sanity-check`** (runs 0–3). *Done.* Device alive on the
  provided contacts, no leakage. **Two** resistance maxima on each gate → two
  CNPs in series between B_1 and B_2: a series mosaic (regions A and B). Carried
  forward as the standing confound.
- **Step 1 — `gatemap`, 0 T** (run 4 aborted/railed, **run 5** good). *Done.*
  Two parallel CNP ridges → the mosaic is two regions of the same gate stack,
  region B electron-doped by 0.43×10¹² vs A. Ridge A R_CNP 240 Ω at D ≈ 0 rising
  to ~2.4 kΩ at D ≈ +0.25 V/nm — a D-tunable gap, *not* by itself a stacking read.
- **Step 2 — `cnp-and-dline-calibration`** (from run 5). *Done.* c_bg/c_tg = 0.773
  (data), c_tg = 2.796 mF/m² **from the 9.5 nm geometry prior — absolute n scale
  uncalibrated**, n_offset −0.089×10¹², D_offset −0.013 V/nm. D = 0 line inside
  the validators: n = −1.27 … +3.27×10¹².
- **Step 3 — `sdh-spot-check`** (**runs 6, 7**), e-side n = +3.2×10¹², h-side
  n = −1.2×10¹². *Done; analysed at the handoff (`ana_sdh_spots.py`).* Strong SdH,
  onset ≲ 0.7–1.3 T, clean to 10 T. Two families in the spectra:
  - a branch near the full-density value — 29.6 T at n = +3.2 (F_L = 33.1 T) and
    12.2 T at n = −1.2 (F_L = 12.4 T): **scales with n, one 4-fold FS carrying
    ~all the density** → leans ABCA;
  - a dominant ~7.0 T tone present at **both** densities (with its 2×/3×/4×
    harmonics) — density-*independent*, so not a band of the gated channel.
    Candidate: the mosaic's other region, a contact-doped pocket, or a
    non-SdH periodicity.
  A 1-D spot cannot separate these. **That is what Step 4 is for.**

- **Step 4 — `landau-fan` at D = 0 (NEXT).** R_xx(n, B), n fast along the D = 0
  line (−1.25 … +3.24×10¹², 113 pts), B slow, **uniform in 1/B** 1.0 → 10 T
  (109 rows, F_Nyq 60 T, Δf 1.11 T) plus a B = 0 anchor row. What it establishes:
  1. **F(n) per column** (per-column FFT in 1/B) — the branch count and the
     density partition. One branch at F = \|n\|h/4e → ABCA; two branches summing
     to it → ABAB vs ABCB by the partition asymmetry.
  2. **Density-independent branches fall out as horizontal lines in the F–n
     plane** — the ~7 T tone is diagnosed, not guessed.
  3. **The mosaic resolves**: two CNP apexes at different n, each with its own
     fan, or one apex → tells us whether the SdH is one region or two in series.
  4. **Absolute density calibration, prior-free**: LL line slopes dn/dB = νe/h
     fix the n scale, retiring the 9.5 nm geometry prior (currently the largest
     systematic — the 11 % F vs F_L shortfall at n = +3.2 is within it).
  - *Changes my mind:* a single branch tracking F_L with no second branch
    anywhere on either carrier side → ABCA. Two comparable branches → ABAB.
    A light + heavy pair with a strongly asymmetric split → ABCB. No branch
    tracking n at all → the calibration or the contact pair is the problem, not
    the stacking.

- **Step 5 — follow-ups, chosen from the fan** (not yet committed):
  - if ABCA-leaning: a **D-dependence** check — the gap at the CNP vs D
    (run 5 already shows the D-tunable gap; a fan or a gate cut at finite D
    tests whether the single branch survives, as it must for a J = 4 band);
  - if two branches: a **T-ladder** at one density for m\* via Lifshitz–Kosevich,
    which separates ABAB's (0.03, 0.06) m_e pair from ABCB's
    monolayer-like/trilayer-like pair. Note T_e ≈ 8 K on this rig caps what LK
    can resolve — light masses are LK-dead here.
- **Close-out — `return-to-initial`** per the brief.

## Standing hedges

- Absolute n (hence F_L) rests on the 9.5 nm hBN geometry prior until Step 4
  calibrates it from the fan. All "F vs F_L" comparisons before that carry a
  ~10 % systematic.
- Series mosaic (two CNPs between B_1 and B_2): R_xx is a sum over two regions.
  Any two-frequency read must be checked against "two regions at 1.13× density"
  before it is read as "two bands".
- One contact pair only (B_1 − B_2). "Region-resolved" in the output contract
  can only mean this pair; the mosaic is *inside* it. Say so in the call.
