import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

for rid, tag in ((6,'electron n=+3.2e12'), (7,'hole n=-1.2e12')):
    r = open_run(f'data/{rid}')
    print('='*70); print(f'run {rid} — {tag}')
    print(summarize_run(r))
    chs = resolve_channels(r.meta)
    for c in chs: print('  ch', c.cid, c.col, 'gain', c.gain, 'label', c.label, 'is_current', c.is_current)
    cur = current_channel(chs)
    B = r.col('magnet_field')
    I = r.col(cur.col)/cur.gain
    V = r.col('sr1_X')/1.0
    R = V/I
    T = r.col('T_sample')
    print(f'  rows={len(B)} B {B.min():.3f}..{B.max():.3f}  I med {np.median(I):.4e} A (spread {I.min():.3e}..{I.max():.3e})')
    print(f'  T {T.min():.3f}..{T.max():.3f} K')
    print(f'  R med {np.median(R):.1f}  min {R.min():.1f}  max {R.max():.1f} Ohm')
    print(f'  leak |I_tg| max {np.abs(r.col("k_2400_tg_curr")).max():.2e}  |I_bg| max {np.abs(r.col("k_2400_bg_curr")).max():.2e}')
    fs = 50e-6/1.0/np.median(np.abs(I))
    print(f'  full-scale R at 50uV: {fs:.0f} Ohm; max/FS = {R.max()/fs:.2f}')
    np.save(f'hera_scratch/spot{rid}_BR.npy', np.vstack([B,R,T]))
