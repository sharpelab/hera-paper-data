"""Runs 6 & 7 — sdh-spot-check read: raw MR, onset, 1/B FFT vs F_L."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)


def load(i):
    r = open_run("data/%d" % i)
    B = r.col("magnet_field")
    R = (r.col("sr1_X") / 1.0) / (r.col("sr0_X") / -1e6)
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    o = np.argsort(B)
    return B[o], R[o], T[o], itg[o], ibg[o], r


fig, axes = plt.subplots(2, 2, figsize=(13, 8))
out = {}
for k, (i, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    B, R, T, itg, ibg, r = load(i)
    FL = luttinger_frequency(abs(n12) * 1e12 * 1e4)  # m^-2
    print("\n===== run %d  n = %+.2fe12  F_L = %.2f T" % (i, n12, FL))
    print("  T_sample %.3f-%.3f K; |I_tg|max %.2e A  |I_bg|max %.2e A"
          % (T.min(), T.max(), np.abs(itg).max(), np.abs(ibg).max()))
    print("  R(B): min %.1f  at B=%.2f ; max %.1f at B=%.2f ; R(Bmin)=%.1f Ohm"
          % (R.min(), B[np.argmin(R)], R.max(), B[np.argmax(R)], R[0]))
    # full-scale check: sens 50 uV, I_bias
    mc = r.meta.get("measurement_config", {})
    print("  measurement_config:", {kk: vv for kk, vv in mc.items() if "amp" in kk.lower() or "sens" in kk.lower() or "gain" in kk.lower() or "bias" in kk.lower() or "Si" in kk})
    ax = axes[0, k]
    ax.plot(B, R, lw=0.7)
    ax.set(xlabel="B (T)", ylabel=r"$R_{xx}$ ($\Omega$)", title="run %d raw: n=%+.2fe12, D=0" % (i, n12))

    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        out[i] = on
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e)
        on = None

    # FFT over a couple of cutoffs
    ax2 = axes[1, k]
    for cut in (1.0, 1.5, 2.0, 3.0):
        if cut >= B.max():
            continue
        f, sp = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5)
        ax2.plot(f, sp[0] / sp[0].max(), lw=0.9, label="cut %.1f T" % cut)
        pk = f[np.argsort(sp[0])[::-1][:6]]
        print("  FFT cut %.1f T: top peaks (T) %s ; dF=%.2f"
              % (cut, np.array2string(np.sort(pk), precision=2), 1 / (1 / cut - 1 / B.max())))
    ax2.axvline(FL, color="k", ls="--", label="F_L=%.1f T" % FL)
    ax2.set(xlim=(0, 1.6 * FL), xlabel="F (T)", ylabel="norm |FFT|", title="run %d 1/B FFT" % i)
    ax2.legend(fontsize=7)

plt.tight_layout()
plt.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("\nsaved hera_scratch/spot_runs67.png")
