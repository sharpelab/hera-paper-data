"""Spot-check read: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12). Onset + FFT vs F_L."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
SPEC = {6: ("electron", +3.2), 7: ("hole", -1.2)}
I_FS = 50e-6 / 1.0  # sr1 sensitivity 50 uV, gain 1

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
for k, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}")
    side, n12 = SPEC[rid]
    B = r.col("magnet_field")
    I = r.col("sr0_X") / (-1e6)
    V = r.col("sr1_X") / 1.0
    R = V / I
    t = r.col("time"); T = r.col("T_sample")
    o = np.argsort(B); B, R, Rs = B[o], R[o], None
    Rs = R
    F_L = luttinger_frequency(abs(n12) * 1e12 * 1e4)  # cm^-2 -> m^-2
    I_bias = float(r.meta["measurement_config"].get("drive_V", 1.0)) / 1e8 if "drive_V" in r.meta.get("measurement_config", {}) else 1.0 / 1e8
    print("=" * 70)
    print(f"run {rid} ({side}, n = {n12:+.2f}e12): {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"wall {(t.max()-t.min())/60:.1f} min -> {(t.max()-t.min())/len(B):.2f} s/pt")
    print(f"  T_sample {T.min():.3f}-{T.max():.3f} K; R {R.min():.0f}-{R.max():.0f} Ohm; I_meas {np.median(np.abs(I))*1e9:.3f} nA")
    print(f"  F_L(g=4) = {F_L:.2f} T; full-scale R = {I_FS/np.median(np.abs(I)):.0f} Ohm; max |V|/FS = {np.abs(V).max()/50e-6*100:.1f}%")
    # leakage
    print(f"  |I_tg| max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA, |I_bg| max {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA")

    ax = axes[0, k]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw — {side}, n={n12:+.2f}e12")

    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=I_FS / np.median(np.abs(I)))
        print("  --- sdh_onset ---")
        print("   " + on.summary().replace("\n", "\n   "))
    except SdhOnsetError as e:
        on = None
        print(f"  --- sdh_onset FAILED: {e}")

    # background-subtracted trace over the usable window
    b_lo = on.onset_b if on is not None else 1.0
    b_hi = (on.clip_high_b or B.max()) if on is not None else B.max()
    m = (B >= max(b_lo, 0.3)) & (B <= b_hi)
    cf = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(cf, B[m])
    ax = axes[1, k]
    ax.plot(1 / B[m], dR, lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"bg-subtracted (deg5), B {max(b_lo,0.3):.2f}-{b_hi:.2f} T")

    # FFT, a few cutoffs
    ax = axes[2, k]
    for cut in (max(b_lo, 0.5), 1.0, 2.0, 3.0):
        if cut >= b_hi - 0.5:
            continue
        f, sp = sdh_fft(R[:, None], B, b_range=(cut, b_hi), bg_degree=5, log=False, nfft=2048)
        s = sp[0]
        ax.plot(f, s / s[f > 1].max(), lw=0.9, label=f"cut {cut:.2f} T")
        pk = [(f[i], s[i]) for i in range(2, len(f) - 2)
              if s[i] > s[i - 1] and s[i] > s[i + 1] and s[i] > 0.08 * s[f > 1].max() and f[i] > 1]
        pk.sort(key=lambda x: -x[1])
        print(f"  FFT [{cut:.2f}-{b_hi:.2f} T] dF={1/(1/max(cut,1e-9)-1/b_hi):.2f} T  peaks: " +
              ", ".join(f"{p[0]:.1f}T({p[1]/pk[0][1]:.2f})" for p in pk[:6]))
    ax.axvline(F_L, color="r", ls="--", lw=1, label=f"F_L {F_L:.1f} T")
    ax.axvline(0.72 * F_L, color="g", ls=":", lw=1, label="0.72/0.28 F_L")
    ax.axvline(0.28 * F_L, color="g", ls=":", lw=1)
    ax.set_xlim(0, min(2.2 * F_L, f.max())); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title(f"1/B FFT — run {rid}")

fig.tight_layout()
fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("saved hera_scratch/spot_runs67.png")
