"""Runs 6-7 (sdh-spot-check): raw R(B), detrended 1/B, FFT vs F_L, sdh_onset tones, minima -> filling factors."""
from hera.analysis import resolve_channels, sdh_onset
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelmin

spots = {6: +3.2, 7: -1.2}   # 1e12 cm^-2 (run-5 calibration, scale = geometry prior)
traces = {}
for rid, n12 in spots.items():
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I); T = r.col("T_sample")
    o = np.argsort(B); traces[rid] = (B[o], R[o], I[o], T[o], n12)
    print(f"run {rid}: n = {n12:+.1f}e12, {len(B)} pts, B {B.min():.2f}..{B.max():.2f} T (median step {np.median(np.abs(np.diff(B)))*1e3:.0f} mT), "
          f"R {R.min():.0f}..{R.max():.0f} Ohm (fs max {R.max()/5000:.2f}), I_drain {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, T {T.min():.3f}..{T.max():.3f} K, interrupted {r.interrupted}")

# (1) raw
fig, ax = plt.subplots(2, 2, figsize=(13, 7.5))
for k, rid in enumerate(spots):
    B, R, I, T, n12 = traces[rid]
    ax[k, 0].plot(B, R, lw=0.8); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[k, 0].set_title(f"run {rid} raw: n = {n12:+.1f}e12, D = 0, T = {T.mean():.2f} K")
    m = B > 1; ax[k, 1].plot(1 / B[m], R[m], lw=0.8); ax[k, 1].set_xlabel("1/B (1/T)"); ax[k, 1].set_ylabel("|Rxx| (Ohm)"); ax[k, 1].set_title(f"run {rid} raw vs 1/B (B > 1 T)")
fig.tight_layout(); plt.show()

# (2) analysis: detrended 1/B trace + FFT vs F_L, sdh_onset tone table, minima -> nu
fig, ax = plt.subplots(2, 2, figsize=(13, 7.5))
for k, rid in enumerate(spots):
    B, R, I, T, n12 = traces[rid]
    FL = luttinger_frequency(abs(n12) * 1e16)
    m = B >= 1.0; bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[k, 0].plot(1 / B[m], R[m] - bg, lw=0.7); ax[k, 0].set_xlabel("1/B (1/T)"); ax[k, 0].set_ylabel("dR (Ohm)"); ax[k, 0].set_title(f"run {rid} detrended (poly5 in B), B > 1 T")
    for lo in (1.0, 2.0, 4.0):
        mm = (B >= lo) & (B <= 10.0)
        f, sp = sdh_fft(R[mm][:, None], B[mm], nfft=2048, bg_degree=5, log=False)
        ax[k, 1].plot(f, sp[0] / sp[0][f > 2].max(), label=f"{lo:.0f}-10 T (1/B res {1/(1/lo-0.1):.1f} T)", alpha=0.8)
    ax[k, 1].axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L(4-fold, n={n12:+.1f}) = {FL:.1f} T"); ax[k, 1].axvline(FL / 2, color="gray", ls=":", lw=0.8)
    ax[k, 1].set_xlim(0, 60); ax[k, 1].set_xlabel("SdH frequency (T)"); ax[k, 1].set_ylabel("norm. FFT amp"); ax[k, 1].legend(fontsize=7); ax[k, 1].set_title(f"run {rid} FFT windows")
    print(f"\n--- run {rid}: F_L = {FL:.1f} T (F_L/2 = {FL/2:.1f}); n h/e = {abs(n12)*41.357:.1f} T ---")
    try:
        print(sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9).summary())
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e)
    Rs = gaussian_filter1d(R, 2 if rid == 6 else 1.5); mm = B > (2.5 if rid == 6 else 1.0)
    idx = argrelmin(Rs[mm], order=15 if rid == 6 else 8)[0]
    nhe = abs(n12) * 41.357
    print("minima:  " + "  ".join(f"{B[mm][i]:.2f}T({Rs[mm][i]:.0f}Ω) ν={nhe/B[mm][i]:.1f}|{1.087*nhe/B[mm][i]:.1f}" for i in idx))
fig.tight_layout(); plt.show()
