"""Runs 6 & 7 — SdH spot checks at D=0 (electron n=+3.2e12, hole n=-1.2e12).
Raw traces, then SdH FFT in 1/B and per-tone onsets. Scratch pass."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset

fig, axes = plt.subplots(2, 3, figsize=(15, 8))

for row, (rid, lab) in enumerate([(6, 'run 6 — e side, n=+3.2e12'),
                                  (7, 'run 7 — h side, n=-1.2e12')]):
    r = open_run(f'data/{rid}')
    B = r.col('magnet_field')
    I = r.col('sr0_X') / (-1e6)          # transimpedance, A
    V = r.col('sr1_X')                    # Rxx voltage, gain 1
    R = V / I                             # signed 4-probe R

    # raw
    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel('B (T)'); ax.set_ylabel('Rxx (Ohm)'); ax.set_title(lab)

    # background-subtracted oscillation vs 1/B (B > 1.5 T)
    m = B > 1.5
    Bs, Rs = B[m], R[m]
    order = np.argsort(Bs)
    Bs, Rs = Bs[order], Rs[order]
    bg = np.polyval(np.polyfit(Bs, Rs, 5), Bs)
    ax = axes[row, 1]
    ax.plot(1/Bs, Rs - bg, lw=0.6)
    ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dRxx (Ohm)')
    ax.set_title('osc, B>1.5 T, poly5 removed')

    # FFT
    freqs, spec = sdh_fft(R[:, None], B, b_range=(1.5, 10), nfft=4096,
                          bg_degree=5, log=False)
    sp = spec[0]
    ax = axes[row, 2]
    ax.plot(freqs, sp, lw=0.8)
    ax.set_xlim(0, 120); ax.set_xlabel('F (T)'); ax.set_ylabel('|FFT|')
    ax.set_title('SdH FFT in 1/B (1.5-10 T)')

    # peaks
    from scipy.signal import find_peaks
    noise = np.median(sp[freqs > 150]) if (freqs > 150).any() else np.median(sp)
    pk, props = find_peaks(sp, height=6*noise, distance=8)
    print(f'--- run {rid}: R(0)={R[np.argmin(np.abs(B-B.min()))]:.1f}  R(max B)={R[np.argmax(B)]:.1f} Ohm')
    print(f'    T_sample mean {r.col("T_sample").mean():.3f} K; I at max B {I[np.argmax(B)]*1e9:.2f} nA')
    for p in pk:
        if freqs[p] > 2:
            print(f'    FFT peak: F = {freqs[p]:7.2f} T   amp {sp[p]:.3g}  ({sp[p]/noise:.0f}x noise)')
    for p in pk[:6]:
        if freqs[p] > 2:
            ax.axvline(freqs[p], color='r', ls=':', lw=0.6)

    # onsets
    try:
        o = sdh_onset(R, B, b_hi=10.0)
        print('    sdh_onset:', o)
    except Exception as e:
        print('    sdh_onset failed:', e)

    # leakage sanity
    for g in ('k_2400_tg_curr', 'k_2400_bg_curr'):
        c = r.col(g)
        print(f'    {g}: med {np.median(c)*1e12:.0f} pA  max|{np.max(np.abs(c))*1e12:.0f}| pA')

fig.tight_layout()
fig.savefig('hera_scratch/spots_67.png', dpi=110)
print('saved hera_scratch/spots_67.png')
