import numpy as np
from hera.analysis import open_run, summarize_run, sdh_fft, sdh_onset

for rid in (6, 7):
    run = open_run(f"data/{rid}")
    print(summarize_run(run))
    B = run.col('magnet_field')
    I = run.col('sr0_X') / run.meta['measurement_config']['sr0_gain']
    R = (run.col('sr1_X') / 1.0) / I
    T = run.col('T_sample')
    for name, arr in [('B', B), ('T', T), ('I nA', I*1e9), ('R ohm', R),
                      ('TG pA', run.col('k_2400_tg_curr')*1e12),
                      ('BG pA', run.col('k_2400_bg_curr')*1e12)]:
        print(rid, name, 'min med max', np.min(arr), np.median(arr), np.max(arr))
    try:
        on = sdh_onset(R, B, b_lo=1.0, b_hi=9.8, r_full_scale=5000)
        print(on.summary())
    except Exception as exc:
        print('onset error', type(exc).__name__, str(exc))
    for b_low in [1.5, 2.0, 3.0, 4.0]:
        for deg in [3, 5]:
            try:
                f, spec = sdh_fft(R[:,None], B, b_range=(b_low, 9.8),
                                  nfft=2048, bg_degree=deg, log=False)
                sp=spec[0]
                from scipy.signal import find_peaks
                peaks,_=find_peaks(sp)
                peaks=sorted((p for p in peaks if 2<f[p]<80),key=lambda p:sp[p],reverse=True)[:8]
                print(rid, 'FFT', b_low, deg, [(round(f[p],2), round(sp[p],2)) for p in peaks])
            except Exception as exc:
                print('FFT error', b_low,deg,type(exc).__name__,str(exc))
