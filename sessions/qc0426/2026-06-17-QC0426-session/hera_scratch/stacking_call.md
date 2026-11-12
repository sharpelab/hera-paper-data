# STACKING CALL — QC0426 trilayer graphene: **ABA (Bernal)**, strong

*Independent FS-count determination per `investigations/trilayer-stacking-fs-count.md`,
from this session's data only (strict isolation; no prior-campaign input). Output
contract, all five parts.*

## 1. Per-region verdict (strength scale)

- **sr1 / pair T3–T4 (top arc): ABA (strong).** Two-tone partition resolved at
  n=±8e12 (spot checks, runs 4/5) and tracked across the fan (run 6, 15/33 columns;
  18 low-n columns excluded for high-B overload). λ ≡ (f_ML+f_BL)/F_L = 1.083 ± 0.055.
- **sr2 / pair B4–B5 (bottom): ABA (strong).** Partition robust across 29/33 fan
  columns; λ = 1.056 ± 0.074; corroborated by both spot checks.
- **Device-level: ABA, both probed regions agree — no stacking mosaic detected.**
  sr1 and sr2 give the *same* partition (f_BL/F_L ≈ 0.85, f_ML/F_L ≈ 0.20) → single
  stacking across the contacted area. Rxy (Hall pair T5–B6) provided the consistent
  density cross-check.

## 2. Evidence (frequencies, coordinates, Luttinger check)

- **f_BL ≈ 0.85·F_L — bilayer-like (quadratic) pocket.** n=+8e12,D=0: 70 T (sr1),
  69 T (sr2); n=−8e12,D=0: 72 T both. Tracks ∝n across the fan. Detrender-robust
  (poly 3/5/7 × hann/blackman).
- **f_ML ≈ 0.20·F_L — monolayer-like (Dirac) pocket** (the discriminating small
  partner). n=+8e12: 16 T (sr1), 19 T (sr2); n=−8e12: 16 T both. Detrender-robust;
  mildly window-sensitive (the known f_ML extraction fork).
- **Luttinger sum (the decisive FS-count evidence):** f_ML+f_BL = λ·F_L with
  λ = 1.06–1.08 **constant across density** in both channels (fan), and λ matches
  the Hall-slope rescale (n_H/n_gate = 1.05–1.07). Model-independent, robust across n
  → **two Fermi surfaces**, not one.
- **Onsager forward-model overlay: NOT performed at the operating density** — the
  model (`fs_count_b0`) clamps F(n) above |n|≈3.5e12, below the ±8e12 operating point
  (model README). ML/BL labeling is by pocket size + band-structure expectation, not
  curve shape.
- **Coverage:** 4 fixed-density spot checks (2 channels × hole/electron) + a 33-column
  electron fan, all showing the pair. **No measurement showed a single tone at F_L**
  (the ABC signature).

## 3. Confidence + hedges

**Binary ABA-vs-ABC: confident (ABA).** The investigation's binary criterion —
partition robustness, model-independent — is satisfied across density, both channels,
both sides. ABC is excluded (the small ML partner is resolved and robust).

Hedges (why "strong", not "decisive"):
- **LK effective-mass split NOT measured** — the gold-standard two-band confirmation
  and rigorous beat exclusion (`temperature-dependence`, **blocklisted** this session).
  Beat exclusion here rests on the FFT/partition argument (a beat would not yield an
  independent f_ML∝n branch satisfying f_ML+f_BL=F_L across density) — strong, but not
  the decisive mass cross-check.
- **Onsager overlay unavailable** at operating density (model clamp) — ML/BL by size.
- **Low-n columns clipped** at high B (sr1 18/33, sr2 4/33) from the climbing MR; the
  partition rests on the unclipped mid-/high-n columns (sr2: 29).
- **Warm rig** (base ≈1.2 K, T_e ≈8 K): the count is at the resolvable level; no claim
  about features *absent* at this T (those are "unresolved, not absent").
- **n-scale:** absolute n carried a ~7% geometry-prior error, now upgraded via the SdH
  lever-arm (λ) and the Hall slope (two independent, agreeing).

## 4. What would firm / extend

- **LK mass split** (`temperature-dependence` Flavor B) — the decisive ML-light /
  BL-heavy two-mass confirmation + beat exclusion. (Blocklisted this session; the
  natural next step.)
- **Onsager overlay** once the `fs_count_b0` clamp is extended past 8e12 (model TODO).
- **Lower T / higher mobility (mK rig)** — sharpens the small ML tone for any ABA
  QHF / interaction follow-up.

## 5. Bottom line

**QC0426 is ABA (Bernal) trilayer graphene — strong, both probed regions (T3–T4,
B4–B5), both density sides.** Two coexisting Fermi surfaces (ML Dirac + BL parabolic)
partition the Luttinger density robustly across n; ABC is excluded. The one cross-check
short of "decisive" — the LK mass split — was blocklisted this session and is the
recommended next step. This is a confident call backed by feature-level evidence (the
required standard), not a bare lean.

**Campaign implication (`fs-count` Next):** ABA-confirmed → conventional trilayer; the
correlated/flat-band physics lives on the ABC side, so the high-value QHF/interaction
follow-up needs lower T and higher mobility (an mK rig). Deprioritize on the VTI unless
the QHF angle is pursued.

*Evidence in this notebook: spot A (cell 15), spot B (cell 17), fan F(n) (cell 19);
calibration (cells 12–13). Raw runs: data/4 (e spot), data/5 (h spot), data/6 (fan);
data/2 (gate map). Acquisition/QA log: session_notes.md.*
