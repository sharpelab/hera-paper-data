import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run
file_path = next((p / "data" for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "6").is_dir()), None)
assert file_path is not None, "session data directory not found"
run = lambda i: open_run(file_path / str(i))
# Runs 6 and 7: raw traces first, then the resolved spectra. No instrument access.
from hera.analysis import resolve_channels, current_channel, sdh_fft
from scipy.signal import find_peaks

fig, axes = plt.subplots(2, 2, figsize=(12, 7.5))
for row, rid in enumerate((6, 7)):
    rr = run(rid)
    channels = resolve_channels(rr.meta)
    cur = current_channel(channels)
    vxx = next(c for c in channels if c.n == 1 and not c.is_current)
    B = rr.col('magnet_field')
    I = rr.col(cur.col) / cur.gain
    R = np.abs((rr.col(vxx.col) / vxx.gain) / I)
    order = np.argsort(B)
    axes[row, 0].plot(B[order], R[order], lw=0.8)
    axes[row, 0].set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title=f'data/{rid}: raw four-probe trace')
    print(f'data/{rid}: {rr.rows} points, B={B[0]:.2f}->{B[-1]:.2f} T, '
          f'T_sample={rr.col("T_sample").min():.3f}-{rr.col("T_sample").max():.3f} K, '
          f'|Rxx|max={R.max():.0f} Ω, I_median={np.median(I)*1e9:.2f} nA, '
          f'|Vxx|max/50µV={np.max(np.abs(rr.col(vxx.col)/vxx.gain))/50e-6:.3f}, '
          f'|I_TG/BG|max={np.max(np.abs(rr.col("k_2400_tg_curr")))*1e12:.0f}/'
          f'{np.max(np.abs(rr.col("k_2400_bg_curr")))*1e12:.0f} pA')
    freq, spec = sdh_fft(R[:, None], B, b_range=(2, 10), nfft=4096, bg_degree=5, log=False)
    use = (freq > 2) & (freq < 60)
    axes[row, 1].plot(freq[use], spec[0, use], lw=0.9)
    axes[row, 1].set(xlabel='SdH frequency (T)', ylabel='FFT magnitude (arb.)',
                     title=f'data/{rid}: B=2–10 T, B-polynomial detrended')
    peaks, _ = find_peaks(spec[0])
    peaks = sorted([p for p in peaks if 2 < freq[p] < 60], key=lambda p: spec[0, p], reverse=True)[:5]
    print('  peaks 2–10 T:', ', '.join(f'{freq[p]:.1f} T' for p in peaks))
fig.tight_layout()
plt.show()
