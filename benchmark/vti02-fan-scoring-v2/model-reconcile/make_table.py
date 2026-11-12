"""tone_table_all.csv -> tone_table.csv (the plug-in's table): per n, F_light_<model> for every model on a common grid
(e 0.30-3.60, h -2.00..-0.30, step 0.05) plus the envelope env_lo / env_hi = min / max F_light over the four
non-corpus models (B, Halder_ABAB, Shi_ABAB, graphite_eps5.7) and the masses of each model. F_heavy = F_L - F_light."""
import numpy as np, pandas as pd
T = pd.read_csv('tone_table_all.csv')
N = np.round(np.concatenate([-np.arange(2.0, 0.2999, -0.05), np.arange(0.30, 3.6001, 0.05)]), 3)
out = pd.DataFrame(dict(n=N, F_L=10.3392 * np.abs(N)))
for m in ('corpus', 'B', 'Halder_ABAB', 'Shi_ABAB', 'graphite_eps5.7'):
    t = T[T.model == m].set_index('n')
    for c in ('F_light', 'm_light', 'm_heavy'):
        out[f'{c}_{m}'] = t[c].reindex(N).values
four = out[[f'F_light_{m}' for m in ('B', 'Halder_ABAB', 'Shi_ABAB', 'graphite_eps5.7')]].values
out['F_light_env_lo'] = four.min(1); out['F_light_env_hi'] = four.max(1)
assert not out.isna().any().any(), out[out.isna().any(axis=1)]
out.round(5).to_csv('tone_table.csv', index=False)
print(out.shape)
