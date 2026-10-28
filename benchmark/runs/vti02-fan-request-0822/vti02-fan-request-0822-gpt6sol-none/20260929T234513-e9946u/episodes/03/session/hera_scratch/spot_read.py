from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset

fig, ax = plt.subplots(2, 2, figsize=(12, 8))
for row, rid in enumerate((6, 7)):
    run = open_run(f'data/{rid}')
    B = run.col('magnet_field')
    channels = {ch.cid: ch for ch in resolve_channels(run.meta)}
    I = run.col('sr0_X') / channels['sr0'].gain
    V = run.col('sr1_X') / channels['sr1'].gain
    R = np.abs(V / I)
    ax[row, 0].plot(B, R, '.', ms=1.5)
    ax[row, 0].set(title=f'Run {rid}: raw B sweep', xlabel='B (T)', ylabel='|Vxx / I| (Ω)')
    ax[row, 0].grid(alpha=.2)
    f, spec = sdh_fft(R[:, None], B, b_range=(2, 10), nfft=4096,
                      bg_degree=5, log=False)
    ax[row, 1].plot(f, spec[0])
    ax[row, 1].set(xlim=(0, 80), title=f'Run {rid}: FFT of B=2–10 T',
                   xlabel='1/B frequency (T)', ylabel='FFT amplitude (a.u.)')
    ax[row, 1].grid(alpha=.2)
    onset = sdh_onset(R, B, b_hi=10, b_lo=1, r_full_scale=5000)
    print(f'run {rid}: R median {np.median(R):.1f} Ω, max {np.max(R):.1f} Ω, '
          f'max |V| / 50 µV {np.max(np.abs(V))/50e-6:.3f}, '
          f'max |I_tg| {np.max(np.abs(run.col("k_2400_tg_curr")))*1e12:.0f} pA, '
          f'max |I_bg| {np.max(np.abs(run.col("k_2400_bg_curr")))*1e12:.0f} pA')
    print(onset.summary())
fig.tight_layout()
fig.savefig(Path('hera_scratch/spot_runs_6_7.png'), dpi=160)
