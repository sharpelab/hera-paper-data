**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.** Ablation-series lock (no-corpus offline stages); design + grading: Primer doc "HERA T1 no-corpus control - vti-02.md". Locked as produced; not edited.

# vti-02 — transport call (locked; session 2026-08-23)

## Provenance

- Session: E1 HERA tactical on the VTI, 2026-08-23 20:27 → 2026-08-24 11:16
  (rig local). Corpus commit `039b0f5`, clean at session build
  (`corpus_provenance.json`).
- Transcript: `fc1603b4-2a86-4d23-ae59-5528ec1d09c7.jsonl`.
- Call: ana notebook `20260823_ana.ipynb` final cell, appended
  2026-08-24T09:18:46Z. Text below is that cell, verbatim.

---

# FINAL CALL — vti-02 stacking order (session 2026-08-23/24)

## Per-region verdict
- **Pair B_1–B_2 (sr1; source T_0 → drain B_3) — the only measured region: ABAB (Bernal), strong.**
- No other region measurable this cooldown: T_1–T_4 dead as provided, sr2/sr3 not connected — no second contact pair, no Rxy.

## Evidence (session runs only)
1. **R_CNP(D), B = 0** (data/3, data/4): minimum 248 Ω at D0 = (V_tg, V_bg) = (0.11, 0.00); rises ×14 to ≈3.4 kΩ by D−D0 ≈ +0.23 V/nm and **saturates** to the box edge (+0.32). ABCA would be ≫MΩ and exponential in D at 1.2 K.
2. **D-symmetry** (data/4): R(−D)/R(+D) = 0.85–0.90 over |D−D0| = 0.04–0.125 V/nm — inversion-symmetric response → excludes ABCB (no inversion/mirror).
3. **Landau fan at D ≈ 0** (data/6): minima at ν = −12, −8, −4, +4, +8, +12, +16, +20 (**4-fold steps; ν = ±4 robust to the lowest resolvable B**) — Bernal two-sector LL structure, not ABCA's 16-fold zero-energy manifold (ν = ±8-first). **ν = 0 grows non-monotonically** (dips at ≈2.4 and ≈7.2 T: zero-manifold LL crossings — a Bernal-multilayer fingerprint).
4. **Landau fan at D−D0 ≈ +0.20** (data/7): the sequence splits to **steps of 2** (ν = ±2, ±4, +6, ±8) and ν = 0 becomes monotonic (73 kΩ at 8 T) — D-polarized bilayer-like LLs.
5. **Activation** (data/8–18): Δ ≈ 1.8 meV at D−D0 = +0.28, 1.2 meV at +0.19, ≈0 at |D−D0| ≤ 0.11; residual R(∞) ≈ 1.1 kΩ. meV-scale, weakly D-dependent gap ↔ Bernal; not ABCA's tens of meV.
6. **Calibration** (this session): c_bg/c_tg = 0.71 (data/3/4 CNP-line slope), n = 0.82 × n_geo (data/6 ν-line fit); all n, D values above are on this session's own scale (geometry-prior D units).

## Confidence and hedges
- **Would overturn:** an activation gap ≫10 meV at reachable D (excluded by data/8–18); strongly D-asymmetric transport (excluded by data/4 within the ±0.125 V/nm overlap); a ν = ±8-first LL sequence (excluded by data/6).
- **Not measured:** any second region (all spare contacts dead as provided — a boundary between stacking domains elsewhere in the flake is invisible to this pair); Rxy (no wired probe pair); |D−D0| > 0.32 V/nm; T < 1.17 K; the −D side beyond −0.13 V/nm (box limit).
- **Secondary feature:** a weak parallel resistance line ≈0.4 V below the CNP line in V_bg (≈−0.5e12 cm⁻²; data/1, data/3) is D-flat, ≈300 Ω, contributes no LL signature of its own in data/6/7 — most consistent with a contact-doped strip near a probe, not a second stacking domain; it does not affect the verdict.
- ABCB with accidentally compensated asymmetry cannot be excluded by symmetry alone, but the observed 4-fold → 2-fold LL evolution and ν = 0 crossing pattern match ABAB specifically.