"""Runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12) sdh-spot-check: raw R(B), onset, FFT, Luttinger closure."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency

out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    fs = 50e-6 / 10e-9
    print(f"\n=== run {rid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T ===")
    print(f"R(B~0) {R[:3].mean():.0f} Ohm, R max {R.max():.0f} at B {B[R.argmax()]:.2f} T (FS {fs:.0f}), R(10T) {R[-3:].mean():.0f}")
    print(f"I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K; I_tg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA; I_bg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA")
    dt = np.diff(np.sort(r.col("time")))
    print(f"time/pt median {np.median(dt):.2f} s; total {(r.col('time').max()-r.col('time').min())/60:.1f} min")
    try:
        so = sdh_onset(R, B, b_lo=0.5, r_full_scale=fs)
        print(so.summary())
        out[rid] = so
    except Exception as e:
        print("sdh_onset failed:", e)
    a = ax[0, k]; a.plot(B, R, lw=0.7); a.set_xlabel("B (T)"); a.set_ylabel("|Rxx| (Ohm)"); a.set_title(f"run {rid} raw, n={n12:+.1f}e12")
    # FFT over two windows
    for j, (lo, hi) in enumerate([(2.0, 10.0), (4.0, 10.0)]):
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=4096, bg_degree=5)
        S = S[0]
        m = f < 3 * FL
        pk = np.argsort(S[m])[::-1]
        from scipy.signal import find_peaks
        p, _ = find_peaks(S[m], prominence=0.08 * S[m].max())
        top = sorted(p, key=lambda i: -S[m][i])[:6]
        print(f"FFT {lo}-{hi} T: peaks " + ", ".join(f"{f[m][i]:.1f} T ({S[m][i]/S[m].max():.2f})" for i in sorted(top)) + f"   [F/F_L: " + ", ".join(f"{f[m][i]/FL:.3f}" for i in sorted(top)) + "]")
        ax[1 + j, k].plot(f[m], S[m]); ax[1 + j, k].axvline(FL, color="r", ls="--", lw=0.8, label="F_L")
        ax[1 + j, k].set_xlabel("F (T)"); ax[1 + j, k].set_title(f"FFT log R, {lo}-{hi} T"); ax[1 + j, k].legend()
fig.tight_layout(); fig.savefig("hera_scratch/sdh67.png", dpi=90)

# background-subtracted vs 1/B
fig, ax = plt.subplots(2, 1, figsize=(12, 7))
for k, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))
    o = np.argsort(B); B, R = B[o], R[o]; m = B > 1.0
    lr = np.log10(R[m]); bg = np.polyval(np.polyfit(B[m], lr, 5), B[m])
    ax[k].plot(1 / B[m], lr - bg, lw=0.7); ax[k].set_xlabel("1/B (1/T)"); ax[k].set_ylabel("dlog R"); ax[k].set_title(f"run {rid} background-subtracted")
fig.tight_layout(); fig.savefig("hera_scratch/sdh67_invB.png", dpi=90)
