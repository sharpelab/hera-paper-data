"""SdH spot checks run 6 (electron, n=+3.2e12, D=0) and run 7 (hole, n=-1.2e12, D=0): raw R(B), onset, FFT."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency

cal = json.load(open("hera_scratch/cal_run5.json"))
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs(r.col("sr1_X") / ch["sr1"].gain / I)
    o = np.argsort(B); B, R, T = B[o], R[o], r.col("T_sample")[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"=== run {rid}: n={n12:+.1f}e12  F_L={FL:.1f} T  B {B.min():.2f}-{B.max():.2f}  R {R.min():.1f}-{R.max():.1f} Ohm "
          f"R(0)={R[B<0.4].mean():.1f}  R(Bmax)={R[-5:].mean():.1f}  T {T.min():.3f}-{T.max():.3f} K")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw |Rxx| n={n12:+.1f}e12 D=0"); ax[0, j].set_xlabel("B (T)")
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
        out[rid] = dict(onset=on.onset_b, tones=[(t.freq, t.contrast, t.onset_b, t.marginal, t.harmonic_of) for t in on.tones])
    except Exception as e:
        print("onset error:", e); out[rid] = dict(err=str(e))
    for k, (blo, bdeg) in enumerate([(2.0, 5), (4.0, 5)]):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), nfft=4096, bg_degree=bdeg, log=True)
        sp = sp[0]
        m = (f > 1.0) & (f < 3 * FL)
        pk = np.argsort(sp[m])[::-1]
        fm = f[m]; spm = sp[m]
        # local maxima list
        lm = [i for i in range(1, len(spm) - 1) if spm[i] > spm[i - 1] and spm[i] >= spm[i + 1]]
        lm = sorted(lm, key=lambda i: -spm[i])[:6]
        print(f"  FFT b>{blo}: top peaks " + ", ".join(f"{fm[i]:.1f} T ({spm[i]/spm[lm[0]]:.2f})" for i in lm)
              + f"  | F/F_L: " + ", ".join(f"{fm[i]/FL:.2f}" for i in lm))
        ax[1 + k, j].plot(f, sp, lw=0.8); ax[1 + k, j].set_xlim(0, 2.5 * FL)
        for x, c in [(FL, "k"), (FL / 3, "r"), (0.276 * FL, "g"), (0.724 * FL, "g")]:
            ax[1 + k, j].axvline(x, color=c, ls=":", lw=0.8)
        ax[1 + k, j].set_title(f"FFT log R, B {blo}-{B.max():.0f} T (k: F_L, r: F_L/3, g: ABAB 0.28/0.72 F_L)")
        ax[1 + k, j].set_xlabel("F (T)")
    # detrended oscillation vs 1/B for eye
fig.tight_layout(); fig.savefig("hera_scratch/sdh67.png", dpi=90)

# detrended residual plots
fig2, ax2 = plt.subplots(2, 1, figsize=(12, 7))
for j, rid in enumerate([6, 7]):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs(r.col("sr1_X") / ch["sr1"].gain / I); o = np.argsort(B); B, R = B[o], R[o]
    m = B > 1.0
    y = np.log10(R[m]); cf = np.polyfit(B[m], y, 5); res = y - np.polyval(cf, B[m])
    ax2[j].plot(1 / B[m], res, lw=0.7); ax2[j].set_xlabel("1/B (1/T)"); ax2[j].set_title(f"run {rid} log R - poly5(B), B>1 T")
fig2.tight_layout(); fig2.savefig("hera_scratch/sdh67_resid.png", dpi=90)
json.dump(out, open("hera_scratch/sdh67.json", "w"), indent=1, default=str)
