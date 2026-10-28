"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), both D = 0 (run-5 cal).
Raw R(B), noise floor, minima list, sdh_onset + sdh_fft, and the LL-index (1/B vs index) check of the density scale."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency
import scipy.constants as cst

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
runs = {6: dict(n=3.2, side="electron"), 7: dict(n=-1.2, side="hole")}
out = {}
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, info) in enumerate(runs.items()):
    r = open_run(Path("data") / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    Rs = (r.col("sr1_X") / ch["sr1"].gain) / I
    T = r.col("T_sample")
    o = np.argsort(B); B, Rs, T, I = B[o], Rs[o], T[o], I[o]
    R = np.abs(Rs)
    sens = r.meta["instruments"].get("sr1", {}).get("sensitivity") if isinstance(r.meta.get("instruments"), dict) else None
    # noise floor: residual after Savitzky-Golay smoothing in the low-B smooth window
    lo = (B > 0.3) & (B < 1.5)
    res = Rs[lo] - savgol_filter(Rs[lo], 11, 3)
    noise = np.std(res)
    n_SI = info["n"] * 1e16
    F_L = float(luttinger_frequency(n_SI))
    print(f"\n=== run {rid} ({info['side']}, n = {info['n']:+.2f}e12, D = 0): {len(B)} pts, B {B.min():.2f}..{B.max():.2f} T, "
          f"T {T.min():.3f}-{T.max():.3f} K, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA")
    print(f"R(B=0.3) = {R[np.argmin(abs(B-0.3))]:.0f} Ohm; R max {R.max():.0f} at {B[np.argmax(R)]:.2f} T; min signed R {Rs.min():.1f} at {B[np.argmin(Rs)]:.2f} T; "
          f"noise (0.3-1.5 T, SG residual) {noise:.2f} Ohm; F_L(g=4) = {F_L:.1f} T (n h/e = {4*F_L:.1f} T)")
    # minima (on smoothed |R|) above 1.5 T
    sm = savgol_filter(R, 7, 2)
    sel = B > 1.5
    mins, _ = find_peaks(-sm[sel], prominence=8)
    Bm = B[sel][mins]; Rm = sm[sel][mins]
    print("minima (B, R, nu if n as calibrated):")
    for b, rm in zip(Bm, Rm):
        print(f"   {b:6.3f} T  R={rm:7.1f}  nu(n_cal)={4*F_L/b:6.2f}")
    # onset
    try:
        on = sdh_onset(R, B, b_lo=0.3, r_full_scale=(sens / 10e-9) if sens else None)
        print(on.summary())
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print("sdh_onset failed:", e); onset_b = None
    # FFT windows
    for (b0, b1) in [(1.5, 10.0), (2.0, 6.0), (1.5, 4.0)]:
        f, sp = sdh_fft(R[:, None], B, b_range=(b0, b1), nfft=4096, bg_degree=5, log=False)
        sp = sp[0]; m = f > 2.0
        pk, _ = find_peaks(sp[m], prominence=0.1 * sp[m].max())
        top = sorted(zip(sp[m][pk], f[m][pk]), reverse=True)[:6]
        print(f"FFT {b0}-{b1} T (|R|, lin): peaks F[T] (rel amp): " + ", ".join(f"{ff:.1f} ({a/top[0][0]:.2f})" for a, ff in top) if top else "no peaks")
    f, sp = sdh_fft(R[:, None], B, b_range=(1.5, 10.0), nfft=4096, bg_degree=5, log=False); sp = sp[0]
    out[rid] = dict(B=B.tolist(), R=R.tolist(), minima=list(zip(Bm.tolist(), Rm.tolist())), F_L=F_L, noise=noise, onset=onset_b)
    ax = axes[0, j]; ax.plot(B, Rs, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx signed (Ohm)")
    ax.set_title(f"run {rid} {info['side']} n={info['n']:+.1f}e12 D=0  raw R(B)"); ax.axhline(0, color="k", lw=0.5)
    for b in Bm: ax.axvline(b, color="r", lw=0.4, alpha=0.5)
    ax = axes[1, j]; sel = B > 1.0; ax.plot(1 / B[sel], R[sel], lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("|Rxx| (Ohm)")
    ax.set_title("vs 1/B (B > 1 T)")
    ax = axes[2, j]; ax.plot(f, sp / sp[f > 2].max()); ax.set_xlim(0, 150); ax.set_xlabel("F (T)"); ax.set_ylabel("FFT |R| 1.5-10 T (norm)")
    ax.axvline(F_L, color="g", ls="--", label=f"F_L(g=4)={F_L:.1f} T"); ax.axvline(2 * F_L, color="g", ls=":", label="2 F_L")
    ax.legend(); ax.set_title("SdH FFT in 1/B, 1.5-10 T, deg-5 B-space bg")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spot_runs6_7.png", dpi=110)
json.dump(out, open("hera_scratch/sdh_spot_runs6_7.json", "w"))
print("\nsaved hera_scratch/sdh_spot_runs6_7.png")
