"""Electron fan (run 6) analysis: per-column SdH FFT -> F(n) branches -> the
partition-robustness test f_ML(n)+f_BL(n)=F_L(n), plus harmonic/intermod screen.
Run when the fan completes: menv python fan_analyze.py [onset]"""
import sys, json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency
from scipy.signal import find_peaks

ONSET = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
import os
m = json.load(open('data/6/metadata.json')); ci = {c: i for i, c in enumerate(m['columns'])}
_f = 'data/6/data.tsv.gz' if os.path.exists('data/6/data.tsv.gz') else 'data/6/data.tsv'
raw = np.loadtxt(_f); Ib = m['measurement_config']['bias_voltage'] / m['measurement_config']['bias_resistor']
ns_cm = np.linspace(2e12, 10e12, 33); NN = len(ns_cm)
NB = len(raw) // NN                       # complete B-rows (robust to a partial last row)
Bcol = raw[:NB*NN, ci['magnet_mag']]; Bvals = Bcol.reshape(NB, NN)[:, 0]
print(f'fan: {len(raw)} pts -> {NB} complete B-rows x {NN} n-cols ; B {Bvals.min():.2f}..{Bvals.max():.2f}T')
# reshape: rows ordered slow(B)-major, fast(n)-minor
def grid(col):
    g = (raw[:NB*NN, ci[col]] / Ib)
    return g.reshape(NB, NN)   # (B, n)
R1 = grid('sr1_X'); R2 = grid('sr2_X')
FLn = luttinger_frequency(ns_cm * 1e4)   # F_L(n), Tesla

fig, axes = plt.subplots(2, 3, figsize=(17, 9))
for row, (nm, Rg) in enumerate([('sr1 T3-T4', R1), ('sr2 B4-B5', R2)]):
    # raw 2D Rxx(n,B)
    ax = axes[row, 0]
    im = ax.pcolormesh(ns_cm/1e12, Bvals, Rg, shading='auto', cmap='viridis')
    ax.set_xlabel('n (1e12 cm^-2)'); ax.set_ylabel('B (T)'); ax.set_title(f'{nm} Rxx(n,B)'); plt.colorbar(im, ax=ax)
    # per-column FFT (sdh_fft does all columns at once)
    f, spec = sdh_fft(Rg, Bvals, b_range=(ONSET, 8.0), detrend=5, window='hann', nfft=4096, log=False)
    fb = (f > 4) & (f < 120); fbf = f[fb]
    ax = axes[row, 1]
    Snorm = spec[:, fb] / spec[:, fb].max(axis=1, keepdims=True)   # normalize per column
    im = ax.pcolormesh(ns_cm/1e12, fbf, Snorm.T, shading='auto', cmap='magma')
    ax.plot(ns_cm/1e12, FLn, 'c--', lw=1.5, label='F_L(n)')
    ax.plot(ns_cm/1e12, FLn/2, 'c:', lw=1, label='F_L/2')
    ax.set_xlabel('n (1e12 cm^-2)'); ax.set_ylabel('F (T)'); ax.set_ylim(0, 115)
    ax.set_title(f'{nm} per-column FFT waterfall'); ax.legend(fontsize=7); plt.colorbar(im, ax=ax)
    # extract two branches per column: strongest peak in low band (<F_L/2) and high band
    fML, fBL = np.full(NN, np.nan), np.full(NN, np.nan)
    for j in range(NN):
        S = spec[j, fb]
        lo = fbf < FLn[j]*0.55; hi = (fbf >= FLn[j]*0.55) & (fbf < FLn[j]*1.25)
        if lo.sum() and S[lo].max() > 0.15*S.max():
            fML[j] = fbf[lo][np.argmax(S[lo])]
        if hi.sum() and S[hi].max() > 0.15*S.max():
            fBL[j] = fbf[hi][np.argmax(S[hi])]
    ax = axes[row, 2]
    ax.plot(ns_cm/1e12, fML, 'o-', ms=3, label='f_ML (low)')
    ax.plot(ns_cm/1e12, fBL, 's-', ms=3, label='f_BL (high)')
    ax.plot(ns_cm/1e12, fML+fBL, '^-', ms=3, label='f_ML+f_BL')
    ax.plot(ns_cm/1e12, FLn, 'k--', lw=1.5, label='F_L(n)')
    ax.set_xlabel('n (1e12 cm^-2)'); ax.set_ylabel('F (T)'); ax.set_title(f'{nm} partition test'); ax.legend(fontsize=7); ax.grid(alpha=.3)
    # numeric partition check (mid-high n where tones resolve)
    ok = np.isfinite(fML) & np.isfinite(fBL) & (ns_cm > 4e12)
    if ok.sum():
        resid = (fML[ok]+fBL[ok]-FLn[ok]) / FLn[ok]
        print(f'[{nm}] partition f_ML+f_BL vs F_L (n>4e12, {ok.sum()} cols): '
              f'mean resid {resid.mean()*100:+.1f}%, rms {resid.std()*100:.1f}% '
              f'| f_ML {np.nanmin(fML[ok]):.0f}-{np.nanmax(fML[ok]):.0f}T, f_BL {np.nanmin(fBL[ok]):.0f}-{np.nanmax(fBL[ok]):.0f}T')
plt.tight_layout(); plt.savefig('hera_scratch/fan_analyze.png', dpi=95)
print('saved hera_scratch/fan_analyze.png')
print('READ: two branches tracking with n, summing to F_L(n) across density = ABA')
print('(partition robust, model-independent). A single branch on F_L would be ABC.')
