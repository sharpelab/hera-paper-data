"""Read session SdH spot checks before choosing a Landau fan."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
for col, rid in enumerate((6, 7)):
    run = open_run(f'data/{rid}')
    ch = {c.cid: c for c in resolve_channels(run.meta)}
    B = run.col('magnet_field')
    I = run.col('sr0_X') / ch['sr0'].gain
    X = run.col('sr1_X') / ch['sr1'].gain
    R = abs(X / I)
    t = run.col('T_sample')
    itg, ibg = run.col('k_2400_tg_curr'), run.col('k_2400_bg_curr')
    print(f'run {rid}: {len(B)} pts, B {B[0]:.3f}->{B[-1]:.3f} T, '
          f'R {R.min():.1f}..{R.max():.1f} ohm, |X| max {abs(X).max()*1e6:.2f} uV '
          f'({abs(X).max()/50e-6:.1%} FS), I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, '
          f'T {t.min():.3f}..{t.max():.3f} K, '
          f'TG I {itg.min()*1e12:.0f}..{itg.max()*1e12:.0f} pA, '
          f'BG I {ibg.min()*1e12:.0f}..{ibg.max()*1e12:.0f} pA')
    p = np.argsort(B)
    B, R = B[p], R[p]
    axes[0, col].plot(B, R, lw=.7)
    axes[0, col].set(xlabel='B (T)', ylabel='|Rxx| (ohm)', title=f'run {rid} raw')
    for lo in (1.5, 2, 3):
        try:
            onset = sdh_onset(R, B, b_lo=lo, b_hi=9.8, r_full_scale=5000)
            print(f'  onset b_lo={lo}: {onset.summary()}')
            break
        except Exception as ex:
            print(f'  onset b_lo={lo}: {type(ex).__name__}: {ex}')
    for br in ((2, 9.8), (3, 9.8), (4, 9.8)):
        try:
            f, sp = sdh_fft(R[:, None], B, b_range=br, nfft=2048, bg_degree=4)
            spec = sp[0]
            pk, prop = find_peaks(spec, prominence=spec.max()*.06)
            pk = sorted(pk, key=lambda i: -spec[i])
            tones = [(round(f[i], 2), round(spec[i]/spec.max(), 2)) for i in pk if 2 < f[i] < 80][:8]
            print(f'  FFT {br}: tones F (T), rel={tones}; delta F={1/(1/br[0]-1/br[1]):.2f} T')
            axes[1, col].plot(f, spec, label=f'{br[0]}–{br[1]} T')
        except Exception as ex:
            print(f'  FFT {br}: {type(ex).__name__}: {ex}')
    axes[1, col].set(xlim=(0, 70), xlabel='F (T)', ylabel='FFT amplitude', title=f'run {rid} SdH FFT')
    axes[1, col].legend(fontsize=8)
fig.tight_layout()
fig.savefig('hera_scratch/spot_read.png', dpi=130)
