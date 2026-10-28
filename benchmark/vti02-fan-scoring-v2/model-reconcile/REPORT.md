# Tone model reconciliation (agent, 2026-09-23)

## Recommendation

**Halder_ABAB** at D = 0, with no added screening and γ3 on. Nothing in it is fitted to vti-02.
- On every held-out group it matches or beats refit B, including the hole side.
- On clean training data (F_L ≥ 15 T) it ties B.
- It gives the best mass ratio of the candidates, though still too high.

**Fallback: refit B** (γ2 −0.0145, γ3 0.3), used if the Halder middle-pair couplings
(quoted secondhand from Klanurak 2024) fail to check out. Shi_ABAB differs from Halder only in
Δ′, so it is not independent. Keep the corpus model as a secondary score: its hole side is
refuted at about 4σ.

**Frame:** the model-fit F_L-tone frame. Swapping in the literature agent's frame changes
bias/rmse by at most 0.001.

## Partition residuals, observed − model (bias / rmse)

| group | n | corpus | refit B | **Halder** | Shi | graphite + ε 5.7 |
|---|---|---|---|---|---|---|
| train 08-25 | 112 | +0.042 / 0.052 | +0.005 / 0.026 | +0.007 / 0.034 | +0.007 / 0.033 | +0.003 / 0.029 |
| train 08-22 | 125 | +0.036 / 0.041 | +0.001 / 0.019 | +0.001 / 0.021 | +0.001 / 0.020 | −0.003 / 0.020 |
| train, F_L ≥ 15 T | 225 | +0.034 / 0.038 | −0.001 / 0.016 | −0.001 / 0.018 | −0.001 / 0.017 | −0.004 / 0.017 |
| held-out 08-21 electron | 10 | +0.051 / 0.063 | +0.024 / 0.043 | +0.015 / 0.040 | +0.016 / 0.041 | +0.014 / 0.040 |
| held-out 08-24 electron | 1 | +0.022 | −0.034 | −0.009 | −0.011 | −0.023 |
| held-out hole | 7 | −0.113 / 0.114 | +0.028 / 0.032 | +0.015 / 0.022 | +0.025 / 0.030 | +0.035 / 0.038 |

- **Hole side:** χ²/N is 14.8 for the corpus model, 1.3 for B and 0.6 for Halder. γ3 is what
  fixes it, and Halder and B both carry γ3, so the hole data can't separate them.
- **Halder's one loss:** 13 heavy-only points on 08-25 below F_L ≈ 15 T, where the light tone
  has fewer than 2 periods. That is the known ±0.03 low-n systematic, not a clean test.
- **Slopes:** Halder is about 0.01 steeper than the data.
- **Masses** at n 2.8 (heavy/light ratio; measured 1.2–1.5): corpus 2.34, B 2.14,
  Halder 1.84, Shi 1.89, graphite + ε 1.84–2.10. Every model is too high, so any mass-ratio
  rule has to use measured masses.

## Plug-in

`tone_fn.py` has the same interface as model-fit:
`tone_fn(n, side, model='Halder_ABAB') -> (F_light, F_heavy, F_L)`.
- Models: Halder_ABAB (default), Shi_ABAB, graphite_eps5.7, B, corpus, env_lo, env_hi.
- `mstar_fn` gives the masses.
- Tables: electron |n| 0.30–3.60, hole 0.30–2.00, step 0.05. No solver runs at call time.

**Uncertainty band** (env_lo … env_hi, as F_light/F_L):
- electron: 0.131–0.158 at n 1.25, 0.164–0.180 at 1.5, 0.206–0.211 at 2.0, 0.240–0.252 at 3.0.
- hole: 0.276–0.296 at −1.0.
- This is ≤ 0.4 T in F_light at n ≥ 1.5, below δF ≈ 1.1 T. On the dev set it moves each
  episode by ≤ 1 capped-cell step (0.067 in Q).

## Dev-set rescore

`rescore.md` has the full tables, with episodes labelled by observed model. Headlines:
- **Corpus → any refined model:** every fan gains 0–12 columns and 0–0.20 in Q. The one
  exception is live 0824-r4, whose hole columns only the corpus credits.
- **B → Halder:** Halder counts 0–4 fewer columns at low n, but Q is equal or higher.
- **Sensitive episodes:** the two opus-none fans, haiku 3xn8hn #00, sonnet 232408 and luna
  tayua3 #00.
- **2.4 T-start fans:** 0 under every model.
- **Opus arm gap** (corpus − none, mean Q): 0.33 under the corpus model, 0.30 under B,
  0.20 under Halder. The model choice changes the effect size, so it belongs in the multiverse.
- **Clips:** the flat 0.75 T clip and the per-column Dingle clip give nearly the same columns.
- **Frame sensitivity:** Q moves up to 0.13 under the 08-22 frame variant; the ordering
  doesn't change.

## Contradicts the proposal

1. The corpus undercount is not uniform across arms: 0–12 columns, and the opus none arm gains
   the most.
2. The mass-scaled clip used the corpus light/heavy ratio of 0.42. Halder gives 0.54, and the
   measured ratio is 0.67–0.83.
3. 08-25 n_scale should be 0.95 in `cases.toml`; the live 0825-r8 rows here still use 1.0.

## Artifacts

- Plug-in and tables: `tone_fn.py`, `tone_table.csv`, `tone_table_all.csv`,
  `compute_tones.py`, `make_table.py`.
- Evaluation: `evaluate.py`, `eval_partition.csv`, `eval_summary*.csv`, `eval_masses.csv`.
- Rescore: `rescore.py`, `rescore.csv`, `rescore.md`.
