"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12) at D=0: raw R(B), onset, FFT vs Luttinger."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency, SdhOnsetError

D = Path(__file__).resolve().parent.parent / "data"
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(D / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"=== run {rid}: n={n12:+.1f}e12, F_L={FL:.1f} T; B {B.min():.3f}-{B.max():.3f} ({len(B)} pts); "
          f"R(B~0)={R[B<0.4].mean():.1f}, R(10T)={R[-5:].mean():.0f} Ohm, Rmax {R.max():.0f}; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; "
          f"T {T.min():.3f}-{T.max():.3f} K; |Itg|max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA")
    ax[0, k].plot(B, R, lw=0.8); ax[0, k].set_title(f"run {rid} raw R(B), n={n12:+.1f}e12, D=0"); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)")
    # background-subtracted in 1/B
    for blo in (1.5, 2.5, 4.0):
        m = B >= blo
        cf = np.polyfit(B[m], np.log10(R[m]), 5); dR = np.log10(R[m]) - np.polyval(cf, B[m])
        if blo == 2.5:
            ax[1, k].plot(1 / B[m], dR, lw=0.8); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("dlog10R (bg deg5)"); ax[1, k].set_title(f"run {rid} residual vs 1/B (B>{blo})")
        f, S = sdh_fft(R[:, None], B, b_range=(blo, B.max()), nfft=4096, bg_degree=5)
        S = S[0]
        sel = f > 2
        pk = np.argsort(S[sel])[::-1]
        fs = f[sel]; Ss = S[sel]
        # local maxima
        lm = [i for i in range(1, len(Ss) - 1) if Ss[i] > Ss[i - 1] and Ss[i] >= Ss[i + 1]]
        lm = sorted(lm, key=lambda i: -Ss[i])[:6]
        print(f"  FFT B>{blo}: peaks " + ", ".join(f"{fs[i]:.1f}T({Ss[i]/Ss[lm[0]]:.2f})" for i in lm) + f"; res dF={1/(1/blo-1/B.max()):.1f} T")
        if blo == 2.5:
            ax[2, k].plot(f, S); ax[2, k].set_xlim(0, 60)
            ax[2, k].axvline(FL, color="r", ls="--", label=f"F_L={FL:.1f}"); ax[2, k].legend(); ax[2, k].set_xlabel("F (T)"); ax[2, k].set_title(f"run {rid} FFT (B>{blo})")
    try:
        on = sdh_onset(R, B, r_full_scale=r.meta.get("instruments", {}) and None)
        print(on.summary())
    except SdhOnsetError as e:
        print("  sdh_onset:", e)
    # oscillation minima positions -> filling factors
    m = B >= 2.0
    cf = np.polyfit(B[m], np.log10(R[m]), 5); dR = np.log10(R[m]) - np.polyval(cf, B[m])
    from scipy.signal import find_peaks
    from scipy.ndimage import gaussian_filter1d
    sm = gaussian_filter1d(dR, 2)
    mins, _ = find_peaks(-sm, prominence=0.3 * np.std(sm))
    Bm = B[m][mins]
    nu = abs(n12) * 1e16 * 6.62607e-34 / 1.602177e-19 / Bm
    print("  minima B: " + ", ".join(f"{b:.2f}" for b in Bm[::-1][:14]))
    print("  -> nu = n h/eB: " + ", ".join(f"{v:.1f}" for v in nu[::-1][:14]))
fig.tight_layout(); fig.savefig(Path(__file__).parent / "sdh67.png", dpi=90)
