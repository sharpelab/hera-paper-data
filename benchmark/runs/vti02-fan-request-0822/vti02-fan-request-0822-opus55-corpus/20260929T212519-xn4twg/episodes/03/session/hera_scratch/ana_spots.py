"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): onset, tones, FFT vs F_L + model."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, summarize_run
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    print(summarize_run(r)); print("cols", r.metadata.get("columns"))
    B = r.col("magnet_field"); vx = r.col("sr1_X"); ix = r.col("sr0_X") / -1e6
    R = vx / ix
    o = np.argsort(B); B, R, vx, ix = B[o], R[o], vx[o], ix[o]
    T = r.col("T_sample")
    FL = float(luttinger_frequency(n12 * 1e16))
    print(f"run {rid}: n={n12}e12 F_L={FL:.1f} T; B {B.min():.3f}-{B.max():.3f}, {len(B)} pts; R {R.min():.1f}-{R.max():.1f} Ohm; "
          f"|sr1_X| max {np.abs(vx).max()*1e6:.2f} uV (sens 50 uV); I {ix.min()*1e9:.2f}-{ix.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f}")
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_title(f"run {rid} raw Rxx, n={n12:+}e12"); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("R (Ohm)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary()); out[rid] = on
    except Exception as e:
        print("ONSET ERR", type(e).__name__, e); on = None
    # bg-subtracted
    for lo in ([1.5, 2.5, 4.0] if rid == 6 else [1.0, 2.0, 3.0]):
        m = B >= lo
        cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
        if lo == ([1.5, 2.5, 4.0] if rid == 6 else [1.0, 2.0, 3.0])[1]:
            ax[1, k].plot(1 / B[m], dR, lw=0.7); ax[1, k].set_xlabel("1/B"); ax[1, k].set_title(f"dR (deg5 bg, B>{lo})")
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, nfft=4096, log=False)
        s = sp[0]
        ax[2, k].plot(f, s / s.max(), lw=0.8, label=f"B>{lo}")
        pk = [i for i in range(1, len(s) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and s[i] > 0.12 * s.max() and f[i] > 1.5]
        print(f"  FFT B>{lo}: dF={1/(1/lo-1/B.max()):.2f} T; peaks " + ", ".join(f"{f[i]:.1f}({s[i]/s.max():.2f})" for i in pk[:10]))
    ax[2, k].axvline(FL, color="k", ls="--"); ax[2, k].set_xlim(0, 2.2 * FL); ax[2, k].legend(); ax[2, k].set_title(f"FFT |dR|, F_L={FL:.1f} T")
fig.tight_layout(); fig.savefig("hera_scratch/spots_6_7.png", dpi=90)
