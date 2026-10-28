# Runs 6 and 7, raw data before FFT. Channel arithmetic follows device card.
from hera.analysis import sdh_fft, sdh_onset
from scipy.signal import find_peaks

fig, axs = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
for j, (rid, density, cutoff) in enumerate([(6, 3.2, 1.3), (7, -1.2, 0.7)]):
    rr = run(rid)
    B = rr.col('magnet_field')
    I = rr.col('sr0_X') / -1e6
    R = rr.col('sr1_X') / I
    order = np.argsort(B)
    B, R = B[order], R[order]
    axs[0,j].plot(B, R, lw=0.8)
    axs[0,j].set(title=f'Run {rid}, n={density:+.1f}e12, D=0: raw Rxx', xlabel='B (T)', ylabel='Rxx (ohm)')
    f, power = sdh_fft(R[:,None], B, b_range=(cutoff, 10), nfft=4096, bg_degree=5, log=False)
    y = power[0]
    axs[1,j].plot(f, y, lw=0.9)
    axs[1,j].axvline(10.339*abs(density), color='k', ls=':', lw=1, label='F_L geometry prior')
    axs[1,j].set(xlim=(0, 45), xlabel='frequency (T)', ylabel='FFT power', title=f'FFT: {cutoff:.1f}–10 T; B-space polynomial background')
    axs[1,j].legend(fontsize=8)
    peaks,_ = find_peaks(y)
    peaks = sorted((i for i in peaks if 3<f[i]<40), key=lambda i:y[i], reverse=True)[:6]
    print(f'run {rid}: strongest FFT peaks {[round(float(f[i]),1) for i in peaks]} T; F_L={10.339*abs(density):.1f} T')
    on = sdh_onset(R,B,b_lo=0.3,b_hi=10,r_full_scale=5000)
    print(on.summary())
plt.show()
