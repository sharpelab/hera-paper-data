"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12):
raw R(B), sdh_onset per-tone summary, FFT vs F_L with window/bg stability, PNGs."""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError

DATA = "/home/hera/measurements/zack/20260822-vti-02/data"
OUT = "/home/hera/measurements/zack/20260822-vti-02/hera_scratch"
FL = lambda n12: cst.h / (4 * cst.e) * n12 * 1e16   # T, n in 1e12 cm^-2

def load(rid):
    r = open_run(f"{DATA}/{rid}")
    print(f"===== run {rid} =====\n{summarize_run(r)}\ncols: {r.cols}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / (-1e6); V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); return r, B[o], R[o], I[o]

res = {}
for rid, n12 in [(6, 3.2), (7, -1.2)]:
    r, B, R, I = load(rid)
    fl = FL(n12)
    print(f"n = {n12:+.2f}e12 -> F_L = {fl:.2f} T; I_bias {np.median(I)*1e9:.2f} nA; R(B<0.2) {np.median(R[B<0.2]) if (B<0.2).any() else np.nan:.1f} Ohm; "
          f"R max {R.max():.0f} at B={B[np.argmax(R)]:.2f}; FS 5000 Ohm -> max fs frac {R.max()/5000:.2f}")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9, b_lo=0.3)
            print(on.summary())
            onset_b = on.onset_b
            tones = [(t.freq, t.onset_b, getattr(t, "censored", None), getattr(t, "marginal", None), getattr(t, "harmonic_of", None)) for t in on.tones]
        except SdhOnsetError as e:
            print("SdhOnsetError:", e); onset_b = None; tones = []
        for ww in w: print("  warn:", ww.message)
    res[rid] = dict(n12=n12, FL=fl, onset_b=onset_b, tones=tones)

    # FFT stability: windows x bg degrees
    Bmax = B.max()
    lo0 = onset_b if onset_b else 1.5
    fig, ax = plt.subplots(2, 2, figsize=(13, 8))
    ax[0, 0].plot(B, R, lw=0.7); ax[0, 0].set_xlabel("B (T)"); ax[0, 0].set_ylabel("Rxx (Ohm)"); ax[0, 0].set_title(f"run {rid} raw R, n={n12:+.1f}e12 D=0")
    if onset_b: ax[0, 0].axvline(onset_b, color="r", ls="--", lw=0.8, label=f"onset {onset_b:.2f} T"); ax[0, 0].legend()
    # bg-subtracted vs 1/B
    m = B >= lo0
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[0, 1].plot(1 / B[m], dR, lw=0.7); ax[0, 1].set_xlabel("1/B (1/T)"); ax[0, 1].set_ylabel("dR (Ohm), deg-5 bg in B"); ax[0, 1].set_title("background-subtracted")
    windows = [(lo0, Bmax), (lo0, 0.5 * (lo0 + Bmax) + 0.5), (max(lo0, 0.5 * (lo0 + Bmax) - 0.5), Bmax), (lo0 + 0.5, Bmax)]
    peaks_all = []
    for (a, b), c in zip(windows, ["k", "C0", "C1", "C2"]):
        for deg, ls in [(5, "-"), (3, ":")]:
            f, sp = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=deg, log=False, nfft=2048)
            s = sp[0]; s = s / s[f > 2].max()
            ax[1, 0].plot(f, s, color=c, ls=ls, lw=0.9, label=f"[{a:.1f},{b:.1f}] T deg{deg}")
            sel = (f > 2) & (f < 2.2 * fl)
            pk, pr = find_peaks(s[sel], prominence=0.08)
            fp = f[sel][pk]; ap = s[sel][pk]
            dF = 1 / (1 / a - 1 / b)
            peaks_all.append(((a, b, deg), [(round(x, 2), round(y, 2)) for x, y in zip(fp, ap)], round(dF, 2)))
    ax[1, 0].axvline(fl, color="m", ls="--", label=f"F_L {fl:.1f} T"); ax[1, 0].axvline(0.72 * fl, color="g", ls=":", label="0.72 F_L"); ax[1, 0].axvline(0.28 * fl, color="g", ls=":", label="0.28 F_L")
    ax[1, 0].set_xlim(0, 2.2 * fl); ax[1, 0].set_xlabel("F (T)"); ax[1, 0].set_ylabel("|FFT| (norm)"); ax[1, 0].legend(fontsize=6); ax[1, 0].set_title("FFT in 1/B — window/bg stability")
    # LL index plot: minima of dR vs 1/B
    mins, _ = find_peaks(-dR, prominence=0.15 * np.std(dR))
    ax[1, 1].plot(1 / B[m][mins], np.arange(len(mins)), "o-", ms=3); ax[1, 1].set_xlabel("1/B at dR minima"); ax[1, 1].set_ylabel("index"); ax[1, 1].set_title("minima ladder (slope = F if single tone)")
    if len(mins) > 3:
        x = 1 / B[m][mins]; y = np.arange(len(mins)); p = np.polyfit(x, y, 1)
        ax[1, 1].plot(x, np.polyval(p, x), "r--", lw=0.8, label=f"slope {abs(p[0]):.1f} T"); ax[1, 1].legend()
        print(f"minima ladder: {len(mins)} minima, slope {abs(p[0]):.2f} T (F_L {fl:.2f}); minima at B = {np.round(B[m][mins], 2).tolist()}")
    fig.tight_layout(); fig.savefig(f"{OUT}/spot_run{rid}.png", dpi=110); plt.close(fig)
    for k, pks, dF in peaks_all:
        print(f"  FFT window {k}: dF={dF} T; peaks (F, rel amp): {pks}")
    res[rid]["fft_peaks"] = [(list(k), pks, dF) for k, pks, dF in peaks_all]

json.dump(res, open(f"{OUT}/spot_results.json", "w"), indent=1, default=str)
