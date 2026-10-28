from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft
file_path = Path.cwd() / 'data'

fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for i, col in ((6, 0), (7, 1)):
    r = open_run(Path(file_path) / str(i))
    print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / I)
    ax[0, col].plot(B, R, lw=.9)
    ax[0, col].set(title=f'data/{i}: raw |Rxx|', xlabel='B (T)', ylabel='Ω')
    ax[1, col].plot(B, r.col('k_2400_tg_curr')*1e12, label='TG')
    ax[1, col].plot(B, r.col('k_2400_bg_curr')*1e12, label='BG')
    ax[1, col].set(title=f'data/{i}: raw gate current', xlabel='B (T)', ylabel='pA')
    ax[1, col].legend()
    print(f'data/{i}: T {r.col("T_sample").min():.3f}–{r.col("T_sample").max():.3f} K; '
          f'I {I.min()*1e9:.2f}–{I.max()*1e9:.2f} nA; R {R.min():.1f}–{R.max():.1f} Ω')
fig.tight_layout(); plt.show()

fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
for i, a in ((6, ax[0]), (7, ax[1])):
    r = open_run(Path(file_path) / str(i)); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field'); I = r.col('sr0_X') / ch['sr0'].gain
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / I)
    for lo in (2, 3, 4):
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, 10), log=False)
        a.plot(f, sp[0] / max(sp[0]), label=f'{lo}–10 T')
        pk, _ = find_peaks(sp[0], prominence=max(sp[0])*.05)
        peaks = sorted((j for j in pk if 3 < f[j] < 100), key=lambda j: -sp[0,j])[:4]
        print(f'data/{i} FFT {lo}–10 T: ' + ', '.join(f'{f[j]:.1f} T' for j in peaks))
    a.set(xlim=(0, 100), xlabel='SdH frequency (T)', ylabel='normalized magnitude', title=f'data/{i} — window sensitivity')
    a.legend()
fig.tight_layout(); plt.show()
