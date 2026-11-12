"""Runs 6/7 sdh-spot-check: raw R(B), background-subtracted oscillations, sdh_onset tones, FFT vs F_L."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency, summarize_run
here = Path(__file__).resolve().parent.parent
out = {}
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = open_run(here / "data" / str(rid)); print(summarize_run(r)); print(r.tags)
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = r.col("sr1_X") / I
    T = r.col("T_sample"); order = np.argsort(B); B, R, T = B[order], R[order], T[order]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n={n12:+.2f}e12 F_L(4-fold)={FL:.2f} T; R(B~0)={np.median(R[B<0.3]) if (B<0.3).any() else R[0]:.1f} Ohm, R max {R.max():.0f} at {B[np.argmax(R)]:.2f} T; T {T.mean():.3f}+-{T.std():.3f} K")
    ax[k, 0].plot(B, R, lw=0.7); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("Rxx (Ohm)"); ax[k, 0].set_title(f"run {rid}: n={n12:+.2f}e12, D=0 raw")
    try:
        o = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(o.summary()); out[rid] = dict(onset_b=float(o.onset_b), tones=[(float(t.freq), float(t.contrast), float(t.onset_b), t.harmonic_of) for t in o.tones])
    except SdhOnsetError as e:
        print("onset failed:", e); o = None
    for j, (blo, lab) in enumerate(((1.5, "1.5-10 T"), (3.0, "3-10 T"))):
        m = B >= blo
        f, spec = sdh_fft(R[m][:, None], B[m], nfft=4096, bg_degree=5, log=False)
        sp = spec[0]; sel = (f > 2) & (f < 80)
        ax[k, 1 + j].plot(f[sel], sp[sel] / sp[sel].max()); ax[k, 1 + j].axvline(FL, color="r", ls="--", label=f"F_L={FL:.1f} T")
        ax[k, 1 + j].axvline(FL / 2, color="g", ls=":", label="F_L/2"); ax[k, 1 + j].set_xlabel("F (T)"); ax[k, 1 + j].set_title(f"FFT {lab}"); ax[k, 1 + j].legend(fontsize=7)
        from scipy.signal import find_peaks
        pk, pr = find_peaks(sp[sel], prominence=0.1 * sp[sel].max())
        print(f"  FFT {lab}: peaks (T, rel) " + ", ".join(f"{f[sel][p]:.1f}:{sp[sel][p]/sp[sel].max():.2f}" for p in pk))
    # oscillatory part vs 1/B for the eye
fig.tight_layout(); fig.savefig(here / "hera_scratch" / "spots_67.png", dpi=110)
fig2, ax2 = plt.subplots(2, 1, figsize=(12, 7))
for k, rid in enumerate((6, 7)):
    r = open_run(here / "data" / str(rid)); B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); B, R = B[o], R[o]; m = B > 1.0
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m]); ax2[k].plot(1 / B[m], R[m] - bg, lw=0.7); ax2[k].set_xlabel("1/B (1/T)"); ax2[k].set_ylabel("dR (Ohm)"); ax2[k].set_title(f"run {rid} oscillatory part (deg-5 bg removed, B>1 T)")
    n12 = 3.2 if rid == 6 else -1.2
    for nu in range(4, 41, 4):
        b = abs(n12) * 1e12 / (nu * 2.418e10)
        if 1 / 10 < 1 / b < 1: ax2[k].axvline(1 / b, color="r" if nu % 8 == 0 else "gray", ls=":", lw=0.6); ax2[k].text(1 / b, ax2[k].get_ylim()[1] * 0.9 if k == 0 else 0, str(nu), fontsize=6)
fig2.tight_layout(); fig2.savefig(here / "hera_scratch" / "spots_67_osc.png", dpi=110)
json.dump(out, open(here / "hera_scratch" / "spots_67.json", "w"), indent=1, default=str)
