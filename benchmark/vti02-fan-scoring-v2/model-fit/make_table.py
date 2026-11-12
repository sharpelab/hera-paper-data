"""Tabulate refit B (corpus ABAB set with gamma2 = -0.0145, gamma3 = 0.3; 2D solve) and the corpus model -> tone_table.csv."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '.')
import swm
n = np.round(np.concatenate([np.arange(-1.60, -0.449, 0.05), np.arange(0.50, 3.6001, 0.05)]), 3)
B = swm.tones_2d(swm.params(g2=-0.0145, g3=0.3), n)
Cc = swm.tones(swm.ABAB, n)
pd.DataFrame(dict(n=n, F_light_B=B[:, 0], F_heavy_B=B[:, 1], F_light_corpus=Cc[:, 0], F_heavy_corpus=Cc[:, 1],
                  F_L=swm.FL_PER_N * np.abs(n))).round(4).to_csv('tone_table.csv', index=False)
print(pd.read_csv('tone_table.csv').iloc[::6].to_string())
