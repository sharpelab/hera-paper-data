# Runs 6-7: onset + FFT-in-1/B read vs F_L and the FS-count forward model
import sys
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, SdhOnsetError
sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count')
import fs_count_b0 as fscm

fig, axs = plt.subplots(2, 2, figsize=(13, 7))
for row, (rid, nn) in enumerate(((6, +3.2e12), (7, -1.2e12))):
    B, R, I = runs67[rid]
    m = B >= 1.0                       # fine-grid segment only (run 7 is 20 mT throughout; keep symmetric)
    FL = luttinger_frequency(nn * 1e4)  # n in m^-2
    print(f'===== run {rid}: n = {nn:+.1e} cm^-2, F_L = {FL:.1f} T =====')
    try:
        on = sdh_onset(R[m], B[m], r_full_scale=5e-5 / np.median(np.abs(I)))
        print(on.summary())
    except SdhOnsetError as e:
        print('SdhOnsetError:', e)

    # bg-subtracted trace in 1/B
    p = np.polyfit(B[m], R[m], 5)
    axs[row, 0].plot(1/B[m], R[m] - np.polyval(p, B[m]), lw=0.6)
    axs[row, 0].set_xlabel('1/B (1/T)'); axs[row, 0].set_ylabel('dRxx (ohm)')
    axs[row, 0].set_title(f'run {rid}: bg-subtracted (deg-5 in B), B >= 1 T')

    # FFT, two windows: full record vs pre-QH (stability check)
    ax = axs[row, 1]
    for (lo, hi), style in (((1.0, 10.0), '-'), ((1.0, 7.4), '--')):
        freqs, spec = sdh_fft(R[m][:, None], B[m], b_range=(lo, hi), bg_degree=5)
        s = spec[0]
        ax.plot(freqs, s / s.max(), style, lw=0.9, label=f'B in [{lo}, {hi}] T')
        ip, _ = find_peaks(s, height=0.03 * s.max(), prominence=0.02 * s.max())
        top = sorted(zip(s[ip], freqs[ip]), reverse=True)[:8]
        print(f'  FFT [{lo},{hi}]: ' + ', '.join(f'{f:.1f} T ({a/s.max():.2f})' for a, f in top))
    ax.axvline(FL, color='k', ls=':', lw=1, label=f'F_L = {FL:.1f} T')
    # model tones at nominal density (scale = geometry prior, semi-quantitative)
    ef, orbs = fscm.abab_fs(nn * 1e4)
    for j, (F, kf) in enumerate(orbs):
        ax.axvline(F, color='tab:red', ls='--', lw=0.8,
                   label='ABAB model tones' if j == 0 else None)
    print(f'  model @ nominal n: ABAB pair {[f"{F:.1f}" for F, _ in orbs]} T, ABCA singleton {FL:.1f} T')
    ax.set_xlim(0, 70); ax.set_xlabel('F (T)'); ax.set_ylabel('FFT (norm.)')
    ax.legend(fontsize=7); ax.set_title(f'run {rid}: FFT in 1/B')
plt.tight_layout(); plt.show()
