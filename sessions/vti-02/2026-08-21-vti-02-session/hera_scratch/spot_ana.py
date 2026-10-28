"""SdH spot-check read: raw R(B), onset (sdh_onset), FFT in 1/B (sdh_fft) vs F_L and the model tones.
Usage: menv python hera_scratch/spot_ana.py <run_id> <n_e12> [cutoff_T]
"""
import sys, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

DATA = Path(__file__).resolve().parents[1] / "data"
rid = int(sys.argv[1]); n12 = float(sys.argv[2]); cutoff = float(sys.argv[3]) if len(sys.argv) > 3 else None
r = open_run(DATA / str(rid))
mc = r.meta["measurement_config"]
ib = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"] / mc["bias_resistor"]
B = r.col("magnet_field"); I = r.col("sr0_X") / float(mc["sr0_gain"]); R = r.col("sr1_X") / I
T = r.col("T_sample")
print(f"run {rid}: {r.rows} pts, B {B.min():.3f}..{B.max():.3f} T, complete={r.complete} interrupted={r.interrupted}")
print(f"R_xx: {R.min():.1f}..{R.max():.1f} Ohm (B=0: {R[np.argmin(np.abs(B))]:.1f}); I_drain {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; T {T.min():.3f}..{T.max():.3f} K")
FL = luttinger_frequency(n12 * 1e16)
print(f"F_L(n={n12:+.2f}e12) = {FL:.1f} T")

fig, axs = plt.subplots(2, 2, figsize=(14, 9))
ax = axs[0, 0]; ax.plot(B, R, lw=0.8); ax.set_xlabel("B [T]"); ax.set_ylabel("R_xx [Ohm]"); ax.set_title(f"run {rid} raw R_xx(B), n={n12:+.2f}e12")
ax = axs[0, 1]; ax.plot(B, I * 1e9, lw=0.6); ax.set_xlabel("B [T]"); ax.set_ylabel("I_drain [nA]")
ax2 = ax.twinx(); ax2.plot(B, T, "r", lw=0.6); ax2.set_ylabel("T_sample [K]", color="r")

# onset
m = B > 0.2
try:
    on = sdh_onset(R[m], B[m], b_lo=0.3)
    print(on.summary())
    b_on = on.onset_b
except SdhOnsetError as ex:
    print("SdhOnsetError:", ex); on = None; b_on = None

# background-subtracted trace (degree-5 poly in B) for the eye
lo = cutoff if cutoff else (max(b_on, 1.0) if b_on else 1.5)
sel = (B >= lo)
pbg = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(pbg, B[sel])
ax = axs[1, 0]; ax.plot(1 / B[sel], dR, lw=0.8); ax.set_xlabel("1/B [1/T]"); ax.set_ylabel("ΔR_xx [Ohm] (deg-5 bg removed)"); ax.set_title(f"B ≥ {lo:.2f} T")

# FFT vs 1/B, a few windows for the stability sweep
ax = axs[1, 1]
for blo_w, deg in ((lo, 5), (lo, 3), (min(lo + 1.0, B.max() - 2), 5)):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        freqs, spec = sdh_fft(R[:, None], B, b_range=(blo_w, B.max()), bg_degree=deg, nfft=4096, log=False)
    sp = spec[0]; ax.plot(freqs, sp / sp[freqs > 2].max(), lw=0.9, label=f"B≥{blo_w:.1f} T, bg deg {deg}")
    pk = [(freqs[i], sp[i]) for i in range(2, len(sp) - 2) if sp[i] > sp[i-1] and sp[i] > sp[i+1] and freqs[i] > 1.0]
    pk = sorted(pk, key=lambda t: -t[1])[:6]
    print(f"FFT B≥{blo_w:.2f} T deg {deg}: top peaks (T, rel): " + ", ".join(f"{f0:.1f} ({a/sp[freqs>2].max():.2f})" for f0, a in pk))
ax.axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f} T")
for f0, lab in ((0.216 * FL, "ABAB light"), (0.787 * FL, "ABAB heavy")):
    ax.axvline(f0, color="gray", ls=":", lw=0.8)
ax.set_xlim(0, 1.6 * FL); ax.set_xlabel("F [T]"); ax.set_ylabel("FFT amp (norm.)"); ax.legend(fontsize=8)
plt.tight_layout(); out = Path(__file__).resolve().parent / f"spot_{rid}.png"; plt.savefig(out, dpi=90); print("saved", out)
