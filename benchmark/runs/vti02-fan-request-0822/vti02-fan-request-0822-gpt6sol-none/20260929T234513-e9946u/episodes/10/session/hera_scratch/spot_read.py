import numpy as np
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 2, figsize=(11, 7))

for rid in (6, 7):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = (r.col('sr1_X') / ch['sr1'].gain) / I
    sens = r.meta['instruments']['sr1']['parameters']['sensitivity']['value'] if False else 50e-6
    print(f"run {rid}: rows={r.rows} B={B[0]:.3f}->{B[-1]:.3f}, R {np.min(R):.1f}/{np.median(R):.1f}/{np.max(R):.1f} ohm, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, max raw X {np.max(np.abs(r.col('sr1_X')))/sens:.2f} FS, T {np.median(r.col('T_sample')):.3f} K, leakage {np.max(np.abs(r.col('k_2400_tg_curr')))*1e12:.0f}/{np.max(np.abs(r.col('k_2400_bg_curr')))*1e12:.0f} pA")
    j=0 if rid==6 else 1
    ax[j,0].plot(B,R,'.-',ms=1,lw=.5);ax[j,0].set(xlabel='B (T)',ylabel='|Rxx| (ohm)',title=f'Run {rid} raw')
    ax[j,1].plot(1/B[B>0],R[B>0],'.-',ms=1,lw=.5);ax[j,1].set(xlim=(0,1),xlabel='1/B (1/T)',ylabel='|Rxx| (ohm)',title=f'Run {rid} raw vs 1/B')
    try:
        o = sdh_onset(R, B, b_lo=0.3, b_hi=10, r_full_scale=sens/(np.median(I)))
        print(o.summary())
    except Exception as e:
        print('onset error:', repr(e))
    for lo,hi in ((1,10),(2,10),(3,10),(4,10)):
        try:
            f,s=sdh_fft(R[:,None],B,b_range=(lo,hi),nfft=4096,bg_degree=5,log=False)
            y=s[0]; pk,_=find_peaks(y)
            pk=[p for p in pk if 2<f[p]<100]
            pk=sorted(pk,key=lambda p:-y[p])[:8]
            print(f"FFT {lo}-{hi}T: "+', '.join(f'{f[p]:.1f}T({y[p]/np.median(y[(f>2)&(f<100)]):.1f}x)' for p in pk))
        except Exception as e: print('fft error', repr(e))
fig.tight_layout();fig.savefig('hera_scratch/spot_raw.png',dpi=150)
