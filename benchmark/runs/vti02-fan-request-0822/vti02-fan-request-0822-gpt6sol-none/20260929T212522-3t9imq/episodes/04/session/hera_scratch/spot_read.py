from pathlib import Path
import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, luttinger_frequency

for rid in (6, 7):
    r = open_run(Path('data') / str(rid))
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    volt = next(c for c in ch if c.cid == 'sr1')
    B = r.col('magnet_field')
    I = r.col_at(cur.idx) / cur.gain
    R = (r.col_at(volt.idx) / volt.gain) / I
    print(f'run {rid}: {r.rows} rows; B={B.min():.3f}..{B.max():.3f} T; T={np.median(r.col("T_sample")):.3f} K; I={np.median(I)*1e9:.3f} nA; |R| p5/median/p95/max={np.percentile(abs(R),[5,50,95,100])}; |I_tg| max={max(abs(r.col("k_2400_tg_curr")))*1e12:.1f} pA; |I_bg| max={max(abs(r.col("k_2400_bg_curr")))*1e12:.1f} pA')
    order = np.argsort(B)
    Bs, Rs = B[order], R[order]
    for lo in (1.5, 2, 3, 4):
        f, a = sdh_fft(Rs[:,None], Bs, b_range=(lo, 10), nfft=4096, bg_degree=5, log=False)
        a = a[0]
        ok = (f > 2) & (f < 55)
        p, _ = find_peaks(a[ok], prominence=max(a[ok])*0.08)
        ii = np.where(ok)[0][p]
        ii = ii[np.argsort(a[ii])[-6:]][::-1]
        print(f'  FFT B {lo}..10: ' + ', '.join(f'{f[j]:.1f} T ({a[j]/max(a[ok]):.2f})' for j in ii))
    try:
        onset = sdh_onset(Rs, Bs, b_hi=10, b_lo=1.0, r_full_scale=50e-6/1e-8)
        print(onset.summary())
    except Exception as e:
        print('onset error:', type(e).__name__, e)
