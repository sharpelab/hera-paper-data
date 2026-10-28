"""Runs 6 & 7 — SdH spot checks (electron n=+3.2e12, hole n=-1.2e12 at D=0).
Raw R(B), then sdh_onset + sdh_fft per run. Feeds the Landau-fan design."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, SdhOnsetError,
                           luttinger_frequency)

for rid, nlabel in ((6, '+3.2e12 e-side'), (7, '-1.2e12 h-side')):
    r = open_run(f'data/{rid}')
    chs = resolve_channels(r.meta)
    cur = current_channel(chs)
    vch = [c for c in chs if not c.is_current][0]
    B = r.col('magnet_field')
    I = r.col(cur.col) / cur.gain
    R = (r.col(vch.col) / vch.gain) / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    print(f'=== run {rid} ({nlabel}) === rows {r.rows}, B {B.min():.2f}..{B.max():.2f} T')
    print(f'  R(B~min)={R[:5].mean():.1f} ohm, R(B_max)={R[-5:].mean():.1f} ohm, '
          f'Rmax={R.max():.1f} at B={B[np.argmax(R)]:.2f}; I median {np.median(I)*1e9:.2f} nA')
    # full-density Onsager for reference (n in SI)
    n_si = abs(float(nlabel.split()[0].replace('e-side','').replace('h-side',''))) * 1e16
    print(f'  F_Luttinger(full n, 4-fold) = {luttinger_frequency(n_si):.1f} T')
    # onset + tones
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6/10e-9)
        print(so.summary())
    except SdhOnsetError as e:
        print(f'  sdh_onset FAILED: {e}')
    # FFT windows
    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].plot(B, R, lw=0.6); ax[0].set(xlabel='B (T)', ylabel='R_xx (ohm)', title=f'run {rid}: raw R(B), n {nlabel}')
    m = B > 1.0
    ax[1].plot(1/B[m], R[m], lw=0.6); ax[1].set(xlabel='1/B (1/T)', ylabel='R_xx (ohm)', title='vs 1/B (B>1T)')
    for b_lo, b_hi, c in ((2.0, B.max(), 'C0'), (4.0, B.max(), 'C1'), (6.0, B.max(), 'C3')):
        try:
            f, sp = sdh_fft(R[:, None], B, b_range=(b_lo, b_hi))
            s1 = sp[0]; s1 = s1/ s1[f > 2].max()
            ax[2].plot(f, s1, c, lw=0.8, label=f'{b_lo:.0f}-{b_hi:.0f} T')
        except Exception as e:
            print(f'  fft {b_lo}-{b_hi}: {e}')
    ax[2].set(xlabel='F (T)', ylabel='norm |FFT|', xlim=(0, 80), title='SdH FFT in 1/B')
    ax[2].legend()
    fig.tight_layout(); fig.savefig(f'hera_scratch/spot_run{rid}.png', dpi=110)
    print()
