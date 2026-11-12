"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, 1/B FFT."""
import sys, json, warnings
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
import inspect
print("luttinger_frequency", inspect.signature(luttinger_frequency))
out = {}
fig, axs = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(Path("data") / str(rid)); print("="*30, rid); print(summarize_run(r)); print("cols", r.cols, "interrupted", r.interrupted)
    B = r.col("magnet_field"); I = r.col("sr0_X") / (-1e6); V = r.col("sr1_X")
    R = V / I; Rb = V / 10e-9
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], r.col("T_sample")[o]
    print(f"B {B.min():.3f}..{B.max():.3f} N={len(B)}; I {I.min()*1e9:.3f}..{I.max()*1e9:.3f} nA; R {R.min():.1f}..{R.max():.1f} Ohm; T {T.min():.3f}..{T.max():.3f}")
    FL = 4.1357e-15 / 4 * abs(n12) * 1e16  # (h/4e) n
    print(f"F_L = {FL:.2f} T")
    # dynamic range: sens 50 uV / 10 nA = 5 kOhm
    print(f"max |R|/FS = {np.abs(R).max()/5000:.3f}")
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_title(f"run {rid}: n={n12:+.1f}e12, D=0 — raw Rxx (sr1/sr0)"); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    try:
        on = sdh_onset(R, B, r_full_scale=5000.0)
        print(on.summary())
        out[rid] = dict(onset_b=float(on.onset_b), clip_high_b=None if on.clip_high_b is None else float(on.clip_high_b),
                        tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                    harmonic_of=t.harmonic_of if not hasattr(t.harmonic_of,'__float__') else float(t.harmonic_of)) for t in on.tones])
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = None; out[rid] = dict(error=str(e))
    # background-subtracted view + FFT for a few windows
    for lo in ([1.5, 2.5, 4.0] if onset is None else [max(onset, 0.8), max(onset, 0.8) + 1.0, 4.0]):
        for deg in (3, 5):
            m = (B >= lo) & (B <= B.max())
            try:
                f, s = sdh_fft(R[:, None], B, b_range=(lo, float(B.max())), bg_degree=deg, log=False, nfft=2048)
            except Exception as e:
                print("fft fail", lo, deg, e); continue
            s = s[0]; pk = np.argsort(s)[::-1]
            # local maxima
            from scipy.signal import find_peaks
            p, _ = find_peaks(s, prominence=0.05 * s.max()); p = p[np.argsort(s[p])[::-1]][:8]
            dF = 1 / (1 / lo - 1 / B.max())
            print(f"  FFT window [{lo:.2f},{B.max():.1f}] deg{deg}: dF={dF:.2f} T; peaks (T, rel): " + ", ".join(f"{f[i]:.1f}({s[i]/s.max():.2f})" for i in p))
            if deg == 5 and lo == (4.0):
                axs[2, j].plot(f, s / s.max(), label=f"[{lo:.1f},{B.max():.0f}] deg{deg}")
            if deg == 5 and lo < 4.0:
                axs[2, j].plot(f, s / s.max(), label=f"[{lo:.1f},{B.max():.0f}] deg{deg}")
    # low/high half split for the dominant window
    if onset is not None:
        lo = max(onset, 0.8); mid = 2 / (1 / lo + 1 / B.max())
        for (a, b) in [(lo, mid), (mid, B.max())]:
            f, s = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=3, log=False, nfft=2048); s = s[0]
            from scipy.signal import find_peaks
            p, _ = find_peaks(s, prominence=0.05 * s.max()); p = p[np.argsort(s[p])[::-1]][:6]
            print(f"  half [{a:.2f},{b:.2f}] dF={1/(1/a-1/b):.2f}: " + ", ".join(f"{f[i]:.1f}({s[i]/s.max():.2f})" for i in p))
    axs[2, j].axvline(FL, color="k", ls="--", label=f"F_L={FL:.1f} T"); axs[2, j].set_xlim(0, 2.2 * FL); axs[2, j].set_xlabel("F (T)"); axs[2, j].legend(fontsize=7); axs[2, j].set_title("1/B FFT")
    # bg-subtracted dR vs 1/B
    m = B >= 1.0; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    axs[1, j].plot(1 / B[m], dR, lw=0.7); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_ylabel("dRxx (Ohm), deg-5 bg in B"); axs[1, j].set_title("background-subtracted vs 1/B (B>1 T)")
    # filling factors at minima of R
    from scipy.signal import find_peaks
    mm = B >= 3.0; p, _ = find_peaks(-R[mm], prominence=20)
    nu = abs(n12) * 1e16 * 4.1357e-15 / B[mm][p]
    print("  Rxx minima B (T) / nu:", ", ".join(f"{b:.2f}/{v:.1f}" for b, v in zip(B[mm][p], nu)))
fig.tight_layout(); fig.savefig("hera_scratch/spot_read.png", dpi=110)
json.dump(out, open("hera_scratch/spot_read.json", "w"), indent=1, default=str)
