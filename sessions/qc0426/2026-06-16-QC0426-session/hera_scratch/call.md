# Stacking call — QC0426 (trilayer graphene), VTI, 2026-06-16

**FS-count at D=0 (`trilayer-stacking-fs-count`). Independent, blinded, region-resolved. Output contract (5 parts).**

## 1. Per-region verdict (STYLE strength scale)
One contiguous region probed (hole side, D=0), two Rxx pairs:
- **sr1 (T3–T4, top arc): cannot-tell ABA vs ABC — resolution-limited; consistent-with ABC (weak).**
- **sr2 (B4–B5, bottom): cannot-tell — resolution-limited; consistent-with ABC (weak).**
- Channels **agree** (no mosaic/domain disagreement detected) — but both are resolution-limited, so the agreement is weak evidence of uniformity, not a clean single-domain finding.

## 2. Evidence
- **Dominant SdH tone — F = 41.2 T at n = −4.0×10¹² cm⁻², D=0, hole side** (go/no-go, file_id 2; FFT in 1/B over B∈[2.5,7.95] T; **detrender-stable** across poly6/poly8/Gaussian high-pass). This equals the **full-density Luttinger value** F_tot = n·h/4e = 41.4 T (ratio 0.995).
- **Fan (file_id 3)**: the dominant tone **disperses with |n|**, tracking the full-density / ABA-BL line across n = −1.4 → −5.0×10¹² (heatmap + go/no-go anchor; **qualitative** — per-column F(n) is thermally broadened, not cleanly extractable). Model curves valid only |n| ≤ 3.5×10¹² (forward-model E_F/kmax cap).
- **Luttinger**: the single resolved tone alone accounts for n (Σf = n·h/4e). No resolved density deficit demanding a second pocket.
- **Non-pocket feature**: a **constant-F band at ~5–9 T that does NOT disperse with n** → fixed offset / artifact (fails the Onsager-tracking requirement), **not** a Fermi surface. The faint ~5.5 T feature in the go/no-go wide window is this same non-dispersing artifact.
- **Not resolvable**: the discriminating **ABA ML (Dirac) tone**, predicted F ≈ 1–2 T here. Below the SdH onset (~2 T), below the frequency resolution (δF ≈ 2.7 T fan / 3.6 T go/no-go), below the F>3 T analysis floor, and thermally smeared (device **T_e ≈ 8 K**). **Searched-and-not-resolvable**, not searched-and-absent.

## 3. Confidence + hedges
- Confidence in an ABA/ABC distinction: **LOW (resolution-limited).**
- The **big tone is non-discriminating by design**: ABA-BL ≈ ABC-single to within a few % (< resolution) over the accessible n — confirmed by the coincident model curves.
- The weak ABC lean rests only on the single tone carrying the **full** Luttinger density (no resolved deficit), itself within resolution of the ABA-BL prediction (~92–95% of full).
- Hedges: hole side only; D=0 (ratio data-calibrated, scale geometry-prior); single region (2 pairs, both limited); sample base 1.2 K but **T_e~8 K dominates smearing**; absolute n-scale geometry-prior (QH lever-arm not yet applied — though F = full-density at the geometry-n is a consistency check that the scale is ≈right).

## 4. What would firm the call
- **High-field Streda/Chern LL-offset (Step 6)** — ABA's ML Dirac inserts an N=0 zero-mode shifting the QH sequence vs ABC's ν=±6-centred 12-fold zero LL; bigger gaps, resolvable at this T/field. Rxy(sr3) to 8 T already in hand (file_id 3); **quantitative ABC-LL overlay model is pending** (survey §9) — the recommended next analysis.
- **Lower T / higher mobility (mK rig)** — drop T_e below the ML cyclotron gap to resolve the F~1–2 T tone and sharpen the spectrum.
- **LK mass split** (`temperature-dependence` Flavor B) — two masses → two bands (ABA); one → one band. **Blocklisted this session**; flag for a follow-up.
- **QH lever-arm** to upgrade the absolute n-scale and sharpen the Luttinger comparison.

## 5. Bottom line
**A calibrated "cannot tell" with reasons — a successful outcome per the contract.** The robust positive finding is a **single, full-density-carrying Fermi surface** (consistent-with ABC single pocket, indistinguishable from ABA-BL at this resolution). The discriminating ML tone is not resolvable in the accessible (n, D, B, T_e) envelope. **A confident ABA/ABC call is not supported by feature-level evidence and would be a protocol violation.**

*Provenance: gates A/B/C ✓; (n,D) calibration file_id 1 (c_bg/c_tg=1.298, ratio data-grade, scale geometry-prior). Go/no-go file_id 2. Fan file_id 3 (D=0 hole side, B 7.95→0.5 T). Forward model `fs_count_b0.py`. Analysis: hera_scratch/{gonogo_fft2,fan_figure}.py.*
