"""SdH read of the two spot checks (runs 6, 7): raw R(B), bg-subtracted dR, sdh_onset, sdh_fft windows."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, warnings
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
FS = 50e-6/10e-9   # 5 kOhm full scale
out = {}
for rid, n12 in ((6, 3.2), (7, -1.2)):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); R = r.col("sr1_X")/(r.col("sr0_X")/-1e6)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12)*1e16))
    print(f"\n===== run {rid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T; R(B~0) = {R[B<0.1].mean():.1f}, R(10T) = {R[-1]:.0f} Ohm; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=FS)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        out[rid] = on
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); on = None
    # bg-subtracted trace for a by-eye plot
    m = B > 0.5
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    fig, ax = plt.subplots(3, 1, figsize=(10, 10))
    ax[0].plot(B, R, lw=0.7); ax[0].set_ylabel("Rxx (Ohm)"); ax[0].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0, raw")
    ax[1].plot(1/B[m], dR, lw=0.7); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dR (Ohm), deg-5 bg in B")
    for lo in (1.5, 2.5, 4.0):
        for deg in (5,):
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, 10.0), bg_degree=deg, log=False, nfft=2048)
            s = sp[0]; ax[2].plot(f, s/s[(f>3)&(f<80)].max(), lw=0.8, label=f"B {lo}-10 T, deg {deg}")
            pk = [(round(float(f[i]),1), round(float(s[i]/s[(f>3)&(f<80)].max()),2)) for i in np.argsort(s)[::-1] if 3 < f[i] < 80][:6]
            print(f"  FFT window {lo}-10 T deg {deg}: top peaks (T, rel) = {pk}")
    ax[2].axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f}"); ax[2].set_xlim(0, 80); ax[2].set_xlabel("F (T)"); ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=110)
