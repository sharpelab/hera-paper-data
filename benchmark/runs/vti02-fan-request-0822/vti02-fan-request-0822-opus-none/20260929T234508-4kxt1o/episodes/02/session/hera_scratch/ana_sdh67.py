"""SdH spot checks runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12) — raw + FFT + onset."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

D = Path("/home/hera/measurements/zack/20260822-vti-02/data")

def trace(rid):
    r = open_run(D / str(rid))
    B = r.col("magnet_field")
    mc = r.meta["measurement_config"]
    I = r.col("sr0_X") / mc["sr0_gain"]
    V1 = r.col("sr1_X") / mc.get("sr1_gain", 1.0)
    Rxx = V1 / I
    T = r.col("T_sample")
    return r, B, Rxx, I, T

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for j, (rid, nsp) in enumerate([(6, +3.2), (7, -1.2)]):
    r, B, Rxx, I, T = trace(rid)
    o = np.argsort(B); Bs, Rs = B[o], Rxx[o]
    out[rid] = (Bs, Rs)
    ax = axes[0, j]
    ax.plot(B, Rxx, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid}: raw  n={nsp:+.1f}e12  I={np.median(np.abs(I))*1e9:.2f} nA  T={T.mean():.2f} K")

    # background-subtracted vs 1/B
    m = Bs > 1.0
    p = np.polyfit(Bs[m], Rs[m], 5)
    dR = Rs[m] - np.polyval(p, Bs[m])
    ax = axes[1, j]
    ax.plot(1 / Bs[m], dR, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title(f"run {rid}: bg-subtracted (deg5, B>1 T)")

    f, spec = sdh_fft(Rs[m][:, None], Bs[m], b_range=(1.0, Bs.max()), bg_degree=5, log=False)
    s = spec[0]
    ax = axes[2, j]
    ax.plot(f, s, lw=1.0)
    ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT|")
    FL = abs(nsp) * 1e16 * 6.62607015e-34 / (4 * 1.602176634e-19)
    ax.axvline(FL, color="r", ls="--", lw=0.8)
    ax.set_title(f"run {rid}: FFT over 1-10 T; F_L(full n)={FL:.1f} T (red)")
    # top peaks
    from scipy.signal import find_peaks
    pk, _ = find_peaks(s, height=0.12 * s[f > 3].max())
    pk = [q for q in pk if f[q] > 3]
    pk = sorted(pk, key=lambda q: -s[q])[:8]
    print(f"--- run {rid}: n={nsp:+.2f}e12, F_L={FL:.2f} T, R(B~0)={Rs[:5].mean():.1f} Ohm, R(10T)={Rs[-5:].mean():.1f} Ohm")
    print("   FFT peaks (F T, rel amp):", [(round(float(f[q]), 2), round(float(s[q] / s[pk[0]]), 3)) for q in pk])
    try:
        so = sdh_onset(Rs, Bs, b_lo=0.3, f_min=3.0)
        print(so.summary())
    except SdhOnsetError as e:
        print("   sdh_onset FAILED:", e)

plt.tight_layout()
plt.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/sdh67.png", dpi=110)
print("saved sdh67.png")
