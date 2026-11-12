from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset
from scipy.signal import find_peaks
import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 1, figsize=(9, 7), sharex=True)
for j, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}")
    cc = current_channel(resolve_channels(r.meta))
    I = r.col(cc.col) / cc.gain
    B, R = r.col("magnet_field"), r.col("sr1_X") / I
    for blo in (1.2, 1.5, 2.0):
        f, spec = sdh_fft(R[:, None], B, b_range=(blo, 10.0), nfft=4096, log=False)
        y = spec[0]
        ax[j].plot(f, y / np.max(y), label=f"{blo}–10 T")
        peaks, _ = find_peaks(y, prominence=0.12 * np.max(y))
        print(f"run {rid}, B≥{blo}: "+", ".join(f"{f[k]:.1f} T" for k in sorted(peaks,key=lambda k:y[k],reverse=True)[:6]))
    o = sdh_onset(R, B, b_lo=0.8, r_full_scale=5000)
    print(f"run {rid}: {o.summary()}")
    ax[j].set(xlim=(0, 45), ylabel="FFT / max", title=f"run {rid} window test")
    ax[j].legend()
ax[-1].set_xlabel("frequency (T)")
fig.tight_layout()
plt.show()
