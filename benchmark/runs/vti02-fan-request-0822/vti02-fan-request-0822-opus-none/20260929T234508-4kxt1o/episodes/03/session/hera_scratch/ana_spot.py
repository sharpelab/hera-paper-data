"""SdH spot checks: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
Raw R(B), background-subtracted, FFT in 1/B, onset read. Scratch."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_fft, sdh_onset, SdhOnsetError, GateCalibration,
                           luttinger_frequency)

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
gc = GateCalibration(c_tg=CAL["c_tg"], c_bg=CAL["c_bg"],
                     n_offset=CAL["n_offset"] * 1e16, D_offset=CAL["D_offset"] * 1e9)


def load(rid):
    r = open_run(f"data/{rid}")
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    I = r.col(cur.col) / cur.gain
    V = r.col("sr1_X") / [c.gain for c in ch if c.cid == "sr1"][0]
    B = r.col("magnet_field")
    R = V / I
    o = np.argsort(B)
    return r, B[o], R[o], I[o], r.col("T_sample")[o]


fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for k, (rid, ntag) in enumerate([(6, +3.2), (7, -1.2)]):
    r, B, R, I, T = load(rid)
    nSI = ntag * 1e16
    FL = luttinger_frequency(nSI)
    print(f"\n=== run {rid}: n = {ntag:+.2f}e12, F_L = {FL:.2f} T ===")
    print(f"  rows {len(B)}  B {B.min():.3f}..{B.max():.3f} T  "
          f"T {T.mean():.3f} K ({T.min():.3f}-{T.max():.3f})")
    print(f"  I_bias med {np.median(I)*1e9:.3f} nA (range {I.min()*1e9:.3f}..{I.max()*1e9:.3f})")
    print(f"  R: B=min {R[0]:.1f}  B=max {R[-1]:.1f}  min {R.min():.1f}  max {R.max():.1f} Ohm")
    r_fs = 50e-6 / np.median(np.abs(I))
    print(f"  full scale (50 uV / I) = {r_fs:.0f} Ohm; max/FS = {R.max()/r_fs:.3f}")

    ax = axes[0, k]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid}: raw, n={ntag:+.2f}e12, D=0")

    # background-subtracted, in 1/B
    m = B > 0.8
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    dR = R[m] - bg
    axes[1, k].plot(1 / B[m], dR, lw=0.7)
    axes[1, k].set_xlabel("1/B (1/T)"); axes[1, k].set_ylabel(r"$\Delta R$ ($\Omega$)")
    axes[1, k].set_title(f"run {rid}: poly-5 background removed (B>0.8 T)")
    print(f"  dR rms (B>0.8) = {dR.std():.3f} Ohm; ptp = {np.ptp(dR):.3f}")
    # noise proxy: high-B half rms of a tight local detrend
    hi = B[m] > 5
    print(f"  dR rms (B>5)   = {dR[hi].std():.3f} Ohm")

    f, spec = sdh_fft(R[:, None], B, b_range=(1.0, B.max()), nfft=4096,
                      bg_degree=5, log=False)
    s = spec[0]
    keep = (f > 1) & (f < 3 * max(FL, 15))
    axes[2, k].plot(f[keep], s[keep], lw=0.9)
    for fv, lab, c in [(FL, "F_L (single FS)", "k"),
                       (0.227 * FL, "ABAB light", "tab:red"),
                       (0.773 * FL, "ABAB heavy", "tab:orange")]:
        axes[2, k].axvline(fv, ls="--", lw=0.8, color=c, label=f"{lab} {fv:.1f} T")
    axes[2, k].set_xlabel("F (T)"); axes[2, k].set_ylabel("|FFT|")
    axes[2, k].legend(fontsize=7); axes[2, k].set_title(f"run {rid}: FFT in 1/B, B>1 T")

    top = np.argsort(s[keep])[::-1][:8]
    fk, sk = f[keep], s[keep]
    print("  FFT peaks (T, amp):", ", ".join(f"{fk[i]:.2f}:{sk[i]:.3g}" for i in sorted(top)))

    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        out[rid] = on
    except SdhOnsetError as e:
        print(f"  sdh_onset: FAILED -- {e}")

fig.tight_layout()
fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("\nsaved hera_scratch/spot_runs67.png")
