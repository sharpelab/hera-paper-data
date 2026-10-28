"""Runs 6 & 7 — SdH spot checks (electron n=+3.2e12, hole n=-1.2e12) at D=0.
Raw MR, sdh_onset per trace, sdh_fft above onset, tones vs F_L and the
fs_count_b0 model. Feeds the landau-fan design."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_onset, sdh_fft, SdhOnsetError,
                           luttinger_frequency)

sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count')
import fs_count_b0 as fs

SENS = 50e-6  # sr1 sensitivity, V (both runs)

out = {}
fig, axs = plt.subplots(3, 2, figsize=(13, 12))

for j, (rid, n_cm2) in enumerate([(6, 3.2e12), (7, -1.2e12)]):
    run = open_run(f'data/{rid}')
    chs = resolve_channels(run.meta)
    cur = current_channel(chs)
    volt = [c for c in chs if not c.is_current and c.cid == 'sr1'][0]
    B = run.col('magnet_field')
    I = np.abs(run.col(cur.col) / cur.gain)
    R = np.abs((run.col(volt.col) / volt.gain) / (run.col(cur.col) / cur.gain))
    order = np.argsort(B)
    B, R, I = B[order], R[order], I[order]
    i_med = float(np.median(I))
    r_fs = SENS / i_med

    FL = luttinger_frequency(n_cm2)  # h/4e * n
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        summ = on.summary()
        onset = on.onset_b
    except SdhOnsetError as e:
        summ, onset, on = f'SdhOnsetError: {e}', None, None
    print(f'== run {rid}  n={n_cm2:+.2e}  F_L={FL:.1f} T  I_med={i_med*1e9:.3f} nA '
          f'R(B=0)={R[np.argmin(B)]:.1f} Ohm  r_fs={r_fs:.0f} Ohm')
    print(summ)

    # raw MR
    ax = axs[0, j]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel('B (T)'); ax.set_ylabel('R_xx (Ohm)')
    ax.set_title(f'run {rid}: raw MR, n={n_cm2/1e12:+.1f}e12, D=0')

    # background-subtracted (poly deg 5 in B, above onset window)
    cut = max(onset if onset else 1.0, 1.0)
    m = B >= cut
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax = axs[1, j]
    ax.plot(1.0/B[m], dR, lw=0.6)
    ax.set_xlabel('1/B (1/T)'); ax.set_ylabel('dR_xx (Ohm)')
    ax.set_title(f'run {rid}: dR vs 1/B above {cut:.2f} T')

    # FFT
    freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, float(B.max())))
    sp = spec[0]
    ax = axs[2, j]
    ax.plot(freqs, sp / sp.max(), lw=0.8)
    ax.axvline(FL, color='r', ls='--', label=f'F_L={FL:.1f} T')
    # model tones
    try:
        _, orb = fs.abab_fs(n_cm2)
        for F, _k in orb:
            ax.axvline(F, color='g', ls=':', alpha=0.8)
        ax.plot([], [], 'g:', label='ABAB model')
    except Exception as e:
        print('abab_fs:', e)
    try:
        _, _, _, nf, Ftot = fs.abca_fs(n_cm2)
        ax.axvline(Ftot, color='m', ls='-.', alpha=0.8, label=f'ABCA {Ftot:.1f} T')
    except Exception as e:
        print('abca_fs:', e)
    ax.set_xlim(0, FL * 1.6)
    ax.set_xlabel('F (T)'); ax.set_ylabel('FFT (norm)')
    ax.legend(fontsize=8)
    ax.set_title(f'run {rid}: FFT in 1/B, window [{cut:.2f}, {B.max():.1f}] T')

    out[rid] = dict(n=n_cm2, FL=FL, onset=onset, i_med=i_med,
                    peak_freqs=[float(freqs[k]) for k in
                                (sp > 0.15 * sp.max()).nonzero()[0]
                                if 0 < k < len(sp) - 1
                                and sp[k] >= sp[k-1] and sp[k] >= sp[k+1]
                                and freqs[k] > 3])
    print('local peaks >15%:', ['%.1f' % f for f in out[rid]['peak_freqs']])

fig.tight_layout()
fig.savefig('hera_scratch/spots_67.png', dpi=110)
print(json.dumps({str(k): v for k, v in out.items()}, indent=1, default=float))
