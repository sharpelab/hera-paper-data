from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset

ROOT = Path(__file__).resolve().parent.parent
fig, axes = plt.subplots(2, 3, figsize=(14, 7), constrained_layout=True)
for row, rid in enumerate((6, 7)):
    run = open_run(ROOT / 'data' / str(rid))
    channels = resolve_channels(run.meta)
    cc = current_channel(channels)
    vc = next(c for c in channels if c.cid == 'sr1')
    B = run.col('magnet_field')
    I = run.col(cc.col) / cc.gain
    V = run.col(vc.col) / vc.gain
    R = np.abs(V / I)
    axes[row, 0].plot(B, V * 1e6, '.', ms=1.5, label='sr1 X (µV)')
    axes[row, 0].plot(B, I * 1e9, '.', ms=1.5, label='drain I (nA)')
    axes[row, 0].set_title(f'run {rid} raw, {"electron" if rid==6 else "hole"}')
    axes[row, 0].set_ylabel('raw physical channels')
    axes[row, 0].legend(fontsize=8)
    axes[row, 1].plot(B, R, lw=0.8)
    axes[row, 1].set_title(f'Rxx = |V/I|, range {R.min():.1f}–{R.max():.0f} Ω')
    for lo, hi, color in [(2, 9.8, 'C0'), (3, 9.8, 'C1'), (4, 9.8, 'C2')]:
        f, spec = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=2048, bg_degree=5, log=False)
        m = (f >= 2) & (f <= 45)
        y = spec[0, m]
        axes[row, 2].plot(f[m], y / y.max(), color=color, label=f'{lo}–{hi} T')
        peaks, _ = find_peaks(y, prominence=0.10)
        top = sorted(peaks, key=lambda p: y[p], reverse=True)[:4]
        print(rid, f'{lo}-{hi}T', [(round(float(f[m][p]), 1), round(float(y[p]/y.max()),2)) for p in top])
    axes[row, 2].set_title('SdH FFT, normalized per window')
    axes[row, 2].set_xlim(2,45)
    axes[row, 2].legend(fontsize=8)
    for a in axes[row]: a.set_xlabel('B (T)' if a != axes[row,2] else 'F (T)')
    print('RUN',rid,'R Ω',np.percentile(R,[0,50,95,100]),'I nA',np.percentile(I*1e9,[0,50,100]),
          'T K',np.min(run.col('T_sample')),np.max(run.col('T_sample')),
          'gate pA max',max(abs(run.col('k_2400_tg_curr')))*1e12,max(abs(run.col('k_2400_bg_curr')))*1e12)
    print(sdh_onset(R, B, b_lo=0.3, b_hi=10, r_full_scale=5000).summary())
fig.savefig(ROOT / 'hera_scratch' / 'sdh_runs6_7.png', dpi=180)
