"""Runs 6 & 7 — SdH spot checks at D = 0 (run-5 cal): raw traces, background-subtracted
oscillations in 1/B, and SdH FFTs with the peak table. Sum-rule check against
F_total = n h / (4e)."""
from scipy.signal import find_peaks

E12 = 1e16  # 1e12 cm^-2 in m^-2
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for row, (rid, nspot, lab) in enumerate([(6, +3.2, 'run 6 — electron, n = +3.2e12'),
                                         (7, -1.2, 'run 7 — hole, n = -1.2e12')]):
    r = run(rid)
    B = r.col('magnet_field')
    R = r.col('sr1_X') / (r.col('sr0_X') / -1e6)   # (V/gain)/I, signed
    F_tot = abs(nspot) * E12 * cst.h / (4 * cst.e)

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel('B (T)'); ax.set_ylabel('Rxx (Ohm)'); ax.set_title(lab)

    m = B > 1.5
    Bs = np.sort(B[m]); Rs = R[m][np.argsort(B[m])]
    bg = np.polyval(np.polyfit(Bs, Rs, 5), Bs)
    ax = axes[row, 1]
    ax.plot(1 / Bs, Rs - bg, lw=0.6)
    ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dRxx (Ohm)')
    ax.set_title('oscillation, B > 1.5 T, poly5 removed')

    freqs, spec = sdh_fft(R[:, None], B, b_range=(1.5, 10), nfft=4096, bg_degree=5, log=False)
    sp = spec[0]
    noise = np.median(sp[freqs > 150])
    pk, _ = find_peaks(sp, height=10 * noise, distance=3)
    pk = [p for p in pk if 2 < freqs[p] < 120]
    ax = axes[row, 2]
    ax.plot(freqs, sp, lw=0.8)
    ax.axvline(F_tot, color='g', ls='--', lw=1, label=f'F_total(g=4) = {F_tot:.1f} T')
    for p in pk[:8]:
        ax.axvline(freqs[p], color='r', ls=':', lw=0.6)
    ax.set_xlim(0, 120); ax.set_xlabel('F (T)'); ax.set_ylabel('|FFT|')
    ax.set_title('SdH FFT in 1/B (1.5–10 T)'); ax.legend(fontsize=8)
    print(f'run {rid}: F_total(g=4) = {F_tot:.1f} T; R(B_min) = {R[np.argmin(B)]:.0f} Ohm, '
          f'R(10 T) = {R[np.argmax(B)]:.0f} Ohm; peaks (F, amp):')
    print('   ' + ', '.join(f'{freqs[p]:.1f} T ({sp[p]:.2g})' for p in pk[:8]))
fig.tight_layout()
