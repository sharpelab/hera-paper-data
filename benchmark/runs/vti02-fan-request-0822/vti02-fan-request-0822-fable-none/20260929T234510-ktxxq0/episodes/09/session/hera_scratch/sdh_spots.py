"""SdH read of spot checks: run 6 (electron n=+3.2e12, B 0->10 T) and run 7 (hole n=-1.2e12, 10->0.3 T).
Raw traces, background-subtracted oscillations, sdh_onset tone tables, sdh_fft spectra,
compared against the Luttinger frequency for the run-5 calibration density."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency, SdhOnsetError

SPOTS = {6: ("electron", +3.2e16), 7: ("hole", -1.2e16)}  # n in m^-2
fig, ax = plt.subplots(3, 2, figsize=(12, 10))

for j, (rid, (side, n_si)) in enumerate(SPOTS.items()):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / np.abs(I)
    order = np.argsort(B)
    B, R = B[order], R[order]
    FL = luttinger_frequency(n_si)
    print(f"run {rid} ({side}, n = {n_si*1e-16:+.2f}e12): {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"R {R.min():.1f}-{R.max():.1f} Ohm | F_L(4-fold) = {FL:.1f} T")

    ax[0, j].plot(B, R, lw=0.7)
    ax[0, j].set_title(f"run {rid} {side}: raw R vs B")
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")

    # onset + tone table (r_full_scale = sens/I_bias = 50 uV / 10 nA = 5 kOhm)
    try:
        o = sdh_onset(R, B, b_lo=0.3, r_full_scale=5000.0)
        print(o.summary())
    except SdhOnsetError as e:
        print(f"  sdh_onset failed: {e}")
        o = None

    # FFT over the upper 1/B window
    for b_lo, style in ((1.5, "-"), (3.0, "--")):
        f, sp = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()), nfft=4096, bg_degree=5, log=False)
        sp = sp[0] / sp[0].max()
        ax[1, j].plot(f, sp, style, lw=0.8, label=f"B {b_lo}-{B.max():.0f} T")
    ax[1, j].axvline(FL, color="r", ls=":", label=f"F_L = {FL:.1f} T")
    for frac, c in ((0.5, "g"), (0.25, "orange")):
        ax[1, j].axvline(FL * frac, color=c, ls=":", alpha=0.6)
    ax[1, j].set_xlim(0, 1.6 * FL)
    ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("FFT amp (norm)")
    ax[1, j].legend(fontsize=7); ax[1, j].set_title(f"run {rid}: SdH FFT (F_L, F_L/2, F_L/4 marked)")

    # background-subtracted oscillation vs 1/B (poly in B)
    sel = B >= 1.0
    bg = np.polyval(np.polyfit(B[sel], R[sel], 5), B[sel])
    ax[2, j].plot(1 / B[sel], R[sel] - bg, lw=0.6)
    ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_ylabel("dR (Ohm)")
    ax[2, j].set_title(f"run {rid}: dR vs 1/B (deg-5 bg, B>1 T)")

fig.tight_layout()
fig.savefig("hera_scratch/sdh_spots.png", dpi=130)
print("saved hera_scratch/sdh_spots.png")
