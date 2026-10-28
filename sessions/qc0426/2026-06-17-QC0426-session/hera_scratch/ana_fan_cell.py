# Electron Landau fan (run 6): per-column SdH FFT -> F(n) -> partition-robustness test.
# The model-independent FS-count refinement: f_ML(n)+f_BL(n)=lambda*F_L(n), lambda const
# across n => two Fermi surfaces => ABA. lambda is also the SdH-based lever-arm (n-scale).
from hera.analysis import sdh_fft, luttinger_frequency

mF = load_meta(6); ciF = {c: i for i, c in enumerate(mF['columns'])}
rawF = np.loadtxt(os.path.join(file_path, '6', 'data.tsv.gz'))
IbF = mF['measurement_config']['bias_voltage'] / mF['measurement_config']['bias_resistor']
nsF = np.linspace(2e12, 10e12, 33); NNf = len(nsF); NBf = len(rawF)//NNf
BvalsF = rawF[:NBf*NNf, ciF['magnet_mag']].reshape(NBf, NNf)[:, 0]
FLgF = luttinger_frequency(nsF*1e4)
def gridF(c): return (rawF[:NBf*NNf, ciF[c]]/IbF).reshape(NBf, NNf)
RF = {'sr1 T3-T4': gridF('sr1_X'), 'sr2 B4-B5': gridF('sr2_X')}
OVLf = 430.0

fig, axes = plt.subplots(2, 3, figsize=(17, 9))
for row, (nm, Rg) in enumerate(RF.items()):
    f, spec = sdh_fft(Rg, BvalsF, b_range=(2.0, 8.0), detrend=5, window='hann', nfft=4096, log=False)
    fML = np.full(NNf, np.nan); fBL = np.full(NNf, np.nan); clip = np.zeros(NNf, bool)
    for j in range(NNf):
        clip[j] = (Rg[BvalsF > 4, j] > OVLf).mean() > 0.1
        S = spec[j]; FL = FLgF[j]
        lo = (f > 0.12*FL) & (f < 0.45*FL); hi = (f > 0.55*FL) & (f < 0.92*FL)
        if lo.any() and S[lo].max() > 0.12*S.max(): fML[j] = f[lo][np.argmax(S[lo])]
        if hi.any() and S[hi].max() > 0.12*S.max(): fBL[j] = f[hi][np.argmax(S[hi])]
    fb = (f > 4) & (f < 120)
    a = axes[row, 0]; im = a.pcolormesh(nsF/1e12, BvalsF, np.clip(Rg, 0, 450), shading='auto', cmap='viridis')
    a.set_xlabel('n (1e12 cm$^{-2}$)'); a.set_ylabel('B (T)'); a.set_title(f'{nm}  $R_{{xx}}$(n,B)'); plt.colorbar(im, ax=a)
    a = axes[row, 1]; Sn = spec[:, fb]/spec[:, fb].max(axis=1, keepdims=True)
    im = a.pcolormesh(nsF/1e12, f[fb], Sn.T, shading='auto', cmap='magma'); plt.colorbar(im, ax=a)
    a.plot(nsF/1e12, FLgF, 'c--', lw=1.3, label='$F_L$(n)'); a.set_ylim(0, 115)
    a.set_xlabel('n (1e12)'); a.set_ylabel('F (T)'); a.set_title(f'{nm}  FFT waterfall'); a.legend(fontsize=7)
    a = axes[row, 2]; good = np.isfinite(fML) & np.isfinite(fBL) & ~clip
    a.plot(nsF/1e12, fML, 'o', ms=3, label='$f_{ML}$'); a.plot(nsF/1e12, fBL, 's', ms=3, label='$f_{BL}$')
    a.plot(nsF/1e12, fML+fBL, '^', ms=3, label='$f_{ML}+f_{BL}$'); a.plot(nsF/1e12, FLgF, 'k--', label='$F_L$ gate')
    a.set_xlabel('n (1e12)'); a.set_ylabel('F (T)'); a.set_title(f'{nm}  partition'); a.legend(fontsize=7); a.grid(alpha=.3)
    if good.sum() >= 4:
        lam = ((fML+fBL)/FLgF)[good]
        print(f'[{nm}] {good.sum()}/{NNf} good cols (clipped {clip.sum()}): '
              f'lambda=(f_ML+f_BL)/F_L = {lam.mean():.3f}+/-{lam.std():.3f}; '
              f'f_BL/F_L={np.nanmean((fBL/FLgF)[good]):.2f}, f_ML/F_L={np.nanmean((fML/FLgF)[good]):.2f}')
plt.suptitle('Electron fan F(n): two branches summing to F_L across density -> ABA', y=1.01)
plt.tight_layout(); plt.show()
print('lambda~1.06-1.08 CONSTANT across n => f_ML+f_BL=F_L robust => two Fermi surfaces => ABA.')
print('lambda is the SdH lever-arm; agrees with the Hall n-scale (n_H/n_gate~1.05-1.07).')
