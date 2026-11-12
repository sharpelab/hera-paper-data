from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_fft

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for row, rid in enumerate((6, 7)):
    rr = open_run(Path('data') / str(rid))
    cc = {c.cid: c for c in resolve_channels(rr.meta)}
    bb = rr.col('magnet_field')
    ii = rr.col('sr0_X') / cc['sr0'].gain
    resistance = np.abs((rr.col('sr1_X') / cc['sr1'].gain) / ii)
    axes[row, 0].plot(bb, resistance, lw=0.9)
    axes[row, 0].set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title=f'data/{rid}: raw four-probe Rxx')
    ff, ss = sdh_fft(resistance[:, None], bb, b_range=(2.0, 10.0), nfft=2048, bg_degree=4)
    spectrum = ss[0]
    axes[row, 1].plot(ff, spectrum)
    axes[row, 1].set(xlim=(0, 65), xlabel='SdH frequency (T)', ylabel='FFT magnitude (arb.)',
                     title=f'data/{rid}: 2–10 T FFT')
    peaks, _ = find_peaks(spectrum)
    peaks = sorted((k for k in peaks if 2 <= ff[k] <= 65), key=lambda k: spectrum[k], reverse=True)[:5]
    print(f'data/{rid}: {len(bb)} points, B {bb[0]:.2f}→{bb[-1]:.2f} T; '
          f'|Rxx| {resistance.min():.1f}–{resistance.max():.1f} Ω; '
          f'I {ii.min()*1e9:.3f}–{ii.max()*1e9:.3f} nA; '
          f'T {rr.col("T_sample").min():.3f}–{rr.col("T_sample").max():.3f} K; '
          f'FFT peaks ' + ', '.join(f'{ff[k]:.1f} T' for k in peaks))
fig.tight_layout()
plt.show()
