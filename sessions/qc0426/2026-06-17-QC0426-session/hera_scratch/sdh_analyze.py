"""SdH spot-check analysis. Usage: menv python sdh_analyze.py <run_id> <n_cm2> [onset_T]
Per-channel: raw Rxx(B), 5th-order background subtract, onset read, FFT in 1/B vs F_L,
peak set + Luttinger combinatorics, FFT-stability sweep (detrend/window)."""
import sys, json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

run_id = sys.argv[1]; n_cm = float(sys.argv[2]); onset = float(sys.argv[3]) if len(sys.argv) > 3 else None
r = open_run(f'data/{run_id}')
m = json.load(open(f'data/{run_id}/metadata.json'))
Ib = m['measurement_config']['bias_voltage'] / m['measurement_config']['bias_resistor']
B = r.col('magnet_mag')
order = np.argsort(B); B = B[order]
chans = {'sr1 T3-T4': 'sr1_X', 'sr2 B4-B5': 'sr2_X'}
FL = luttinger_frequency(abs(n_cm) * 1e4)   # n in m^-2
print(f'run {run_id}: n={n_cm:+.1e} cm^-2, F_L={FL:.1f} T, B {B.min():.3f}..{B.max():.3f} T, npts={len(B)}')

fig, axes = plt.subplots(len(chans), 3, figsize=(16, 4.2 * len(chans)))
if len(chans) == 1: axes = axes[None, :]
for i, (nm, col) in enumerate(chans.items()):
    R = (r.col(col) / Ib)[order]
    # background subtract (5th order) for onset + raw oscillation view
    p = np.polyfit(B, R, 5); dR = R - np.polyval(p, B)
    a0, a1, a2 = axes[i]
    a0.plot(B, R, lw=.8); a0.set_title(f'{nm}  Rxx(B)'); a0.set_xlabel('B (T)'); a0.set_ylabel('Rxx (ohm)'); a0.grid(alpha=.3)
    a1.plot(B, dR, lw=.8); a1.set_title('dRxx (5th-order bkg removed)'); a1.set_xlabel('B (T)'); a1.grid(alpha=.3)
    if onset: a1.axvline(onset, color='r', ls='--', lw=1, label=f'onset {onset}T'); a1.legend(fontsize=8)
    # FFT over [onset, Bmax]; stability sweep over detrend + window
    blo = onset if onset else max(B.min(), 0.5)
    for det, win, lab in [(5, 'hann', 'd5 hann'), (3, 'hann', 'd3 hann'), (5, 'blackman', 'd5 black')]:
        f, Sg = sdh_fft(R.reshape(-1, 1), B, b_range=(blo, B.max()), detrend=det, window=win, nfft=2048, log=False)
        S = Sg[0]
        a2.plot(f, S / np.nanmax(S), lw=.9, label=lab)
    a2.axvline(FL, color='k', ls='--', lw=1, label=f'F_L={FL:.0f}T')
    a2.axvline(FL / 2, color='gray', ls=':', lw=1, label='F_L/2')
    a2.set_xlim(0, FL * 1.6); a2.set_title('FFT in 1/B (stability sweep)'); a2.set_xlabel('F (T)'); a2.legend(fontsize=7); a2.grid(alpha=.3)
    # report peaks (on d5/hann)
    f, Sg = sdh_fft(R.reshape(-1, 1), B, b_range=(blo, B.max()), detrend=5, window='hann', nfft=2048, log=False)
    S = Sg[0]
    band = (f > 3) & (f < FL * 1.5)
    fb, Sb = f[band], S[band]
    from scipy.signal import find_peaks
    pk, _ = find_peaks(Sb, height=0.15 * Sb.max(), distance=10)
    pk = pk[np.argsort(Sb[pk])[::-1]][:6]
    print(f'  [{nm}] onset~{blo}T  peaks (T): ' +
          ', '.join(f'{fb[k]:.1f}({Sb[k]/Sb.max():.2f})' for k in pk) +
          f'  | F_L={FL:.1f}  F_L/2={FL/2:.1f}')
plt.tight_layout(); plt.savefig(f'hera_scratch/sdh_{run_id}.png', dpi=100)
print(f'saved hera_scratch/sdh_{run_id}.png')
