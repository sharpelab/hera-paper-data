"""Runs 6 / 7 — SdH spot checks: raw R(B), background-subtracted trace, FFT in 1/B, sdh_onset."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset, luttinger_frequency

SPOTS = {6: dict(n=3.2, label="electron n=+3.2e12, D=0"), 7: dict(n=-1.2, label="hole n=-1.2e12, D=0")}
fig, ax = plt.subplots(3, 2, figsize=(12, 10))
out = {}
for j, (rid, sp) in enumerate(SPOTS.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    R = r.col("sr1_X") / 1.0 / I
    T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    fL = float(luttinger_frequency(abs(sp["n"]) * 1e16))
    print(f"run {rid} {sp['label']}: B {B.min():.2f}..{B.max():.2f} T, R(0.3T)={R[np.argmin(abs(B-0.3))]:.1f}, R(Bmax)={R[-1]:.1f} Ohm, "
          f"R range {R.min():.1f}..{R.max():.1f}, I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, T {T.min():.3f}..{T.max():.3f} K, F_L={fL:.1f} T")
    print(f"   sr1 X max {r.col('sr1_X').max()*1e6:.2f} uV (sens 50 uV) ; gate I tg {np.median(r.col('k_2400_tg_curr'))*1e12:.0f} pA bg {np.median(r.col('k_2400_bg_curr'))*1e12:.0f} pA")
    ax[0, j].plot(B, R, lw=.8); ax[0, j].set(title=f"run {rid}: {sp['label']} (raw)", xlabel="B (T)", ylabel="Rxx (Ohm)")
    # background-subtracted in B, above 1.5 T
    for b_lo in (1.0, 2.0, 3.0):
        m = B >= b_lo
        p = np.polyfit(B[m], np.log10(R[m]), 5)
        res = np.log10(R[m]) - np.polyval(p, B[m])
        if b_lo == 2.0:
            ax[1, j].plot(1 / B[m], res, lw=.8); ax[1, j].set(xlabel="1/B (1/T)", ylabel="dlog10 R", title="bg-sub (deg5 in B), B>2 T")
        f, sp_ = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()), nfft=4096, bg_degree=5)
        sp_ = sp_[0]
        ax[2, j].plot(f, sp_ / sp_[f > 3].max(), lw=.8, label=f"B>{b_lo}")
        pk = [(f[k], sp_[k]) for k in range(1, len(f) - 1) if sp_[k] > sp_[k - 1] and sp_[k] > sp_[k + 1] and f[k] > 3 and f[k] < 120]
        pk = sorted(pk, key=lambda t: -t[1])[:6]
        print(f"   FFT B>{b_lo}: top peaks " + ", ".join(f"{a:.1f}T({b/pk[0][1]:.2f})" for a, b in pk))
    ax[2, j].axvline(fL, color="k", ls=":", label=f"F_L={fL:.1f}")
    ax[2, j].set(xlim=(0, 80), xlabel="F (T)", ylabel="|FFT| norm", title="FFT in 1/B"); ax[2, j].legend(fontsize=7)
    try:
        so = sdh_onset(R, B, b_lo=0.3, r_full_scale=50e-6 / 1e-8)
        print(so.summary())
        out[rid] = so
    except Exception as e:
        print("   sdh_onset:", type(e).__name__, e)
fig.tight_layout(); fig.savefig("hera_scratch/spots_run6_7.png", dpi=110)
