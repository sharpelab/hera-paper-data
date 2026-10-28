from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset
for rid in [6, 7]:
    r = open_run(Path('/home/hera/measurements/zack/20260822-vti-02/data') / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = r.col('sr1_X') / ch['sr1'].gain / I
    print(summarize_run(r))
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.5))
    ax[0].plot(B, r.col('sr1_X')*1e6); ax[0].set_ylabel('raw sr1 X (uV)')
    ax[1].plot(B, I*1e9); ax[1].set_ylabel('measured drain current (nA)')
    for c in ['k_2400_tg_curr', 'k_2400_bg_curr']:
        ax[2].plot(B, r.col(c)*1e12, label=c)
    ax[2].set_ylabel('gate current (pA)'); ax[2].legend(fontsize=7)
    for a in ax: a.set_xlabel('B (T)')
    fig.suptitle(f'Run {rid}: raw data'); fig.tight_layout(); plt.show()
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.5))
    ax[0].plot(B, R); ax[0].set_xlabel('B (T)'); ax[0].set_ylabel('signed Rxx B_1-B_2 (Ohm)')
    f, spec = sdh_fft(R[:, None], B, b_range=(1, 10), log=False)
    ax[1].plot(f, spec[0]); ax[1].set_xlim(0, 45); ax[1].set_xlabel('frequency (T)'); ax[1].set_ylabel('FFT amplitude (arb.)')
    fig.suptitle(f'Run {rid}: analysis, FFT 1-10 T, resolution ~1.1 T'); fig.tight_layout(); plt.show()
    print(f'Rxx {R.min():.2f}..{R.max():.2f} Ohm; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; T {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K')
    try:
        print(sdh_onset(R, B, r_full_scale=5000).summary())
    except ValueError as exc:
        print('Onset unresolved:', exc)
    print('Interpretation: oscillations justify the fan; spectral tones are not independent band counts. Onset flags and harmonic ambiguities are retained.')
