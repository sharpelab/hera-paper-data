"""Runs 6 & 7 (sdh-spot-check): raw R(B), 1/B background-subtracted, FFT, onsets.
Gain model: R = (sr1_X / sr1_gain) / (sr0_X / sr0_gain)  [hera.analysis convention].
"""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}

for j, (rid, label) in enumerate(((6, "run 6 — electron, n=+3.2e12"), (7, "run 7 — hole, n=-1.2e12"))):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    ch = resolve_channels(r.meta)
    cur = current_channel(ch)
    volt = [c for c in ch if not c.is_current][0]
    I = r.col_at(cur.idx) / cur.gain           # A
    V = r.col_at(volt.idx) / volt.gain         # V
    R = np.abs(V / I)
    o = np.argsort(B); B, R, I, V = B[o], R[o], I[o], V[o]
    T = r.col("T_sample")
    print(f"=== {label} ===")
    print(f"  I = {np.median(I)*1e9:+.3f} nA, R {R.min():.1f} .. {R.max():.1f} Ohm (B=0/min {R[0]:.1f}), T {T.mean():.3f} K")

    # peak-to-peak oscillation amplitude in the top decade of field
    hi = B > 7
    p = np.polyfit(B[hi], R[hi], 3)
    osc = R[hi] - np.polyval(p, B[hi])
    r_fs = 50e-6 / np.median(np.abs(I))
    print(f"  osc pk-pk (B>7T) = {np.ptp(osc):.2f} Ohm ({np.ptp(osc)/R[hi].mean()*100:.1f}% of R); "
          f"R_full_scale(50uV) = {r_fs/1e3:.2f} kOhm, max R / FS = {R.max()/r_fs*100:.2f}%")

    axes[0, j].plot(B, R, lw=0.8); axes[0, j].set(xlabel="B (T)", ylabel="Rxx (Ohm)", title=label + " — raw")
    m = B > 0.9
    pb = np.polyfit(B[m], R[m], 5)
    axes[1, j].plot(1 / B[m], R[m] - np.polyval(pb, B[m]), lw=0.8)
    axes[1, j].set(xlabel="1/B (1/T)", ylabel="dRxx (Ohm)", title="background-subtracted")

    f, spec = sdh_fft(R[:, None], B, b_range=(1.5, B.max()), nfft=8192, bg_degree=5, log=False)
    sp = spec[0]
    axes[2, j].plot(f, sp, lw=0.9); axes[2, j].set(xlim=(0, 60), xlabel="F (T)", ylabel="|FFT|",
                                                   title="SdH FFT, 1.5-10 T (dF = 1.76 T)")
    pk, _ = find_peaks(sp, height=0.06 * sp[f > 3].max())
    pk = pk[f[pk] > 3]
    print("  FFT peaks (F T, rel):", [(round(float(f[i]), 2), round(float(sp[i] / sp[pk].max()), 3)) for i in pk])
    for i in pk:
        axes[2, j].axvline(f[i], color="r", ls=":", lw=0.6)

    h, e = 6.62607015e-34, 1.602176634e-19
    n_nom = 3.2 if rid == 6 else 1.2
    print(f"  F_L(nominal n={n_nom}e12, geometry prior) = {n_nom*1e16*h/(4*e):.1f} T")
    try:
        o2 = sdh_onset(R, B, b_lo=B.min(), r_full_scale=r_fs)
        print("  " + o2.summary().replace("\n", "\n  "))
    except SdhOnsetError as ex:
        print(f"  sdh_onset FAILED: {ex}")
    out[rid] = (B, R)

plt.tight_layout(); plt.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("saved hera_scratch/spot_runs67.png")
