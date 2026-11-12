import numpy as np
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset, GateCalibration, luttinger_frequency

CAL = GateCalibration(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894e16, D_offset=-0.013e9)
base = Path("data")
fig, axes = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for k, (rid, nspot) in enumerate([(6, +3.2), (7, -1.2)]):
    r = open_run(base/str(rid))
    B = r.col("magnet_field"); I = r.col("sr0_X")/(-1e6); V = r.col("sr1_X")/1.0
    R = V/I
    T = r.col("T_sample")
    o = np.argsort(B); B, R = B[o], R[o]
    print("="*70); print(f"RUN {rid}  n={nspot:+.2f}e12  T {T.min():.3f}-{T.max():.3f} K")
    print(f"  R: {R.min():.1f} .. {R.max():.1f} Ohm ; R(Bmin)={R[0]:.1f}, R(Bmax)={R[-1]:.1f}")
    print(f"  I: {np.median(I)*1e9:.3f} nA ; full scale 50uV/I = {50e-6/abs(np.median(I)):.0f} Ohm")
    F_L = luttinger_frequency(abs(nspot)*1e16)
    print(f"  full-density Onsager F_L = {F_L:.1f} T")
    ax = axes[0, k]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw, n={nspot:+.2f}e12")
    # background subtract, plot vs 1/B
    m = B > 0.5
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    ax = axes[1, k]; ax.plot(1/B[m], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"run {rid} background-subtracted vs 1/B")
    print(f"  dR rms (B>0.5) = {dR.std():.3f} Ohm, peak-peak {dR.max()-dR.min():.2f}")
    for blo in (1.0, 2.0, 3.0):
        f, spec = sdh_fft(R[:, None], B, b_range=(blo, B.max()), nfft=2048, bg_degree=5, log=False)
        s = spec[0]; sel = f > 1.0
        top = np.argsort(s[sel])[::-1][:6]
        print(f"  FFT B in [{blo},{B.max():.1f}]: peaks (T, amp) " + ", ".join(f"{f[sel][t]:.1f}:{s[sel][t]:.2f}" for t in sorted(top, key=lambda t:-s[sel][t])))
        if blo == 1.0:
            axes[2, k].plot(f[sel], s[sel], lw=0.8, label=f"B>{blo}")
        else:
            axes[2, k].plot(f[sel], s[sel], lw=0.8, label=f"B>{blo}")
    axes[2, k].axvline(F_L, color='r', ls='--', label=f"F_L={F_L:.1f}")
    axes[2, k].set_xlim(0, 60); axes[2, k].set_xlabel("F (T)"); axes[2, k].legend(fontsize=7); axes[2,k].set_title(f"run {rid} SdH FFT")
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6/abs(np.median(I)))
        print(so.summary())
    except Exception as e:
        print("  sdh_onset:", type(e).__name__, e)
fig.tight_layout(); fig.savefig("hera_scratch/spot67.png", dpi=110)
print("saved hera_scratch/spot67.png")
