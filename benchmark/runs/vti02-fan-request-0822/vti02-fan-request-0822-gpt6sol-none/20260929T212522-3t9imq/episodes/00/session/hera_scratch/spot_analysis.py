from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_fft, sdh_onset

root = Path(__file__).resolve().parents[1]
fig, ax = plt.subplots(2, 2, figsize=(12, 8))
for row, rid in enumerate((6, 7)):
    run = open_run(root / 'data' / str(rid))
    print(summarize_run(run))
    cc = resolve_channels(run.meta)
    ch = {c.cid: c for c in cc}
    I = run.col(ch['sr0'].col) / ch['sr0'].gain
    R = np.abs((run.col(ch['sr1'].col) / ch['sr1'].gain) / I)
    B = run.col('magnet_field')
    order = np.argsort(B)
    B, R, I = B[order], R[order], I[order]
    print(f'run {rid}: B {B.min():.3f}..{B.max():.3f}, R {R.min():.1f}..{R.max():.1f} ohm, I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA, |I_tg| max {np.max(np.abs(run.col("k_2400_tg_curr")))*1e12:.1f} pA, |I_bg| max {np.max(np.abs(run.col("k_2400_bg_curr")))*1e12:.1f} pA')
    for lo in ((1.5, 3.0) if rid == 6 else (1.5, 3.0)):
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(lo, 9.5), nfft=1024, bg_degree=5, log=False)
            yy = spec[0]
            pk, _ = find_peaks(yy)
            pk = sorted((p for p in pk if 2 < f[p] < 80), key=lambda p: yy[p], reverse=True)[:8]
            print(f'FFT {lo}..9.5 T peaks: ' + ', '.join(f'{f[p]:.2f}T({yy[p]:.1f})' for p in pk))
        except Exception as e: print('FFT error', type(e).__name__, e)
    try:
        onset = sdh_onset(R, B, b_hi=9.5, b_lo=1.0, r_full_scale=5000)
        print(onset.summary())
    except Exception as e: print('onset error', type(e).__name__, e)
    ax[row,0].plot(B,R,lw=.6); ax[row,0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title=f'run {rid} raw')
    ax[row,1].plot(f,yy,lw=.7); ax[row,1].set(xlim=(0,70),xlabel='SdH frequency (T)',ylabel='FFT magnitude (ohm)',title=f'run {rid} 3..9.5 T')
fig.tight_layout(); fig.savefig(root / 'hera_scratch' / 'spots_6_7.png',dpi=150)
