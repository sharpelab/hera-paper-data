"""SdH spot checks (runs 6, 7): raw R(B), background-removed oscillatory part vs 1/B, FFT in 1/B, sdh_onset read.
Usage: menv python hera_scratch/spot_analysis.py"""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

def load(rid):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B)
    return r, B[o], R[o], I[o], r.col("T_sample")[o]

runs = {6: ("electron n=+3.2e12", 3.2), 7: ("hole n=-1.2e12", -1.2)}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, (lab, n12)) in enumerate(runs.items()):
    r, B, R, I, T = load(rid)
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid} ({lab}) === {len(B)} pts, B {B.min():.2f}..{B.max():.2f} T; R {R.min():.1f}..{R.max():.1f} Ohm; "
          f"I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; T {T.min():.3f}..{T.max():.3f} K; F_L(full n, 4-fold) = {FL:.1f} T")
    ax[0, k].plot(B, R, lw=0.8); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)"); ax[0, k].set_title(f"run {rid} — {lab} — raw")
    # oscillatory part: poly background in B over B >= 1 T
    m = B >= 1.0
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, k].plot(1 / B[m], dR, lw=0.8); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("dRxx (Ohm)"); ax[1, k].set_title("bg-removed (deg-5 in B), B >= 1 T")
    for b_lo in (1.0, 2.0, 3.0):
        try:
            f, spec = sdh_fft(R[:, None], B, b_range=(b_lo, B.max()), nfft=2048, bg_degree=5, log=False)
            sp = spec[0]; sel = f > 2
            pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
            print(f"  FFT window [{b_lo}, {B.max():.1f}] T: top peaks at F = {np.round(np.sort(pk), 1)} T  (dF ~ {1/(1/b_lo - 1/B.max()):.1f} T)")
            if b_lo == 2.0: ax[2, k].plot(f, sp / sp[sel].max(), lw=1, label=f"[{b_lo},{B.max():.0f}] T")
            if b_lo == 1.0: ax[2, k].plot(f, sp / sp[sel].max(), lw=0.7, alpha=0.6, label=f"[{b_lo},{B.max():.0f}] T")
        except Exception as e:
            print(f"  FFT [{b_lo}, ..] failed: {e}")
    ax[2, k].axvline(FL, color="r", ls="--", lw=1, label=f"F_L = {FL:.1f} T (n/4 deg)")
    ax[2, k].axvline(FL / 2, color="orange", ls=":", lw=1, label="F_L/2")
    ax[2, k].set_xlim(0, 60); ax[2, k].set_xlabel("F (T)"); ax[2, k].set_ylabel("FFT amp (norm)"); ax[2, k].legend(fontsize=7)
    try:
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except SdhOnsetError as e:
        print(f"  sdh_onset: {e}")
    # local extrema count in dR above 3 T as a crude tone check
    from scipy.signal import find_peaks
    mm = B[m] >= 3
    pks, _ = find_peaks(dR[mm], prominence=np.std(dR[mm]) * 0.5)
    print(f"  dR maxima above 3 T: {len(pks)}; positions (T): {np.round(B[m][mm][pks], 2)}")
    print(f"  1/B of maxima: {np.round(1/B[m][mm][pks], 4)}; diffs: {np.round(np.diff(1/B[m][mm][pks]), 4)}")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110); print("\nsaved hera_scratch/spot_runs67.png")
