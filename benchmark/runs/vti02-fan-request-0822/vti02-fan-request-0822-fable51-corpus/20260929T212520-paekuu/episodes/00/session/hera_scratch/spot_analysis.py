"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12):
raw trace, bg-subtracted dR, sdh_onset summary, FFT vs F_L + model tones, B-window split,
bg_degree stability. Scratch: prints + PNGs."""
import sys, json, warnings
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, summarize_run

I_BIAS = 10e-9
FS = 50e-6 / I_BIAS          # 5 kOhm full scale (sr1 50 uV)
h_over_4e = 4.1357e-15 / 4 * 1e16  # T per 1e12 cm^-2 -> F_L = 10.34 T per 1e12

runs = {6: dict(n=+3.2, side="electron"), 7: dict(n=-1.2, side="hole")}
out = {}
for rid, info in runs.items():
    r = open_run(f"data/{rid}")
    print("=" * 78); print(summarize_run(r))
    B = np.asarray(r.col("magnet_field")); X = np.asarray(r.col("sr1_X")); I = np.asarray(r.col("sr0_X")) / (-1e6)
    T = np.asarray(r.col("T_sample"))
    R = X / I                                     # signed
    o = np.argsort(B); B, R, T, I = B[o], R[o], T[o], I[o]
    print(f"run {rid} {info['side']}: n={info['n']:+.2f}e12 F_L={h_over_4e*abs(info['n']):.1f} T; B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts; "
          f"T {T.min():.3f}-{T.max():.3f} K; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.1f}..{R.max():.1f} Ohm (FS {FS:.0f})")
    FL = h_over_4e * abs(info["n"])
    # onset
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, b_lo=0.3, r_full_scale=FS)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        onset = float(on.onset_b)
        tones = [(float(t.freq), float(t.onset_b), bool(getattr(t, 'censored', False)), bool(getattr(t, 'marginal', False))) for t in on.tones]
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = None; tones = []
    out[rid] = dict(onset=onset, tones=tones, FL=FL)

    # FFT windows
    Bmax = B.max()
    fig, ax = plt.subplots(2, 2, figsize=(13, 8))
    ax[0, 0].plot(B, R, lw=0.7); ax[0, 0].set_xlabel("B (T)"); ax[0, 0].set_ylabel("R = sr1_X/I (Ohm)"); ax[0, 0].set_title(f"run {rid} {info['side']} n={info['n']:+.1f}e12 raw")
    # bg-subtracted
    lo = onset if onset else 1.0
    for cut, c in [(lo, "k"), (max(lo, 2.0), "C1"), (max(lo, 3.0), "C2")]:
        m = (B >= cut)
        p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
        ax[0, 1].plot(1 / B[m], dR, lw=0.7, color=c, label=f"cut {cut:.2f} T")
    ax[0, 1].set_xlabel("1/B (1/T)"); ax[0, 1].set_ylabel("dR (Ohm), deg-5 bg in B"); ax[0, 1].legend(fontsize=7); ax[0, 1].set_title("background-subtracted")
    for cut, c in [(lo, "k"), (max(lo, 2.0), "C1"), (max(lo, 3.0), "C2")]:
        f, s = sdh_fft(R[:, None], B, b_range=(cut, Bmax), bg_degree=5, log=False, nfft=2048)
        ax[1, 0].plot(f, s[0] / s[0][f > 2].max(), color=c, lw=0.9, label=f"cut {cut:.2f}")
    for bgd, ls in [(3, ":"), (7, "--")]:
        f, s = sdh_fft(R[:, None], B, b_range=(lo, Bmax), bg_degree=bgd, log=False, nfft=2048)
        ax[1, 0].plot(f, s[0] / s[0][f > 2].max(), color="0.5", ls=ls, lw=0.8, label=f"bg_deg {bgd}")
    ax[1, 0].axvline(FL, color="r", ls="--", label=f"F_L {FL:.1f} T"); ax[1, 0].axvspan(0.85 * FL, 1.15 * FL, color="r", alpha=0.08)
    ax[1, 0].set_xlim(0, 2.2 * FL); ax[1, 0].set_xlabel("F (T)"); ax[1, 0].set_ylabel("|FFT| (norm)"); ax[1, 0].legend(fontsize=7); ax[1, 0].set_title("FFT in 1/B — window/bg stability")
    # B-window split
    mid = 2 / (1 / lo + 1 / Bmax)   # split at the 1/B midpoint
    for (a, b), c in [((lo, mid), "C0"), ((mid, Bmax), "C3"), ((lo, Bmax), "k")]:
        try:
            f, s = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False, nfft=2048)
            ax[1, 1].plot(f, s[0] / s[0][f > 2].max(), color=c, lw=0.9, label=f"{a:.2f}-{b:.2f} T")
        except Exception as e: print("split fft fail", a, b, e)
    ax[1, 1].axvline(FL, color="r", ls="--"); ax[1, 1].set_xlim(0, 2.2 * FL); ax[1, 1].set_xlabel("F (T)"); ax[1, 1].legend(fontsize=7); ax[1, 1].set_title("B-window split (1/B midpoint)")
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110)
    # peak list on the full window
    f, s = sdh_fft(R[:, None], B, b_range=(lo, Bmax), bg_degree=5, log=False, nfft=4096)
    from scipy.signal import find_peaks
    sp = s[0]; sel = f > 1.5
    pk, pr = find_peaks(sp[sel], prominence=0.08 * sp[sel].max())
    fpk = f[sel][pk]; apk = sp[sel][pk]
    order = np.argsort(-apk)[:8]
    print(f"  FFT peaks (cut {lo:.2f}-{Bmax:.1f} T, deg5): " + ", ".join(f"{fpk[i]:.2f} T ({apk[i]/apk.max():.2f}, f/F_L={fpk[i]/FL:.2f})" for i in order))
    dF = 1 / (1 / lo - 1 / Bmax); print(f"  record resolution dF = {dF:.2f} T (onset {lo:.2f} -> {Bmax:.1f} T); F_L/dF = {FL/dF:.1f}")
    out[rid]["peaks"] = [(float(fpk[i]), float(apk[i] / apk.max())) for i in order]
json.dump(out, open("hera_scratch/spot_read.json", "w"), indent=1)
print(json.dumps(out, indent=1))
