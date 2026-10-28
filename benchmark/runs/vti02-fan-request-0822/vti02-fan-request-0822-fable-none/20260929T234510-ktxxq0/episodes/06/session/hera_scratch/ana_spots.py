"""Runs 6 & 7 — SdH spot checks: raw traces, onset, FFT, tone read."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import (open_run, summarize_run, resolve_channels,
                           current_channel, sdh_fft, sdh_onset, SdhOnsetError,
                           luttinger_frequency)

for rid in (6, 7):
    r = open_run(f'data/{rid}')
    print(f'===== run {rid} =====')
    print(summarize_run(r))
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    B = r.col('magnet_field')
    I = r.col(cur.col) / cur.gain
    vch = [c for c in chans if not c.is_current][0]
    R = (r.col(vch.col) / vch.gain) / I
    print(f'I_bias med {np.median(np.abs(I))*1e9:.2f} nA | R range {np.nanmin(R):.1f}..{np.nanmax(R):.1f} Ohm')
    np.save(f'hera_scratch/run{rid}_B.npy', B); np.save(f'hera_scratch/run{rid}_R.npy', R)

    # onset + tones
    sens = 50e-6
    rfs = sens / np.median(np.abs(I))
    try:
        o = sdh_onset(np.abs(R), B, r_full_scale=rfs)
        print(o.summary())
    except SdhOnsetError as e:
        print('SdhOnsetError:', e)

    # FFT over the high-B window
    blo = 1.5 if rid == 6 else 1.0
    sel = B > blo
    f, spec = sdh_fft(np.abs(R[sel])[:, None], B[sel], nfft=2048)
    spec = spec[0]
    print('top FFT peaks (f>2T):')
    from scipy.signal import find_peaks
    pk, _ = find_peaks(spec, height=0.05*spec[f > 2].max())
    pk = [p for p in pk if f[p] > 2]
    for p in sorted(pk, key=lambda p: -spec[p])[:8]:
        print(f'  F = {f[p]:6.2f} T   mag {spec[p]:.3g}')

    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    ax[0].plot(B, np.abs(R), lw=0.5); ax[0].set_xlabel('B (T)'); ax[0].set_ylabel('R (Ohm)')
    ax[0].set_title(f'run {rid} raw')
    ax[1].plot(f, spec); ax[1].set_xlim(0, 60); ax[1].set_xlabel('F (T)'); ax[1].set_title(f'FFT, B>{blo} T')
    fig.tight_layout(); fig.savefig(f'hera_scratch/spot_run{rid}.png', dpi=110)
    print()

# model expectations at the two spots
for n12 in (3.2, -1.2):
    F = luttinger_frequency(abs(n12) * 1e16)
    print(f'n = {n12:+.1f}e12: full-density F_L = {F:.1f} T')
