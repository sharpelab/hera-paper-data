"""Spot-check analysis (runs 6, 7): raw R(B), sdh_onset, FFT tone content + stability, vs model F(n)."""
import numpy as np, json, sys, warnings
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

I_BIAS = 10.0e-9
CM2_SI = 1e16          # 1e12 cm^-2 -> m^-2
SPOTS = {6: +3.20, 7: -1.20}
FS_OHM = 50e-6 / I_BIAS

def peaks(f, s, fmin=1.5, topn=8):
    m = f >= fmin
    ff, ss = f[m], s[m]
    idx, props = find_peaks(ss, prominence=0.04 * ss.max())
    order = np.argsort(props["prominences"])[::-1][:topn]
    idx = idx[order]
    return sorted([(float(ff[i]), float(ss[i] / ss.max())) for i in idx])

res = {}
fig, ax = plt.subplots(3, 2, figsize=(14, 12))

for j, (fid, n12) in enumerate(SPOTS.items()):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * CM2_SI))
    print(f"\n{'='*74}\nrun {fid}: n = {n12:+.2f}e12 cm^-2, F_L = {FL:.2f} T | R {R.min():.0f}..{R.max():.0f} Ohm "
          f"(FS {FS_OHM:.0f}) | T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K | "
          f"B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts")

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        so = sdh_onset(R, B, r_full_scale=FS_OHM)
        for x in w: print("  [warn]", str(x.message)[:160])
    print(so.summary())
    res[fid] = dict(n12=n12, FL=FL, onset_b=float(so.onset_b),
                    tones=[[float(t.freq), float(t.onset_b), bool(t.censored)] for t in so.tones])

    lo = max(so.onset_b, 0.35)
    bmid = 2.0 * lo * B.max() / (lo + B.max())      # equal halves in 1/B
    wins = {"full": (lo, B.max()), "lowB": (lo, bmid), "highB": (bmid, B.max())}
    res[fid]["windows"] = {}
    for k, (b0, b1) in wins.items():
        dF = 1.0 / (1.0 / b0 - 1.0 / b1)
        row = {}
        for deg in (3, 5, 7):
            f, spec = sdh_fft(R[:, None], B, b_range=(b0, b1), nfft=8192, bg_degree=deg, log=False)
            row[deg] = peaks(f, spec[0])
            if deg == 5:
                ax[1, j].plot(f, spec[0] / spec[0][f > 1.5].max(), lw=0.9, label=f"{k} {b0:.2f}-{b1:.1f}T")
        res[fid]["windows"][k] = dict(b=[float(b0), float(b1)], dF=float(dF), peaks=row)
        print(f"  FFT {k:5s} B {b0:.2f}-{b1:.2f} T  deltaF={dF:5.2f} T")
        for deg, pk in row.items():
            print(f"      bg_deg {deg}: " + ", ".join(f"{fq:.2f}T({a:.2f})" for fq, a in pk))

    # --- model at this density ---
    nSI = n12 * CM2_SI
    orbs = M.abab_fs(nSI)[1]; ms = M.abab_mstar(nSI)
    Fa, ma = M.abca_mstar(nSI)
    print(f"  MODEL ABAB: F = {[round(F,2) for F,_ in orbs]} T, sum {sum(F for F,_ in orbs):.2f} (F_L {FL:.2f}); "
          f"m* = {[round(m,4) for _,m in ms]}")
    print(f"  MODEL ABCA: F = {Fa:.2f} T, m* = {ma:.4f} me")
    res[fid]["abab"] = [[float(F), float(m)] for (F, _), (_, m) in zip(orbs, ms)]
    res[fid]["abca"] = [float(Fa), float(ma)]

    ax[0, j].plot(B, R, lw=0.6)
    ax[0, j].axvline(so.onset_b, color="r", ls="--", label=f"onset {so.onset_b:.2f} T")
    ax[0, j].set_title(f"run {fid} RAW Rxx vs B  (n={n12:+.2f}e12, D=0)"); ax[0, j].legend(fontsize=8)
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    ax[1, j].axvline(FL, color="k", ls="--", lw=1.2, label=f"F_L {FL:.1f}T")
    for F, _ in res[fid]["abab"]:
        ax[1, j].axvline(F, color="tab:green", ls=":", lw=1.4)
    ax[1, j].set_xlim(0, FL * 1.6); ax[1, j].set_xlabel("F (T)"); ax[1, j].legend(fontsize=7)
    ax[1, j].set_title(f"run {fid} FFT — green: ABAB model tones, black: F_L")
    m = B >= lo
    c = np.polyfit(B[m], R[m], 5)
    ax[2, j].plot(1.0 / B[m], R[m] - np.polyval(c, B[m]), lw=0.7)
    ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_title(f"run {fid} dRxx vs 1/B (B>{lo:.2f} T)")

plt.tight_layout(); plt.savefig("hera_scratch/spot_runs67.png", dpi=110)
json.dump(res, open("hera_scratch/spot_runs67.json", "w"), indent=1)
print("\nwrote hera_scratch/spot_runs67.png/.json")
