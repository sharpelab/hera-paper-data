# SdH spot checks — runs 6 (electron, n=+3.2e12, D=0) and 7 (hole, n=-1.2e12, D=0)
# Raw R(B), onset + FFT read for each; informs the Landau-fan design.
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import (open_run, summarize_run, resolve_channels,
                           current_channel, sdh_onset, sdh_fft, SdhOnsetError,
                           luttinger_frequency)

BASE = '/home/hera/measurements/zack/20260822-vti-02/data'

def load(rid):
    r = open_run(f'{BASE}/{rid}')
    print(f'=== run {rid} ===')
    print(summarize_run(r))
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    B = r.col('magnet_field')
    I = r.col(cur.col) / cur.gain
    v = [c for c in chans if not c.is_current and c.cid == 'sr1'][0]
    R = (r.col(v.col) / v.gain) / I
    print(f'I median {np.median(I)*1e9:.3f} nA; R range {np.min(R):.1f} .. {np.max(R):.1f} Ohm')
    return r, B, R, I

fig, axes = plt.subplots(2, 3, figsize=(15, 7))
results = {}
for row, (rid, label, nspot) in enumerate([(6, 'electron n=+3.2e12', +3.2e16),
                                           (7, 'hole n=-1.2e12', -1.2e16)]):
    r, B, R, I = load(rid)
    # sort ascending in B for analysis
    idx = np.argsort(B)
    Bs, Rs = B[idx], np.abs(R[idx])
    m = Bs > 0.25
    Bs, Rs = Bs[m], Rs[m]
    ax = axes[row, 0]
    ax.plot(Bs, Rs, lw=0.5)
    ax.set_xlabel('B (T)'); ax.set_ylabel('|Rxx| (Ohm)'); ax.set_title(f'run {rid} {label}')
    # onset
    r_fs = 50e-6 / np.median(np.abs(I))
    try:
        on = sdh_onset(Rs, Bs, r_full_scale=r_fs)
        print(on.summary())
        results[rid] = on
    except SdhOnsetError as e:
        print(f'run {rid}: SdhOnsetError: {e}')
        results[rid] = None
    # FFT high-B window
    for col, brange in [(1, (2.0, Bs.max())), (2, (4.0, Bs.max()))]:
        f, spec = sdh_fft(Rs[:, None], Bs, b_range=brange)
        sp = spec[0]
        ax = axes[row, col]
        ax.plot(f, sp / sp.max(), lw=0.8)
        ax.set_xlim(0, 120); ax.set_xlabel('F (T)')
        ax.set_title(f'FFT {brange[0]}-{Bs.max():.0f} T')
        # top peaks
        from scipy.signal import find_peaks
        pk, _ = find_peaks(sp, height=0.05 * sp.max(), distance=3)
        top = sorted(pk, key=lambda i: -sp[i])[:6]
        print(f'run {rid} FFT {brange}: peaks (T, rel amp):',
              [(round(float(f[i]), 1), round(float(sp[i] / sp.max()), 2)) for i in sorted(top)])
    F_full = luttinger_frequency(abs(nspot))
    print(f'run {rid}: full-density 4-fold Onsager F = {F_full:.1f} T for n = {nspot/1e16:+.1f}e12\n')

plt.tight_layout()
plt.savefig('/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_runs6_7.png', dpi=110)
print('saved spots_runs6_7.png')
