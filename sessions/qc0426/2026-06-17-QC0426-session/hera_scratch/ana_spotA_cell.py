# SdH spot A (run 4): electron n=+8e12, D=0, B 0->8T. RAW Rxx(B) -> background-
# subtract -> FFT in 1/B vs F_L. The FS-count read (fs-count investigation step 3).
from hera.analysis import open_run, sdh_fft, luttinger_frequency
from scipy.signal import find_peaks

r4 = open_run('data/4'); m4 = load_meta(4)
Ib4 = m4['measurement_config']['bias_voltage'] / m4['measurement_config']['bias_resistor']
B4 = r4.col('magnet_mag'); o4 = np.argsort(B4); B4 = B4[o4]
R_A = {'sr1 T3-T4': (r4.col('sr1_X')/Ib4)[o4], 'sr2 B4-B5': (r4.col('sr2_X')/Ib4)[o4]}
bmax_A = {'sr1 T3-T4': 5.3, 'sr2 B4-B5': 8.0}      # sr1 overloads >5.44T (MR climb)
FL_gate = luttinger_frequency(8e16); FL_hall = luttinger_frequency(8.4e16)  # n_Hall from Rxy slope
ONSET = 2.0
print(f'F_L: gate(n=8.0e12)={FL_gate:.1f} T, Hall(n=8.4e12)={FL_hall:.1f} T')

fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for i, (nm, Rc) in enumerate(R_A.items()):
    bm = bmax_A[nm]; sel = B4 <= bm; Bc, Rc2 = B4[sel], Rc[sel]
    dR = Rc2 - np.polyval(np.polyfit(Bc, Rc2, 5), Bc)
    ax[i,0].plot(B4, Rc, lw=.7); ax[i,0].axvline(bm, color='r', ls=':', label=f'use<{bm}T (ovld)')
    ax[i,0].set_title(f'{nm}  Rxx(B)'); ax[i,0].set_ylabel('Rxx (ohm)'); ax[i,0].grid(alpha=.3); ax[i,0].legend(fontsize=7)
    ax[i,1].plot(Bc, dR, lw=.8); ax[i,1].axvline(ONSET, color='g', ls='--', label=f'onset {ONSET}T')
    ax[i,1].set_title(f'{nm}  dRxx (5th-order bkg removed)'); ax[i,1].grid(alpha=.3); ax[i,1].legend(fontsize=7)
    for det, win, lab in [(5,'hann','d5 hann'), (3,'hann','d3 hann'), (7,'blackman','d7 black')]:
        f, Sg = sdh_fft(Rc.reshape(-1,1), B4, b_range=(ONSET, bm), detrend=det, window=win, nfft=4096, log=False)
        ax[i,2].plot(f, Sg[0]/np.nanmax(Sg[0]), lw=.9, label=lab)
    ax[i,2].axvline(FL_gate, color='k', ls='--', label=f'F_L gate {FL_gate:.0f}')
    ax[i,2].axvline(FL_hall, color='b', ls='-.', label=f'F_L Hall {FL_hall:.0f}')
    ax[i,2].set_xlim(0, 110); ax[i,2].set_title(f'{nm}  FFT in 1/B [{ONSET}-{bm}T]'); ax[i,2].set_xlabel('F (T)')
    ax[i,2].legend(fontsize=7); ax[i,2].grid(alpha=.3)
    f, Sg = sdh_fft(Rc.reshape(-1,1), B4, b_range=(ONSET, bm), detrend=5, window='hann', nfft=4096, log=False)
    S = Sg[0]; band = (f>5)&(f<110); fb, Sb = f[band], S[band]
    pk,_ = find_peaks(Sb, height=0.12*Sb.max(), distance=8); pk = sorted(fb[pk[np.argsort(Sb[pk])[::-1]][:3]])
    print(f'[{nm}] dominant tones: {[round(p,1) for p in pk]} T ; sum_low+high vs F_L(Hall)={FL_hall:.0f}')
plt.suptitle('Spot A: electron n=+8e12, D=0 -> two-tone (f_ML~17 + f_BL~70) = F_L -> ABA', y=1.01)
plt.tight_layout(); plt.show()
print('READ: two SdH tones partitioning F_L (Hall) in both channels -> two Fermi surfaces')
print('(ML+BL) -> ABA signature, electron side. ABC would be a single tone at F_L.')
