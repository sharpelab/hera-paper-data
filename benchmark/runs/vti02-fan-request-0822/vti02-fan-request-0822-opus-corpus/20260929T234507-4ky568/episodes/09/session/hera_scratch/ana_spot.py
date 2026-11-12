"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Raw -> onset -> FFT vs F_L. Feeds the landau-fan design."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

def trace(run_dir):
    r = open_run(run_dir)
    B = r.col("magnet_field")
    Icur = r.col("sr0_X") / (-1e6)          # A, drain current (preamp gain -1e6)
    Vxx = r.col("sr1_X") / 1.0              # V, sr1 gain = 1 (device card)
    R = Vxx / Icur
    return r, B, R, Icur

for fid, nspot, sens in ((6, +3.20, 50e-6), (7, -1.20, 50e-6)):
    r, B, R, I = trace(f"data/{fid}")
    o = np.argsort(B)
    B, R, I = B[o], R[o], I[o]
    n_m2 = abs(nspot) * 1e12 * 1e4          # cm^-2 -> m^-2
    FL = float(luttinger_frequency(n_m2))
    Ibias = float(np.median(np.abs(I)))
    rfs = sens / Ibias
    print(f"\n===== run {fid}: n = {nspot:+.2f}e12, F_L = {FL:.2f} T "
          f"| I_bias = {Ibias*1e9:.3f} nA, R_fullscale = {rfs:.0f} Ohm")
    print(f"   R: min {np.nanmin(np.abs(R)):.1f}  max {np.nanmax(np.abs(R)):.1f} Ohm "
          f"({100*np.nanmax(np.abs(R))/rfs:.1f} % FS), B {B.min():.2f}-{B.max():.2f} T, "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    print(f"   gate leakage: |I_tg|max {np.nanmax(np.abs(r.col('k_2400_tg_curr')))*1e12:.1f} pA, "
          f"|I_bg|max {np.nanmax(np.abs(r.col('k_2400_bg_curr')))*1e12:.1f} pA")

    Rm = np.abs(R)
    try:
        on = sdh_onset(Rm, B, r_full_scale=rfs)
        print(on.summary())
        print(f"   onset_b = {on.onset_b:.3f} T, clip_high_b = {on.clip_high_b}")
    except Exception as e:
        on = None
        print("   sdh_onset FAILED:", type(e).__name__, e)

    # FFT over a few low-B cutoffs (stability sweep)
    cuts = [0.5, 0.8, 1.0, 1.5, 2.0]
    fig, ax = plt.subplots(3, 1, figsize=(9, 10))
    ax[0].plot(B, Rm, lw=.7); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)")
    ax[0].set_title(f"run {fid} RAW  n={nspot:+.2f}e12  F_L={FL:.1f} T")
    # background-subtracted vs 1/B
    m = B > 0.3
    bg = np.polyval(np.polyfit(B[m], Rm[m], 5), B[m])
    ax[1].plot(1/B[m], Rm[m]-bg, lw=.8)
    ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm)"); ax[1].set_title("bg-subtracted (deg 5, B>0.3 T)")
    for c in cuts:
        if c >= B.max(): continue
        f, sp = sdh_fft(Rm[:, None], B, b_range=(c, B.max()), bg_degree=5, log=False, nfft=2048)
        s = sp[0]
        ax[2].plot(f, s/ s.max(), lw=.9, label=f"cut {c} T")
        sel = (f > 2) & (f < 3*FL)
        fs, ss = f[sel], s[sel]
        # top peaks
        idx = [i for i in range(1, len(ss)-1) if ss[i] > ss[i-1] and ss[i] > ss[i+1]]
        idx = sorted(idx, key=lambda i: -ss[i])[:5]
        peaks = ", ".join(f"{fs[i]:.1f}T({ss[i]/ss.max():.2f})" for i in sorted(idx, key=lambda i: fs[i]))
        dF = 1/(1/c - 1/B.max())
        print(f"   cut {c:4.1f} T: dF={dF:5.2f} T | peaks (f/F_L): " +
              ", ".join(f"{fs[i]:.1f}T={fs[i]/FL:.3f}FL amp{ss[i]/ss.max():.2f}" for i in sorted(idx, key=lambda i: fs[i])))
    ax[2].axvline(FL, color='k', ls='--', label=f"F_L={FL:.1f} T")
    ax[2].axvline(0.72*FL, color='r', ls=':', label="0.72 F_L")
    ax[2].axvline(0.28*FL, color='b', ls=':', label="0.28 F_L")
    ax[2].set_xlim(0, 2*FL); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("|FFT| (norm)")
    ax[2].legend(fontsize=7)
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{fid}.png", dpi=110)
    print(f"   -> hera_scratch/spot_run{fid}.png")
