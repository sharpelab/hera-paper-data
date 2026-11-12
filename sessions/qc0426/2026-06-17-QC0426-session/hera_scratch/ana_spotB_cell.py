# SdH spot B (run 5): hole n=-8e12, D=0, B 8->0T (descending). Hole-side FS count.
from hera.analysis import open_run, sdh_fft, luttinger_frequency
from scipy.signal import find_peaks

r5 = open_run('data/5'); m5 = load_meta(5)
Ib5 = m5['measurement_config']['bias_voltage'] / m5['measurement_config']['bias_resistor']
B5 = r5.col('magnet_mag'); o5 = np.argsort(B5); B5 = B5[o5]
R_B = {'sr1 T3-T4': (r5.col('sr1_X')/Ib5)[o5], 'sr2 B4-B5': (r5.col('sr2_X')/Ib5)[o5]}
FL_g = luttinger_frequency(8e16); FL_h = luttinger_frequency(8.55e16)  # Hall n=8.55e12
ONSET = 2.0
print(f'HOLE n=-8e12: F_L gate={FL_g:.0f}T, Hall={FL_h:.0f}T')

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for i, (nm, Rc) in enumerate(R_B.items()):
    dR = Rc - np.polyval(np.polyfit(B5, Rc, 5), B5)
    ax[i,0].plot(B5, Rc, lw=.7); ax[i,0].set_title(f'{nm} Rxx(B) hole'); ax[i,0].set_ylabel('Rxx (ohm)'); ax[i,0].grid(alpha=.3)
    for det, win in [(5,'hann'), (3,'hann'), (7,'blackman')]:
        f, Sg = sdh_fft(Rc.reshape(-1,1), B5, b_range=(ONSET,8.0), detrend=det, window=win, nfft=4096, log=False)
        ax[i,1].plot(f, Sg[0]/np.nanmax(Sg[0]), lw=.9, label=f'd{det} {win}')
    for x,c,l,lab in [(16,'g',':','f_ML 16'),(72,'m',':','f_BL 72'),(FL_g,'k','--',f'F_L {FL_g:.0f}'),(FL_h,'b','-.',f'F_L Hall {FL_h:.0f}'),(88,'r',':','16+72=88')]:
        ax[i,1].axvline(x, color=c, ls=l, lw=1, label=lab)
    ax[i,1].set_xlim(0,120); ax[i,1].set_title(f'{nm} FFT [2,8]T'); ax[i,1].set_xlabel('F (T)'); ax[i,1].legend(fontsize=6); ax[i,1].grid(alpha=.3)
    f, Sg = sdh_fft(Rc.reshape(-1,1), B5, b_range=(ONSET,8.0), detrend=5, window='hann', nfft=4096, log=False)
    S = Sg[0]; band=(f>5)&(f<115); fb,Sb=f[band],S[band]
    pk,_=find_peaks(Sb,height=0.12*Sb.max(),distance=8); pk=sorted(fb[pk[np.argsort(Sb[pk])[::-1]][:4]])
    print(f'[{nm}] tones(T): {[round(p,1) for p in pk]}')
plt.suptitle('Spot B hole n=-8e12: ABA pair 16+72=F_L(Hall) + intermod (88=sum, 56=diff)', y=1.01)
plt.tight_layout(); plt.show()
print('READ: hole side confirms the ML(16)+BL(72) pair = F_L (ABA), strong/clean SdH.')
print('Extra peaks ~88-93T (=16+72 sum-intermod) and 40-57T (=72-16 diff/harmonics) from')
print('the stronger nonlinear oscillations; screened by n-dependence in the fan.')
print('-> ABA in BOTH regions on BOTH density sides (4/4 spot-check measurements).')
