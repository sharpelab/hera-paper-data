# Runs 6 & 7 — onset tracking + FFT in 1/B vs F_L and the fs_count_b0 model
import sys
import numpy as np, matplotlib.pyplot as plt
from hera.analysis import sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count')
import fs_count_b0 as fs

# FFT windows: run 6's fine (10 mT) leg starts at 1.0 T — the 50 mT leg below
# undersamples the 7 T tone below B ~ 0.85 T (d(1/B) Nyquist), so the FFT
# window starts at 1.0 T for both runs (also above run 7's 0.71 T onset).
CUT = 1.0
fig, axs = plt.subplots(1, 2, figsize=(12, 4))
for ax, (rid, n12) in zip(axs, [(6, +3.2), (7, -1.2)]):
    B, R, I, _ = spot_trace(rid)          # from the raw cell above
    FL = luttinger_frequency(n12 * 1e16)  # h/4e * n  (m^-2)
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / np.median(I))
        print(f'-- run {rid} (F_L = {FL:.1f} T):')
        print(on.summary())
    except SdhOnsetError as e:
        print(f'-- run {rid}: SdhOnsetError: {e}')
    m = B >= CUT
    freqs, spec = sdh_fft(R[:, None], B, b_range=(CUT, float(B.max())))
    sp = spec[0] / spec[0].max()
    ax.plot(freqs, sp, lw=0.8, label='FFT (1/B)')
    ax.axvline(FL, color='r', ls='--', label=f'F_L = {FL:.1f} T')
    for F, mm in fs.abab_mstar(n12 * 1e16):
        ax.axvline(F, color='g', ls=':', alpha=0.9)
    ax.plot([], [], 'g:', label='ABAB model F(n)')
    Ft, ma = fs.abca_mstar(n12 * 1e16)
    ax.axvline(Ft, color='m', ls='-.', alpha=0.8, label=f'ABCA {Ft:.1f} T (m*={ma:.2f})')
    dF = 1.0 / (1.0 / CUT - 1.0 / B.max())
    ax.set_xlim(0, FL * 1.7); ax.set_xlabel('F (T)'); ax.set_ylabel('FFT (norm)')
    ax.set_title(f'run {rid}: window [{CUT:.1f}, {B.max():.0f}] T, dF = {dF:.2f} T', fontsize=10)
    ax.legend(fontsize=8)
    pk = [float(freqs[k]) for k in range(1, len(sp) - 1)
          if sp[k] > 0.15 and sp[k] >= sp[k-1] and sp[k] >= sp[k+1] and freqs[k] > 3]
    print(f'run {rid}: FFT peaks >15% in window: {["%.1f" % f for f in pk]}')
fig.tight_layout()
