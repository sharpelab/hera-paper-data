"""Q1/Q2 frame: every hole-side D ~ 0 trace (multi-density sweeps split per density) with its acquisition, grid and
densities in each frame.  Writes inventory.csv and frames.csv."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from tones import n_ref

LL = pd.read_csv('ll_frames.csv')
rows = []
for t in load_all(n_max=-0.05):
    B = t['B']; u = np.sort(1 / B); du = np.diff(u)
    n, src = n_ref(t)
    rows.append(dict(trace=t['id'], session='2026-08-' + t['session'][2:], run=t['run'], col=t['col'], kind=t['note'], grid=t['grid'],
                     n_frame=round(t['n_frame'], 3), n_scale=t['n_scale'], n_grader=round(t['n_act_e'], 3), n_ref=round(-n, 3), n_ref_src=src,
                     B_min=round(float(B.min()), 2), B_max=round(float(B.max()), 2), points=int(B.size), span_invT=round(float(u[-1] - u[0]), 3),
                     nyquist_worst_T=round(0.5 / du.max(), 1), I_nA=round(t['I_nA'], 1), tau_s=t['tau_s'], sens_V=t['sens_V'], T_K=round(t['T_K'], 2),
                     R_median_ohm=round(float(np.median(t['R'])), 0)))
I = pd.DataFrame(rows); I.to_csv('inventory.csv', index=False)
F = [dict(trace='0822-r7', n_frame=-1.200, grader_scale_only=-1.063, session_offset_frame=-0.949, F_L_tone=-0.907, QH_or_LL=-1.011, note='QH nu 7,6,5 at 6.0/6.96/8.34 T (spread 0.3 %); F_L-like tone 9.38 T'),
     dict(trace='0824-r5-c0', n_frame=-0.800, grader_scale_only=-0.720, session_offset_frame=np.nan, F_L_tone=-0.726, QH_or_LL=-0.714, note='LL fan 08-24 r4 hole fit s 0.85 n0 +0.03 (e-side fit gives -0.733)'),
     dict(trace='0824-r4-c1', n_frame=-0.967, grader_scale_only=-0.870, session_offset_frame=np.nan, F_L_tone=-0.857, QH_or_LL=-0.847, note='F_L tone sub-threshold (contrast 3.3)'),
     dict(trace='0824-r4-c2', n_frame=-0.897, grader_scale_only=-0.807, session_offset_frame=np.nan, F_L_tone=-0.798, QH_or_LL=-0.788, note='F_L tone sub-threshold (contrast 2.0)'),
     dict(trace='0825-r7-c0', n_frame=-0.900, grader_scale_only=-0.855, session_offset_frame=np.nan, F_L_tone=np.nan, QH_or_LL=-0.842, note='QH nu 8,7,6 at 4.28/5.03/5.83 T (1.2 %); branch 7,6,5 (0.720, 1.5 %) excluded by the heavy tone')]
Fr = pd.DataFrame(F); Fr['FL_over_grader'] = (Fr.F_L_tone / Fr.grader_scale_only).round(3); Fr['QH_over_grader'] = (Fr.QH_or_LL / Fr.grader_scale_only).round(3)
Fr.to_csv('frames.csv', index=False)
pd.set_option('display.width', 250)
print(I.drop(columns=['n_ref_src']).to_string(index=False)); print(Fr.to_string(index=False)); print(LL.to_string(index=False))
