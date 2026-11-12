"""Runs 6/7: onset on the properly sampled record, windowed FFTs, peaks vs model F(n)."""
import numpy as np, warnings, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

def load(rid):
    run = open_run(f"data/{rid}")
    B = run.col("magnet_field"); R = run.col("sr1_X") / (run.col("sr0_X") / -1e6)
    o = np.argsort(B); return B[o], R[o], np.median(run.col("sr0_X") / -1e6)

fig, axs = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12, blo_rec) in enumerate(((6, 3.2, 1.0), (7, -1.2, 0.3))):
    B, R, I = load(rid)
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n===== run {rid}: n = {n12:+.2f}e12, F_L = {FL:.2f} T =====")
    try:
        EF, orb = M.abab_fs(n12 * 1e12); ms = M.abab_mstar(n12 * 1e12)
        print("  model ABAB orbits (F, kF):", [(round(f, 2), round(kf, 3)) for f, kf in orb], " m*:", [(round(f, 2), round(m, 3)) for f, m in ms])
    except Exception as e: print("  abab model err:", e)
    try:
        r = M.abca_fs(n12 * 1e12); print("  model ABCA:", r[1:], " m*:", M.abca_mstar(n12 * 1e12))
    except Exception as e: print("  abca model err:", e)
    # onset on the usable record
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, b_lo=blo_rec, r_full_scale=50e-6 / I)
            print(on.summary() if hasattr(on, "summary") else on)
        except SdhOnsetError as e: print("  SdhOnsetError:", e)
        for ww in w: print("  warn:", ww.message)
    # windowed FFTs
    wins = [(1.0, 3.0), (1.5, 6.0), (2.0, 10.0)] if rid == 6 else [(0.7, 2.5), (1.0, 5.0), (2.0, 10.0)]
    for j, (a, b) in enumerate(wins):
        f, sp = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False)
        sp = sp[0]; m = (f > 1) & (f < 60)
        pk, pr = find_peaks(sp[m], prominence=0.05 * sp[m].max())
        top = sorted(zip(pr["prominences"], f[m][pk]), reverse=True)[:6]
        dF = 1 / (1 / a - 1 / b)
        print(f"  FFT window {a}-{b} T (dF = {dF:.2f} T): peaks F = " + ", ".join(f"{ff:.1f}" for _, ff in top) + "  (F/F_L: " + ", ".join(f"{ff/FL:.2f}" for _, ff in top) + ")")
        ax = axs[k, j]; ax.plot(f[m], sp[m] / sp[m].max()); ax.axvline(FL, color="r", ls="--", lw=0.8, label="F_L")
        for _, ff in top[:4]: ax.annotate(f"{ff:.1f}", (ff, np.interp(ff, f[m], sp[m] / sp[m].max())), fontsize=7)
        ax.set_title(f"run {rid} FFT {a}-{b} T, dF={dF:.1f}"); ax.set_xlabel("F (T)"); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig("hera_scratch/spot_fft_windows.png", dpi=110)

# model F(n) table on the electron side for fan design
print("\n=== model F(n), electron side (T) ===")
for n in (0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.25):
    FL = luttinger_frequency(n * 1e16)
    try: ab = [round(f, 1) for f, _ in M.abab_fs(n * 1e12)[1]]; mm = [round(m, 3) for _, m in M.abab_mstar(n * 1e12)]
    except Exception as e: ab, mm = str(e)[:40], ""
    try: ac = M.abca_fs(n * 1e12); acm = M.abca_mstar(n * 1e12); acs = f"{ac[4]:.1f} ({ac[1]}, m* {acm[1]:.3f})"
    except Exception as e: acs = str(e)[:40]
    print(f"  n={n:.2f}: F_L={FL:5.1f}  ABAB {ab} m* {mm}  ABCA {acs}")
