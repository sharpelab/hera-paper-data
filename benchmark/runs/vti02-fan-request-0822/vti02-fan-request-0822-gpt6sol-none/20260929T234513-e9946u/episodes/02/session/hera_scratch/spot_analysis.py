from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset

fig, axes = plt.subplots(2, 2, figsize=(12, 7))
for i, ax in zip((6, 7), axes):
    r = open_run(Path('data') / str(i))
    print(f'\nRUN {i}\n{summarize_run(r)}')
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / I)
    T = r.col('T_sample')
    tg = r.col('k_2400_tg_curr'); bg = r.col('k_2400_bg_curr')
    print(f'B {B.min():.3f}..{B.max():.3f}, T {T.min():.3f}..{T.max():.3f}, R {R.min():.1f}..{R.max():.1f}, I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA')
    print(f'gate I TG {tg.min()*1e12:.1f}..{tg.max()*1e12:.1f} pA, BG {bg.min()*1e12:.1f}..{bg.max()*1e12:.1f} pA')
    for br in ((2, 10), (3, 10), (4, 10)):
        try:
            f, sp = sdh_fft(R[:,None], B, b_range=br, log=False)
            from scipy.signal import find_peaks
            pk, _ = find_peaks(sp[0], prominence=np.max(sp[0])*0.05)
            peaks = sorted(pk[f[pk]>3], key=lambda j: -sp[0,j])[:6]
            print(f'FFT {br}: '+', '.join(f'{f[j]:.1f}T ({sp[0,j]:.2g})' for j in peaks))
        except Exception as exc: print('FFT ERROR', br, exc)
    try:
        print('ONSET:',sdh_onset(R,B,b_hi=10,r_full_scale=5000).summary())
    except Exception as exc: print('ONSET ERROR',type(exc).__name__,exc)
    ax[0].plot(B,R,'.-',ms=1); ax[0].set_title(f'run {i} raw |Rxx|'); ax[0].set_xlabel('B (T)'); ax[0].set_ylabel('Ohm')
    ax[1].plot(B,tg*1e12,label='TG'); ax[1].plot(B,bg*1e12,label='BG'); ax[1].set_title(f'run {i} gate current'); ax[1].set_xlabel('B (T)'); ax[1].set_ylabel('pA'); ax[1].legend()
fig.tight_layout(); fig.savefig('hera_scratch/spot_raw.png',dpi=130)
