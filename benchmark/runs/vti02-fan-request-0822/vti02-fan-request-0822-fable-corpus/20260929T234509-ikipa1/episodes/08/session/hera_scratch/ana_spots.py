# SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12)
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import (open_run, summarize_run, sdh_onset, sdh_fft,
                           luttinger_frequency, SdhOnsetError)

def snap_param(run, inst, name):
    try:
        return run.meta['instruments'][inst]['snapshot']['parameters'][name]['value']
    except Exception:
        return None

fig, axs = plt.subplots(2, 3, figsize=(15, 7))

for row, (rid, nn) in enumerate(((6, +3.2e12), (7, -1.2e12))):
    run = open_run(f'/home/hera/measurements/zack/20260822-vti-02/data/{rid}')
    B = run.col('magnet_field')
    order = np.argsort(B)
    B = B[order]
    # I from transimpedance drain channel sr0 (gain -1e6 V/A)
    I = run.col('sr0_X')[order] / (-1e6)
    V = run.col('sr1_X')[order]           # sr1 gain 1 (device card)
    R = V / np.abs(I)
    sens = snap_param(run, 'sr1', 'sensitivity')
    amp  = snap_param(run, 'sr1', 'amplitude')
    tc   = snap_param(run, 'sr1', 'time_constant')
    ib_nom = amp / 100e6 if amp else None
    print(f'===== run {rid} =====')
    FL = luttinger_frequency(nn)
    print(f'n = {nn:+.2e} -> F_L = {FL:.2f} T; sr1 sens={sens}, amp={amp} (I_bias~{ib_nom}), tau={tc}')
    print(f'I drain: {np.median(np.abs(I))*1e9:.3f} nA median (min {np.abs(I).min()*1e9:.3f})')
    print(f'R(B lo) = {R[:5].mean():.1f} ohm, R(B hi) = {R[-5:].mean():.1f} ohm, Rmax = {R.max():.1f}')
    rfs = sens / np.median(np.abs(I)) if sens else None
    try:
        on = sdh_onset(R, B, r_full_scale=rfs)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print('SdhOnsetError:', e)
        on, onset = None, None

    ax = axs[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel('B (T)'); ax.set_ylabel('Rxx (ohm)')
    ax.set_title(f'run {rid}: n={nn/1e12:+.1f}e12, F_L={FL:.1f} T')

    cut = onset if onset else 1.5
    m = B >= cut
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax = axs[row, 1]
    ax.plot(1/B[m], dR, lw=0.6)
    ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dRxx (ohm)')
    ax.set_title(f'bg-subtracted, B >= {cut:.2f} T')

    ax = axs[row, 2]
    for cutoff, style in ((cut, '-'), (cut + 0.7, '--')):
        freqs, spec = sdh_fft(R[:, None], B, b_range=(cutoff, B.max()), bg_degree=5)
        s = spec[0]
        ax.plot(freqs, s/s.max(), style, lw=0.9, label=f'cutoff {cutoff:.2f} T')
        ip, props = find_peaks(s, height=0.03*s.max(), prominence=0.02*s.max())
        top = sorted(zip(s[ip], freqs[ip]), reverse=True)[:8]
        print(f'cutoff {cutoff:.2f}: top peaks (amp_rel, F): ' +
              ', '.join(f'({a/s.max():.2f}, {f:.1f} T)' for a, f in top))
    ax.axvline(abs(FL), color='k', ls=':', label=f'F_L={abs(FL):.1f} T')
    ax.set_xlim(0, max(2.2*abs(FL), 20)); ax.set_xlabel('F (T)'); ax.legend(fontsize=7)
    ax.set_title('FFT in 1/B (norm.)')

plt.tight_layout()
plt.savefig('/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_67.png', dpi=110)
print('saved spots_67.png')
