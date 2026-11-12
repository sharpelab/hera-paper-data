"""Electron fan (run 6) FINAL analysis: per-column SdH FFT -> f_ML(n), f_BL(n) ->
partition-robustness test f_ML+f_BL vs F_L(n), with tightened bands + harmonic screen.
The SdH-based lever-arm lambda = <(f_ML+f_BL)/F_L_gate> is the n-scale upgrade."""
import json, numpy as np, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from hera.analysis import sdh_fft, luttinger_frequency

m = json.load(open('data/6/metadata.json')); ci = {c: i for i, c in enumerate(m['columns'])}
raw = np.loadtxt('data/6/data.tsv.gz'); Ib = m['measurement_config']['bias_voltage'] / m['measurement_config']['bias_resistor']
ns_cm = np.linspace(2e12, 10e12, 33); NN = len(ns_cm); NB = len(raw)//NN
Bvals = raw[:NB*NN, ci['magnet_mag']].reshape(NB, NN)[:, 0]
FLg = luttinger_frequency(ns_cm*1e4)               # F_L from gate n
def grid(c): return (raw[:NB*NN, ci[c]]/Ib).reshape(NB, NN)
R = {'sr1 T3-T4': grid('sr1_X'), 'sr2 B4-B5': grid('sr2_X')}
OVL = 430.0   # overload rail (ohm) -> mark clipped columns
print(f'fan complete: {NB} B-rows x {NN} n-cols, B {Bvals.min():.2f}..{Bvals.max():.2f}T')

def extract(Rg, ONSET=2.0):
    f, spec = sdh_fft(Rg, Bvals, b_range=(ONSET, 8.0), detrend=5, window='hann', nfft=4096, log=False)
    fML = np.full(NN, np.nan); fBL = np.full(NN, np.nan); clip = np.zeros(NN, bool)
    for j in range(NN):
        clip[j] = (Rg[Bvals > 4, j] > OVL).mean() > 0.1     # >10% of high-B pts railed
        S = spec[j]; FL = FLg[j]
        lo = (f > 0.12*FL) & (f < 0.45*FL); hi = (f > 0.55*FL) & (f < 0.92*FL)
        if lo.any() and S[lo].max() > 0.12*S.max(): fML[j] = f[lo][np.argmax(S[lo])]
        if hi.any() and S[hi].max() > 0.12*S.max(): fBL[j] = f[hi][np.argmax(S[hi])]
    return f, spec, fML, fBL, clip

fig, axes = plt.subplots(2, 3, figsize=(17, 9))
summary = {}
for row, (nm, Rg) in enumerate(R.items()):
    f, spec, fML, fBL, clip = extract(Rg)
    fb = (f > 4) & (f < 120)
    # waterfall
    ax = axes[row, 1]
    Sn = spec[:, fb]/spec[:, fb].max(axis=1, keepdims=True)
    im = ax.pcolormesh(ns_cm/1e12, f[fb], Sn.T, shading='auto', cmap='magma'); plt.colorbar(im, ax=ax)
    ax.plot(ns_cm/1e12, FLg, 'c--', lw=1.3, label='F_L(n) gate'); ax.plot(ns_cm/1e12, FLg*1.06, 'c:', lw=1, label='x1.06 (Hall)')
    ax.set_xlabel('n (1e12)'); ax.set_ylabel('F (T)'); ax.set_ylim(0, 115); ax.set_title(f'{nm} FFT waterfall'); ax.legend(fontsize=6)
    # raw map
    ax = axes[row, 0]; im = ax.pcolormesh(ns_cm/1e12, Bvals, np.clip(Rg, 0, 450), shading='auto', cmap='viridis')
    ax.set_xlabel('n (1e12)'); ax.set_ylabel('B (T)'); ax.set_title(f'{nm} Rxx(n,B)'); plt.colorbar(im, ax=ax)
    # partition
    ax = axes[row, 2]
    good = np.isfinite(fML) & np.isfinite(fBL) & ~clip
    ax.plot(ns_cm/1e12, fML, 'o', ms=3, label='f_ML'); ax.plot(ns_cm/1e12, fBL, 's', ms=3, label='f_BL')
    ax.plot(ns_cm/1e12, fML+fBL, '^', ms=3, label='f_ML+f_BL'); ax.plot(ns_cm/1e12, FLg, 'k--', label='F_L gate')
    ax.plot(ns_cm[clip]/1e12, (fML+fBL)[clip], 'rx', ms=7, label='clipped (excl)')
    ax.set_xlabel('n (1e12)'); ax.set_ylabel('F (T)'); ax.set_title(f'{nm} partition'); ax.legend(fontsize=6); ax.grid(alpha=.3)
    if good.sum() >= 4:
        lam = ((fML+fBL)/FLg)[good]
        rb = (fBL/FLg)[good]; rm = (fML/FLg)[good]
        print(f'[{nm}] good cols {good.sum()}/{NN} (clipped {clip.sum()}): '
              f'lambda=(f_ML+f_BL)/F_L_gate = {lam.mean():.3f}+/-{lam.std():.3f} '
              f'| f_BL/F_L {rb.mean():.2f}, f_ML/F_L {rm.mean():.2f} '
              f'| f_ML {np.nanmin(fML[good]):.0f}-{np.nanmax(fML[good]):.0f}T f_BL {np.nanmin(fBL[good]):.0f}-{np.nanmax(fBL[good]):.0f}T')
        summary[nm] = dict(lam=lam.mean(), lamstd=lam.std(), nbl=rb.mean(), nml=rm.mean(), ngood=int(good.sum()))
plt.tight_layout(); plt.savefig('hera_scratch/fan_final.png', dpi=95)
print('saved hera_scratch/fan_final.png')
print('PARTITION: lambda~const across n (low std) AND ~1.0-1.1 => f_ML+f_BL=F_L holds => ABA.')
print('A single tone at F_L (f_BL/F_L~1, no f_ML) would be ABC.')
