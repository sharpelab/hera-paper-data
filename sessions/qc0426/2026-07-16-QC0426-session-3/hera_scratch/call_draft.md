# QC0426 — stacking call (investigation step 7, output contract)

## 1. Per-region verdicts (strength scale per STYLE)

- **T3–T4 (sr1): ABA (strong).** Two-pocket FS at every density probed: pair {f_ML, f_BL} resolved at n = −6e12 (run 6: 11.1 + 55.3 T), +6e12 (run 7: 9.3 + 55.5 T), and continuously across n = −2.5 → −6e12 (run 9: 74 columns, both branches tracked).
- **B4–B5 (sr2): ABA (strong).** Same pair at both spot-check densities (run 6: 11.1 + 55.3; run 7: 10.2 + 54.6) and partition-consistent on its unclipped fan columns (16 cols, λ = 1.077).
- **T5–B6 (sr3, Hall)**: not an Rxx region probe; contributes the independent density scale (n_Hall/n_gate = 1.02–1.10, both signs) — consistent, no anomaly.
- **No region is uninformative; no mosaic signature** — both Rxx regions show the same template, ridge fits agree to 0.08%, and the F_L-tone tests as breakdown rather than a coexisting ABC-domain singleton.

## 2. Evidence (tones, coordinates, artifacts)

| Tone | (n, D) | Runs | Backing |
|---|---|---|---|
| f_ML 11.1 / f_BL 55.3 T | (−6e12, 0) | 6 (uniform-B), 9 col (uniform-1/B) | grid-change PASS; ana figs runs 6/9 |
| f_ML 9.3–10.2 / f_BL 54.6–55.5 T | (+6e12, 0) | 7 | ana fig run 7 |
| f_ML(n), f_BL(n) branches | (−2.5→−6e12, 0) | 9 | tracked-branch fig; Σf = λF_L, λ = 1.048, rms 1.9 T |
| Sum tone ≈ F_L | ±6e12 | 6, 7 | B-window split: strengthens with B → breakdown/mixing |
| {~24.5, 33.3 T} — two strong tones, f_ML below δF | (+3.0e12, 0) | 10 | consistent-with ABA (ABC predicts one tone); model overlay inconclusive at this point (assignment ambiguity, reported) |

Luttinger check: single global λ = 1.05 (fan) / 1.07 (SCs) / 1.02–1.10 (Hall) — one in-band scale satisfies every population.

## 3. Confidence + hedges

- **Confidence: high** for the two-FS count on both probed regions (hole side decisive; electron side strong at 6e12).
- Hedges: (a) LK mass split unavailable (temperature-dependence blocklisted) — the per-branch mass confirmation of "two genuine bands" is deferred; the n-tracked partition + grid-change + breakdown-test leave the exotic-mixing alternative little room, but it is not mass-killed. (b) Onsager overlay is qualitative for the hole side (model solves electrons only — gap logged); quantitative overlay exists only at run 10's point. (c) A ~5.5 T low-F feature in run 6 wanders with detrender choice — reported as extraction fork, not a pocket. (d) |n| < 2.5e12: f_ML not resolvable (δF floor) — count not claimed there. (e) D_offset = 0 unexamined; count robust to small residual D (ML/BL mixing ∝ D²).

## 4. What would firm it

- LK mass per branch (one heater ladder at (−6e12, 0), temperature-dependence Flavor B) — the decisive two-bands confirmation; blocklisted this session.
- Valence-band model curves (model TODO) for a quantitative hole-side overlay.
- Streda/Chern high-field complement (step 6): ABA-offset QH sequence check on the existing run-9 high-B rows — partial analysis possible from data on disk.
- Lever-arm upgrade: assign ν to run 9's high-B minima → absolute-scale calibration to close the λ loop.

## 5. Verdict

**QC0426, both probed regions: ABA (Bernal) — strong.** Two distinct Fermi surfaces at D ≈ 0 on both density signs, Luttinger-partitioned across a 2.4× density range with one global scale; the ABC single-surface template is excluded wherever the count is resolvable. Not a "cannot tell": the discriminating feature (the ML partner) is resolved, tracked, and grid-change-robust.
