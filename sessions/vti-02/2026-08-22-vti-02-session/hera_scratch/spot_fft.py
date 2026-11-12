"""Interim / final read of a 1D SdH spot check: raw R(B), background-subtracted dR, sdh_onset, sdh_fft vs F_L."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

rid = int(sys.argv[1]); n12 = float(sys.argv[2]); cutoff = float(sys.argv[3]) if len(sys.argv) > 3 else None
r = open_run(f"data/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = (r.col("sr1_X") / ch["sr1"].gain) / I
T = r.col("T_sample")
m = B >= 0.3; B, R = B[m], R[m]
FL = luttinger_frequency(abs(n12) * 1e16)
print(f"run {rid}: {r.rows} rows, B {B.min():.2f}-{B.max():.2f} T, R {R.min():.1f}..{R.max():.1f} Ohm, T {T.min():.3f}-{T.max():.3f} K; F_L({n12:+.2f}e12) = {FL:.1f} T")
# onset
try:
    on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9)
    print(on.summary())
    onset = on.onset_b
except SdhOnsetError as e:
    print("sdh_onset:", e); onset = None
lo = cutoff if cutoff else (max(onset, 1.0) if onset else 1.5)
# FFT (linear R, degree-5 bg in B) for two windows: full above lo, and high-B half
fig, ax = plt.subplots(3, 1, figsize=(10, 10))
ax[0].plot(B, R, lw=0.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("R = X/I (Ohm)"); ax[0].set_title(f"run {rid} raw, n = {n12:+.2f}e12")
sel = B >= lo
cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
ax[1].plot(1 / B[sel], dR, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dR (Ohm), deg-5 bg removed"); ax[1].set_title(f"window B >= {lo:.2f} T")
for (blo, bhi, lab, c) in [(lo, B.max(), "full", "k"), (lo, (lo + B.max()) / 2, "low-B half", "b"), ((lo + B.max()) / 2, B.max(), "high-B half", "r")]:
    try:
        f, spec = sdh_fft(R[:, None], B, b_range=(blo, bhi), bg_degree=5, log=False, nfft=4096)
        s = spec[0]; s = s / s[f > 2].max()
        ax[2].plot(f, s, c, lw=0.8, label=f"{lab} [{blo:.1f},{bhi:.1f}] T, dF={1/(1/blo-1/bhi):.1f}")
        pk = [(f[i], s[i]) for i in range(2, len(f) - 1) if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.15 and f[i] > 2]
        print(f"  FFT {lab} [{blo:.2f},{bhi:.2f}] T (dF {1/(1/blo-1/bhi):.2f} T): peaks " + ", ".join(f"{a:.1f}T({b:.2f})" for a, b in pk[:10]))
    except Exception as e:
        print("  FFT", lab, "failed:", e)
for frac, lab in [(1, "F_L"), (0.724, "0.72 F_L"), (0.276, "0.28 F_L"), (0.5, "F_L/2")]:
    ax[2].axvline(frac * FL, color="gray", ls=":", lw=0.8); ax[2].text(frac * FL, 1.02, lab, fontsize=7, ha="center")
ax[2].set_xlim(0, 1.6 * FL); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm)"); ax[2].legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110); print(f"saved hera_scratch/spot_run{rid}.png")
