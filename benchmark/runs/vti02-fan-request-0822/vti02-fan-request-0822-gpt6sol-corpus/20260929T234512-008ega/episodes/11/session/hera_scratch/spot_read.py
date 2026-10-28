from hera.analysis import open_run, sdh_onset, sdh_fft
import numpy as np
from scipy.signal import find_peaks

for i, sens, n in [(6, 50e-6, 3.2), (7, 50e-6, -1.2)]:
    run = open_run(f"data/{i}")
    B = run.col("magnet_field")
    R = run.col("sr1_X") / 1e-8
    I_tg, I_bg = run.col("k_2400_tg_curr"), run.col("k_2400_bg_curr")
    print(f"run {i}: B {B.min():.3f}-{B.max():.3f} T, R {R.min():.1f}-{R.max():.1f} ohm, "+
          f"max |I_tg,bg| {np.max(abs(I_tg))*1e12:.0f},{np.max(abs(I_bg))*1e12:.0f} pA, "+
          f"T {run.col('T_sample').min():.3f}-{run.col('T_sample').max():.3f} K")
    try:
        on = sdh_onset(R, B, r_full_scale=sens/1e-8)
        print(on.summary())
        lo = on.onset_b
    except Exception as e:
        print('onset error:', type(e).__name__, str(e))
        lo = 2.0
    for cutoff in [lo, max(lo, 2.5), max(lo, 3.5)]:
        if cutoff >= B.max()-0.5: continue
        f, spec = sdh_fft(R[:,None], B, b_range=(cutoff, B.max()), log=False)
        y = spec[0]
        peaks,_ = find_peaks(y, prominence=np.max(y)*0.02)
        peaks = [p for p in peaks if 2 < f[p] < 60]
        peaks = sorted(peaks,key=lambda p:y[p],reverse=True)[:8]
        print(' fft',round(cutoff,2), 'dF',round(1/(1/cutoff-1/B.max()),2),
              [(round(float(f[p]),2),round(float(y[p]/np.max(y)),2)) for p in peaks])
