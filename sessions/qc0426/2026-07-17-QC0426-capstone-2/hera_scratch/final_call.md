# QC0426 stacking call — trilayer-stacking-fs-count Step 7 (2026-07-18)

## 1 · Per-region verdicts

| region (channel/pair) | verdict |
|---|---|
| **sr1 (T3–T4)** | **ABA (strong)** |
| **sr2 (B4–B5)** | **ABA (strong)** |
| electron side (both pairs, +n) | uninformative for the binary (by model degeneracy — see hedges), consistent-with ABA |

No region shows ABC-required evidence. The two Rxx regions agree — no
stacking-mosaic signal between the probed pairs.

## 2 · Evidence (each tone: F, (n, D) coordinates, checks)

All at D = 0, hole side unless noted; λ = 1.069 global scale
(Luttinger-pinned, run 7 + run 6; device card updated).

- **f_ML ≈ 4.0–4.3 T** at n = −3.0e12 (runs 5, 8; fan branch across
  n = −1…−3.5e12, run 7): light pocket, harmonic train (2f–4f, decaying),
  survives to 32 K; **m* = 0.019–0.021 mₑ** (runs 8–13, both channels).
  Grid-change reproduction ✓ (5.26 vs 22.6 mT grids).
- **f_BL ≈ 27–28 T** at n = −3.0e12 (runs 5, 7): heavy partner; breaks the
  f_ML-harmonic decay envelope (independent tone); **m* = 0.037–0.064 mₑ**
  (channel spread = BL-window harmonic-contamination systematic, stated).
- **Luttinger partition**: f_ML + f_BL = λF_L within ±2δF (δF = 0.85 T)
  per column where the pair is correctly extracted (run 7, 167 columns
  with resolved triples; upper tone tracks λF_L at median ~1 T across
  |n| = 1–3.5e12) — the algebraic, model-free check.
- **≈λF_L tone (32–33 T)**: strengthens ×2.3 vs f_BL from low-B to high-B
  half (breakdown signature, run 5); collapses fastest under T (gone by
  ~10 K); m* ≈ 0.05 mₑ — between m_BL and m_ML+m_BL → read as the ABA
  **magnetic-breakdown sum orbit** with stated systematics.
- **Electron side** (run 6, n = +3.0e12): bright singleton at 33.2 T =
  λF_L with 2f harmonic. Model (`fs_count_b0`): ABA(e⁻, 3e12) = {1.5,
  29.5} T — the 1.5 T ML is below our resolvable band — vs ABC singleton
  31.0 T: **both templates predict one visible tone** → non-discriminating.
- **Onsager overlay**: electron side consistent with both curves; hole-side
  model curves not computable (model is E_F ≥ 0 only — gap flagged). The
  hole-side overlay is carried by the λF_L algebra instead.
- **CNP gap systematics** (run 4): R_CNP strongly D-tunable (>10×, both
  channels, both D signs, min at D = 0) — consistent-with a D-gapped
  band edge; fed into the read as a hint only, per the recipe's
  domain-caveat rule. Not counted as ABA/ABC evidence.

## 3 · Confidence + hedges

**ABA (strong)** for the probed regions. Specific hedges:

- The **F_L-tone origin** is breakdown-*consistent*, not breakdown-proven:
  m_FL/(m_ML+m_BL) = 0.62/0.84 (sr1/sr2) rather than ≈1, and the beat
  exclusion (lighter-than rule) does not fire. A small ABC domain
  contributing a coincident-frequency tone is **not excluded** — but no
  check requires it, and the B-window growth disfavors a normal pocket.
- **δF = 0.85 T** limits tone splitting; the 23–24 T third heavy band
  (5–6×f_ML vs additional orbit) is unresolved — fork carried, not read.
- **T_e ≈ 8 K floor**: masses fit on T ≥ 6 K rungs; base-rung amplitudes
  consistent with the fits (0.8–1.9 ratio) but not used.
- **Coverage**: contacts probe the T3–T4 and B4–B5 regions only; the call
  is per-region, and unprobed flake area may differ (mosaic caveat). The
  electron side was searched and is consistent, not confirming.
- Absolute scale λ carries the SdH pin; **QH lever-arm (ray quantization)
  not yet run** — no ν assignments are claimed anywhere in this call.

## 4 · What would firm it

1. **Model extension** (`fs_count_b0`): E_F < 0 (hole) curves + m*
   emission → direct overlay of the measured branches and masses
   (README TODO; session_notes RECIPE FIX).
2. **Lower-T rig**: δF and the heavy-band split improve with earlier
   onset; a mK fan would resolve the 23–28 T complex and the F_L-tone
   lineshape.
3. **Step-6 Streda/Chern complement** at 8 T (magnet already there): ABA's
   ML zero-mode offset vs ABC's ν = ±6 sequence — qualitative model in
   `ll_sequence.py`.
4. **Raman cross-check** (`raman-stacking-id` + fusion recipe) for
   flake-wide domain mapping beyond the two probed regions.

## 5 · Contract note

Verdict carried with feature-level evidence per tone (above); a
cannot-tell was on the table until the LK split landed — the mass
hierarchy (0.02 vs 0.04–0.06 mₑ, both channels independently) is what
upgraded consistent-with to **strong**.
