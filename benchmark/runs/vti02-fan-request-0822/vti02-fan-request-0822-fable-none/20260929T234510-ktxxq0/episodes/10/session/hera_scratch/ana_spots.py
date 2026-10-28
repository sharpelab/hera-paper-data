# Scratch: SdH spot checks — run 6 (electron, n=+3.2e12) and run 7 (hole, n=-1.2e12)
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

FS_R = 50e-6 / 10e-9   # sr1 sensitivity / I_bias = 5 kOhm full scale

for rid in (6, 7):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    B = r.col("magnet_field")
    I = r.col(cur.col) / cur.gain
    v = [c for c in chans if c.cid == "sr1"][0]
    R = (r.col("sr1_X") / v.gain) / I
    order = np.argsort(B)
    B, R = B[order], R[order]
    print(f"\n===== run {rid}: {r.tags} =====")
    print(f"rows {r.rows}, B {B.min():.2f}..{B.max():.2f} T, R med {np.median(R):.1f} Ohm, max {R.max():.1f}")
    try:
        o = sdh_onset(R, B, r_full_scale=FS_R)
        print(o.summary())
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}")
    # FFT over upper 1/B window regardless
    for b_lo in (1.5, 3.0):
        f, s = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()))
        s = s[0]
        # top peaks
        from scipy.signal import find_peaks
        pk, _ = find_peaks(s, height=0.1 * s.max())
        top = sorted(pk, key=lambda i: -s[i])[:6]
        print(f"FFT b_range ({b_lo},{B.max():.1f}): peaks " +
              ", ".join(f"{f[i]:.1f} T (a={s[i]:.2g})" for i in top))

    fig, ax = plt.subplots(2, 1, figsize=(9, 7))
    ax[0].plot(B, R, lw=0.6)
    ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)")
    ax[0].set_title(f"run {rid} raw Rxx(B)")
    f, s = sdh_fft(R[:, None], B, b_range=(1.5, B.max()))
    ax[1].plot(f, s[0], lw=0.8)
    ax[1].set_xlim(0, 80); ax[1].set_xlabel("F (T)"); ax[1].set_ylabel("FFT amp")
    fig.tight_layout()
    fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110)
    print(f"saved hera_scratch/spot_run{rid}.png")
