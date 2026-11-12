from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for row, rid in enumerate((6, 7)):
    run = open_run(Path('data') / str(rid))
    channels = {c.cid: c for c in resolve_channels(run.meta)}
    b = run.col('magnet_field')
    i = run.col('sr0_X') / channels['sr0'].gain
    r = np.abs((run.col('sr1_X') / channels['sr1'].gain) / i)
    print(f'run {rid}: {len(b)} pts B {b[0]:.3f}->{b[-1]:.3f} T; R {r.min():.1f}..{r.max():.1f} Ohm; I {i.min()*1e9:.3f}..{i.max()*1e9:.3f} nA; T {run.col("T_sample").min():.3f}..{run.col("T_sample").max():.3f} K; leakage median TG/BG {np.median(run.col("k_2400_tg_curr"))*1e12:.1f}/{np.median(run.col("k_2400_bg_curr"))*1e12:.1f} pA')
    axes[row, 0].plot(b, r, lw=0.9)
    axes[row, 0].set(xlabel='B (T)', ylabel='|Rxx| (Ohm)', title=f'run {rid} raw')
    for br in ((1.5, 6), (2.0, 10)):
        try:
            f, spec = sdh_fft(r[:, None], b, b_range=br, nfft=2048, bg_degree=4)
            s = spec[0]
            p, _ = find_peaks(s)
            p = sorted((k for k in p if 2 <= f[k] <= 80), key=lambda k: s[k], reverse=True)[:8]
            print(f'run {rid} FFT B={br}: ' + ', '.join(f'{f[k]:.2f} T ({s[k]:.2g})' for k in p))
            axes[row, 1].plot(f, s/s.max(), label=f'{br[0]}–{br[1]} T')
        except Exception as e:
            print(f'run {rid} FFT {br}: {e}')
    try:
        o = sdh_onset(r, b, b_lo=0.3, b_hi=10, r_full_scale=5000)
        print(f'run {rid} onset:\n{o.summary()}')
    except Exception as e:
        print(f'run {rid} onset failed: {e}')
    axes[row, 1].set(xlim=(0, 80), xlabel='frequency (T)', ylabel='normalized FFT', title=f'run {rid} SdH spectrum')
    axes[row, 1].legend()
fig.tight_layout()
fig.savefig('hera_scratch/spot_analysis.png', dpi=150)
