import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft, luttinger_frequency

r = open_run('data/4')
m = json.load(open('data/4/metadata.json'))
Ib = m['measurement_config']['bias_voltage'] / m['measurement_config']['bias_resistor']
B = r.col('magnet_mag'); o = np.argsort(B); B = B[o]
R = {'sr1 T3-T4': (r.col('sr1_X') / Ib)[o], 'sr2 B4-B5': (r.col('sr2_X') / Ib)[o]}
bmax = {'sr1 T3-T4': 5.3, 'sr2 B4-B5': 8.0}      # sr1 overloads >5.44T
FL = luttinger_frequency(8e16)                    # n=+8e12 cm^-2
ONSET = 2.0
print(f'n=+8e12, F_L={FL:.1f} T, F_L/2={FL/2:.1f} T')

fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for i, (nm, Rc) in enumerate(R.items()):
    bm = bmax[nm]; sel = B <= bm
    Bc, Rc2 = B[sel], Rc[sel]
    p = np.polyfit(Bc, Rc2, 5); dR = Rc2 - np.polyval(p, Bc)
    ax[i, 0].plot(B, Rc, lw=.7); ax[i, 0].axvline(bm, color='r', ls=':', label=f'sr1 ovld {bm}T' if i == 0 else f'use<{bm}T')
    ax[i, 0].set_title(f'{nm} Rxx(B)'); ax[i, 0].set_ylabel('Rxx (ohm)'); ax[i, 0].grid(alpha=.3); ax[i, 0].legend(fontsize=7)
    ax[i, 1].plot(Bc, dR, lw=.8); ax[i, 1].axvline(ONSET, color='g', ls='--', label=f'onset {ONSET}T')
    ax[i, 1].set_title(f'{nm} dRxx (bkg removed)'); ax[i, 1].grid(alpha=.3); ax[i, 1].legend(fontsize=7)
    # FFT + stability sweep over [onset, bm]
    for det, win, lab in [(5, 'hann', 'd5 hann'), (3, 'hann', 'd3 hann'), (5, 'blackman', 'd5 black')]:
        f, Sg = sdh_fft(Rc.reshape(-1, 1), B, b_range=(ONSET, bm), detrend=det, window=win, nfft=4096, log=False)
        S = Sg[0]; ax[i, 2].plot(f, S / np.nanmax(S), lw=.9, label=lab)
    ax[i, 2].axvline(FL, color='k', ls='--', lw=1, label=f'F_L={FL:.0f}')
    ax[i, 2].axvline(FL/2, color='gray', ls=':', label='F_L/2')
    ax[i, 2].set_xlim(0, FL*1.5); ax[i, 2].set_title(f'{nm} FFT in 1/B [{ONSET}-{bm}T]'); ax[i, 2].set_xlabel('F (T)')
    ax[i, 2].legend(fontsize=7); ax[i, 2].grid(alpha=.3)
    # peaks (d5 hann)
    f, Sg = sdh_fft(Rc.reshape(-1, 1), B, b_range=(ONSET, bm), detrend=5, window='hann', nfft=4096, log=False)
    S = Sg[0]; band = (f > 4) & (f < FL*1.4); fb, Sb = f[band], S[band]
    pk, _ = find_peaks(Sb, height=0.12*Sb.max(), distance=8)
    pk = pk[np.argsort(Sb[pk])[::-1]][:6]
    pks = sorted(fb[k] for k in pk)
    print(f'[{nm}] B[{ONSET},{bm}] dF={1/(1/ONSET-1/bm):.1f}T  peaks(T): ' +
          ', '.join(f'{fb[k]:.1f}({Sb[k]/Sb.max():.2f})' for k in pk[np.argsort(fb[pk])]))
    print(f'    sum-check: pairs summing to F_L={FL:.0f}? ' +
          ', '.join(f'{a:.0f}+{b:.0f}={a+b:.0f}' for ii,a in enumerate(pks) for b in pks[ii+1:] if abs(a+b-FL)<8))
plt.tight_layout(); plt.savefig('hera_scratch/ana_spotA.png', dpi=100)
print('saved hera_scratch/ana_spotA.png')
