from scipy.signal import find_peaks
from hera.analysis import sdh_fft
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
for j, rid in enumerate((6, 7)):
    d = spot[rid]; B, R = d['B'], d['R']
    p = np.argsort(B); B, R = B[p], R[p]
    for br in ((2, 9.8), (3, 9.8), (4, 9.8)):
        f, sp = sdh_fft(R[:, None], B, b_range=br, nfft=2048, bg_degree=4)
        y = sp[0]; pk, _ = find_peaks(y, prominence=y.max()*.06)
        peaks = [(float(f[k]), float(y[k]/y.max())) for k in pk if 2 < f[k] < 80]
        peaks = sorted(peaks, key=lambda pair: -pair[1])[:5]
        print(f'data/{rid}, B={br[0]}..{br[1]} T, ΔF≈{1/(1/br[0]-1/br[1]):.1f} T: '
              + ', '.join(f'{v:.1f} T ({a:.2f} rel.)' for v, a in peaks))
        ax[j].plot(f, y, label=f'{br[0]}–{br[1]} T')
    ax[j].set(xlim=(0, 70), xlabel='SdH frequency (T)', ylabel='FFT amplitude', title=f'data/{rid}')
    ax[j].legend(fontsize=8)
fig.tight_layout(); plt.show()
