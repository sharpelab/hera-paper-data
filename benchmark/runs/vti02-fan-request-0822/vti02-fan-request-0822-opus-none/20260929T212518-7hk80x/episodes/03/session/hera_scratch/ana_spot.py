import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset, SdhOnsetError, GateCalibration, luttinger_frequency

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03)
def RB(rid):
    r = open_run(f'data/{rid}')
    B = r.col('magnet_field')
    I = r.col('sr0_X')/(-1e6)
    R = (r.col('sr1_X')/1.0)/I
    o = np.argsort(B)
    return r, B[o], R[o], r.col('T_sample')[o]

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n_nom) in enumerate([(6, 3.2), (7, -1.2)]):
    r, B, R, T = RB(rid)
    FL = abs(n_nom)*1e16*6.62607015e-34/(4*1.602176634e-19)
    print(f'=== run {rid} n={n_nom:+.2f}e12  F_Luttinger(4-fold, full n) = {FL:.2f} T   T_sample {T.mean():.3f} K')
    print(f'    R: min {R.min():.1f} max {R.max():.1f} at B=0..{B.max():.2f}; R(Bmin)={R[0]:.1f}')
    ax = axes[0, j]; ax.plot(B, R, lw=.7); ax.set_xlabel('B (T)'); ax.set_ylabel('Rxx (Ohm)'); ax.set_title(f'run {rid}  n={n_nom:+.1f}e12, D=0  raw')

    # background-subtracted vs 1/B
    m = B > 0.9
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax = axes[1, j]; ax.plot(1/B[m], R[m]-bg, lw=.8); ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dR (Ohm)')
    ax.set_title('poly5-detrended, B>0.9 T')

    # FFT over several windows
    ax = axes[2, j]
    for blo, bhi in [(1.5, 10.0), (3.0, 10.0), (5.0, 10.0)]:
        f, spec = sdh_fft(R[:, None], B, b_range=(blo, bhi), nfft=4096, bg_degree=5, log=False)
        s = spec[0]
        k = (f > 2) & (f < 3*max(FL, 5))
        ax.plot(f[k], s[k]/s[k].max(), lw=.9, label=f'{blo}-{bhi} T')
        pk = f[k][np.argsort(s[k])[-6:]][::-1]
        print(f'    FFT {blo}-{bhi} T: top peaks (T) {np.round(np.sort(pk)[::-1],2)}  df_res={1/(1/blo-1/bhi):.1f} T')
    ax.axvline(FL, color='k', ls='--', lw=.8); ax.set_xlabel('F (T)'); ax.set_ylabel('norm |FFT|'); ax.legend(fontsize=7)
    ax.set_title(f'F_L={FL:.1f} T (dashed)')
    try:
        o = sdh_onset(R, B, r_full_scale=50e-6/10e-9)
        print(o.summary())
    except SdhOnsetError as e:
        print(f'    sdh_onset FAILED: {e}')
plt.tight_layout(); plt.savefig('hera_scratch/spot_67.png', dpi=110)
print('saved hera_scratch/spot_67.png')
