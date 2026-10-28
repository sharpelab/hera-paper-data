"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, onset, FFT, model overlay."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

runs = {6: 3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for j, (rid, n) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; V = r.col("sr1_X") / 1.0
    R = V / I
    o = np.argsort(B); B, R, I, V = B[o], R[o], I[o], V[o]
    keep = B >= (1.0 if rid == 6 else 0.3); B, R, I, V = B[keep], R[keep], I[keep], V[keep]  # run 6: 50 mT grid below 1 T undersamples >7 T tones
    sens = r.meta.get("instruments", {}) if False else None
    print(f"\n=== run {rid}: n={n:+.2f}e12  B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts")
    print(f"I median {np.median(I)*1e9:.2f} nA (range {I.min()*1e9:.2f}-{I.max()*1e9:.2f}); "
          f"R(B~0.3)={R[np.argmin(abs(B-0.3))]:.1f}  R(5T)={R[np.argmin(abs(B-5))]:.1f}  R(10T)={R[-1]:.1f} Ohm; "
          f"max |V| {np.abs(V).max()*1e6:.2f} uV (sens 50 uV)")
    T = r.col("T_sample"); print(f"T_sample {T.min():.3f}-{T.max():.3f} K; I_tg |max| {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA")
    FL = 4.135667e-15/4 * abs(n) * 1e16
    print("F_L helper:", FL)
    EF, orbs = M.abab_fs(n*1e16); ms = M.abab_mstar(n*1e16)
    ab = M.abca_fs(n*1e16); abm = M.abca_mstar(n*1e16)
    print("model ABAB orbits:", [(round(f, 2), round(m, 3)) for f, m in ms], " ABCA:", round(ab[4], 2), "m*", round(abm[1], 3))
    ax[0, j].plot(B, R, lw=0.8); ax[0, j].set_title(f"run {rid} raw Rxx, n={n:+.1f}e12, D=0"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / np.median(np.abs(I)))
        print(on.summary())
        out[rid] = on
        ob = on.onset_b
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e); ob = 1.5
    # background-subtracted view
    Bu = np.linspace(max(ob * 0.8, B.min()), B.max(), 2000)
    Ri = np.interp(Bu, B, R); bg = np.polyval(np.polyfit(Bu, Ri, 5), Bu)
    ax[1, j].plot(1 / Bu, Ri - bg, lw=0.6); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dR (Ohm), deg-5 bg in B")
    ax[1, j].set_title(f"bg-subtracted, onset {ob:.2f} T")
    for lo in sorted({round(ob, 2), 2.0, 3.0, 4.0}):
        if lo >= B.max() - 2: continue
        for deg in (3, 5, 7):
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg, log=False)
            s = sp[0]; m = f > 2
            pk, pr = find_peaks(s[m], prominence=0.08 * s[m].max())
            top = sorted(zip(s[m][pk], f[m][pk]), reverse=True)[:5]
            print(f"  FFT b_range=({lo:.2f},{B.max():.1f}) deg{deg}: dF={1/(1/lo-1/B.max()):.2f} T; peaks " +
                  ", ".join(f"{ff:.2f}T({aa/s[m].max():.2f})" for aa, ff in top))
            if deg == 5:
                ax[2, j].plot(f, s / s[m].max(), lw=0.8, label=f"from {lo:.2f} T")
    for (ff, mm) in ms:
        ax[2, j].axvline(ff, color="g", ls="--", lw=0.8)
    ax[2, j].axvline(ab[4], color="r", ls=":", lw=1.2)
    ax[2, j].set_xlim(0, 2.2 * ab[4]); ax[2, j].set_ylim(0, 1.1); ax[2, j].legend(fontsize=7)
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_title("FFT (deg-5 bg in B); green ABAB, red ABCA=F_L")
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=90)
