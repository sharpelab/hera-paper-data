"""Scratch: raw + SdH read of the two spot checks (runs 6 e-side n=+3.2e12, 7 h-side n=-1.2e12)."""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, luttinger_frequency

OUT = "hera_scratch"
res = {}
for rid, n12, sens in ((6, 3.2, 50e-6), (7, -1.2, 50e-6)):
    r = open_run(f"data/{rid}")
    print(f"\n===== run {rid}  cols={r.cols}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col(cur.col) / cur.gain
    v = [c for c in chans if c.cid == "sr1"][0]
    R = (r.col(v.col) / v.gain) / I
    B = r.col("magnet_field")
    T = r.col("T_sample")
    order = np.argsort(B); B, R, I, T = B[order], R[order], I[order], T[order]
    Ib = np.median(np.abs(I))
    print(f"I_bias med {Ib*1e9:.3f} nA; T {T.min():.3f}-{T.max():.3f} K; R min {R.min():.1f} max {R.max():.1f} Ohm; "
          f"R(B<0.2) mean {R[B<0.2].mean():.1f}")
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"F_L(full density, 4-fold) = {FL:.2f} T; F_L/2 = {FL/2:.2f}")
    # onset
    try:
        on = sdh_onset(np.abs(R), B, b_lo=0.5, r_full_scale=sens / Ib)
        print(on.summary())
        onset = on.onset_b
    except Exception as e:
        print("sdh_onset failed:", e); onset = 2.0
    # FFTs on a few windows
    fig, ax = plt.subplots(3, 1, figsize=(9, 11))
    ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)"); ax[0].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 (raw)")
    ax[1].plot(1 / B[B > 0.8], R[B > 0.8], lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("Rxx (Ohm)")
    for blo, bhi, c in ((max(onset, 1.0), 10.0, "k"), (2.0, 10.0, "C0"), (4.0, 10.0, "C1"), (1.5, 6.0, "C2")):
        m = (B >= blo) & (B <= bhi)
        f, sp = sdh_fft(R[m][:, None], B[m], nfft=4096, bg_degree=5, log=False)
        sp = sp[0]; sp /= sp[f > 2].max()
        ax[2].plot(f, sp, c, lw=0.8, label=f"{blo:.1f}-{bhi:.0f} T")
        sel = (f > 2) & (f < 80)
        from scipy.signal import find_peaks
        pk, pr = find_peaks(sp[sel], prominence=0.05)
        fs = f[sel][pk]; hs = sp[sel][pk]
        top = np.argsort(hs)[::-1][:8]
        print(f"FFT {blo:.1f}-{bhi:.0f} T peaks (T): " + ", ".join(f"{fs[i]:.1f}({hs[i]:.2f})" for i in sorted(top, key=lambda i: fs[i])))
    for k, lab in ((1, "F_L"), (0.5, "F_L/2"), (0.25, "F_L/4")):
        ax[2].axvline(FL * k, color="r", ls=":", lw=0.8); ax[2].text(FL * k, 0.9, lab, color="r", fontsize=7)
    ax[2].set_xlim(0, 80); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm)"); ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"{OUT}/spot_run{rid}.png", dpi=110)
    res[rid] = dict(n12=n12, FL=float(FL), onset=float(onset), Rmax=float(R.max()), Rmin=float(R.min()))
json.dump(res, open(f"{OUT}/spot_summary.json", "w"), indent=1)
