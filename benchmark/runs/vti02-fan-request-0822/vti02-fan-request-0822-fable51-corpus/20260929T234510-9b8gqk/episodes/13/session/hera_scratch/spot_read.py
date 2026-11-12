"""Spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, FFT."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency
H_4E = 6.62607015e-34/(4*1.602176634e-19)
out = {}
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(Path("data")/str(rid)); print(summarize_run(r))
    B = r.col("magnet_field"); I = r.col("sr0_X")/(-1e6); V = r.col("sr1_X")/1.0
    R = V/I; T = r.col("T_sample")
    o = np.argsort(B); B, R, T = B[o], R[o], T[o]
    print(f"run {rid}: B {B.min():.3f}-{B.max():.3f} ({len(B)} pts), R {R.min():.1f}-{R.max():.1f} Ohm, T {T.min():.3f}-{T.max():.3f} K, I {np.abs(I).min()*1e9:.2f}-{np.abs(I).max()*1e9:.2f} nA")
    FL = H_4E*abs(n12)*1e16; print(f"  F_L = {FL:.2f} T")
    ax[k,0].plot(B, R, lw=0.7); ax[k,0].set_xlabel("B (T)"); ax[k,0].set_ylabel("Rxx (Ohm)"); ax[k,0].set_title(f"run {rid} raw, n={n12:+.1f}e12")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/10e-9); print(on.summary()); out[rid] = on
        onset = on.onset_b
    except Exception as e:
        print("  sdh_onset:", repr(e)); onset = None
    # FFT windows
    for cut, ls in [(1.5, "-"), (2.5, "--"), (4.0, ":")]:
        try:
            m = B >= cut
            f, spec = sdh_fft(R[m][:, None], B[m], b_range=(cut, B.max()), bg_degree=5)
            ax[k,2].plot(f, spec[0]/spec[0].max(), ls, lw=0.9, label=f"B>{cut}")
        except Exception as e: print("  sdh_fft", cut, repr(e))
    ax[k,2].axvline(FL, color="k", lw=0.8); ax[k,2].set_xlim(0, 1.5*FL); ax[k,2].set_xlabel("F (T)"); ax[k,2].legend(fontsize=7); ax[k,2].set_title("FFT in 1/B (bg deg 5)")
    # bg-subtracted trace vs 1/B
    m = B >= 1.0
    p = np.polyfit(B[m], R[m], 5); dR = R[m]-np.polyval(p, B[m])
    ax[k,1].plot(1/B[m], dR, lw=0.7); ax[k,1].set_xlabel("1/B (1/T)"); ax[k,1].set_ylabel("dRxx (Ohm)"); ax[k,1].set_title("bg-subtracted (deg 5, B>1)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_read.png", dpi=110); print("saved")
