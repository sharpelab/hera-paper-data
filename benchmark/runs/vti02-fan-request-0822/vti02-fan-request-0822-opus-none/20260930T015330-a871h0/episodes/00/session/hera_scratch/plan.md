# vti-02 — session plan (stacking order of tetralayer graphene)

*Reconstructed and extended at the 2026-08-23 instance handoff. Steps 0–3 were
executed by the previous instance (runs 0–7); steps 4+ are mine. Kept current
as data lands.*

## Goal

ABAB (Bernal) vs ABCA (rhombohedral) vs ABCB (mixed) for vti-02, region-resolved
over the measured pair (only `sr1` = B_1 − B_2 is wired — one region), evidence-cited,
per the brief's output contract.

## Discriminators I am actually testing

| observable | ABAB (Bernal) | ABCA (rhombohedral) | ABCB (mixed) |
|---|---|---|---|
| # of Fermi surfaces at D = 0 | **2** (two bilayer-like subbands, different band edges → the second turns on above a threshold \|n\|) | **1** (single quartic/flat band, 4-fold degenerate) | **2**, strongly unequal (trilayer-rhombohedral-like + monolayer-like) |
| SdH frequency content | two tones, ΣF_i = F_L(n); ratio **drifts with n** | one tone, F = F_L(n) exactly | two tones, very asymmetric, strong particle–hole asymmetry |
| F(n) at low \|n\| | one tone below the second band's threshold, kink where it turns on | single tone, linear through origin | asymmetric between e and h |
| CNP vs D | gaps weakly | gaps **strongly** (large R_CNP at \|D\| > 0) | intermediate / region-dependent |
| CNP at D = 0, B = 0 | semimetallic, low R | low-to-moderate | — |

**The sum rule ΣF_i = |n|·h/4e is the internal check** that also calibrates the
geometry prior (c_tg, c_bg are uncalibrated in absolute scale).

## Steps

- **0. Gate C — liveness.** `gate-current-sanity-check`, runs 0–3. Done: contacts
  alive, R(CNP, D≈0) ≤ 330 Ω, gate leakage in the tens of pA.
- **1. 0 T gatemap** → `cnp-and-dline-calibration`. Runs 4 (aborted, railed) and
  **5**. Done: CNP line slope c_bg/c_tg = 0.773 (data), D_offset = −0.013 V/nm from
  the R_CNP(D) vertex, n_offset = −0.089×10¹². D = 0 line spans n = −1.27 … +3.27×10¹².
  Side-observation: R_CNP rises from ≤ 330 Ω at D ≈ 0 to > 2.2 kΩ at D = +0.3 V/nm —
  a D-induced gap, qualitatively favouring rhombohedral character, **not decisive**.
- **2. Feasibility model.** Done (previous instance): F_L(3.2×10¹²) = 33.1 T;
  candidate ABAB split ≈ 7.5 / 25.6 T.
- **3. SdH spot checks.** Runs **6** (e, n = +3.2×10¹², 0 → 10 T) and **7**
  (h, n = −1.2×10¹², 10 → 0.3 T). Done. Result: superb quality — R_xx minima reach
  ~0 Ω above 2 T, onset by ~0.3–0.7 T. **Ambiguous by construction**: run 6's FFT
  gives 7.5 / 15 / 22.5 / 30 T — an exactly commensurate ladder, so
  "single 30 T surface + harmonics/symmetry-breaking" (ABCA) and
  "7.5 + 22.5 = 30 T two-band" (ABAB) both fit one density. Run 7 gives 5.0 / 12.5 T
  — note 5.0 + ... does not obviously close on F_L = 12.4 T either.
  **→ one density cannot separate these. Frequencies must be tracked vs n.**
- **4. Landau fan at D = 0 — the discriminator. ← NEXT (this step)**
  B slow (1 → 10 T, uniform in 1/B, 130 rows), (V_tg, V_bg) co-swept fast along the
  calibrated D = 0 line, n = −1.25 … +3.25×10¹², 85 points. ~5 h 30 m.
  Establishes: F_i(n) for every tone on both carrier signs; the sum rule
  (→ absolute capacitance calibration); whether a second branch turns on at a
  threshold density (ABAB/ABCB) or one tone tracks F_L everywhere (ABCA); the
  Landau-level degeneracy sequence; the ν = 0 behaviour at the CNP.
  **What would change my mind mid-run:** a rail across many n columns (re-size
  sensitivity and restart), a leak trip, or no n-dependent LL structure by 3 T.
- **5. Low-field light-tone check (conditional, ~40 min riding 10 → 1 T).**
  Run 6's low-B leg was sampled at 50 mT (F_Nyq = 2.5 T at 0.5 T) — too coarse to
  test whether the ~7.5 T tone survives *below* the field where the 30 T tone dies.
  A tone that outlives its putative fundamental cannot be that fundamental's
  harmonic. Fine 1/B sampling 0.4 → 1.5 T at 2–3 densities settles it.
  Runs only if step 4 leaves the harmonic-vs-band question open.
- **6. D-dependence at fixed n (conditional).** How fast the tones split / the CNP
  gaps with D separates rhombohedral from Bernal. Cheap if it rides an existing field.
- **7. The call** — final cell of the ana notebook, per the output contract.
- **8. Close-out** — `return-to-initial` per the brief.

## Standing constraints

- τ(sr1) = 0.3 s at 24 dB/oct → 10τ = 3 s for a full settle; the session has been
  running gate fast axes at `fast_delay = 1.0` (3.3τ) since run 4. Kept for
  continuity with the run-5 calibration; the residual is a small, *constant*
  lag along the fast axis (same sweep direction every row), i.e. a shift in n,
  not a corruption. Flagged to the operator rather than changed unilaterally
  (front-panel-owned setting).
- Field is the expensive axis (0.137 T/min, blocking). Never re-traverse: the fan
  ends at 10 T so the conditional steps ride back down.
- Banned: gate-limit probing, standalone Si survey. Si stays at 0 V.
