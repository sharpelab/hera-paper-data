"""Spot-check read v2: FFT windows above the 50-mT leg (run 6) / above onset (run 7), B-window split,
peak tables vs F_L, model F(n)/m*(n) table in m^-2, column-order + timing calibration."""
import sys, json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from hera.analysis import open_run, sdh_fft, luttinger_frequency
import fs_count_b0 as m

SENS = 50e-6
def load(rid):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / (-1e6); R = np.abs(r.col("sr1_X") / I)
    o = np.argsort(B); return r, B[o], R[o], np.median(np.abs(I))

def peaks(f, sp, fmin, fmax, k=8):
    sel = (f >= fmin) & (f <= fmax); ff, ss = f[sel], sp[sel]
    pk, pr = find_peaks(ss, prominence=0.02 * ss.max())
    order = np.argsort(ss[pk])[::-1][:k]
    return sorted([(round(float(ff[p]), 2), round(float(ss[p] / ss.max()), 3)) for p in pk[order]])

fig, axs = plt.subplots(2, 2, figsize=(14, 9))
res = {}
for j, (rid, n12, blo_full) in enumerate([(6, 3.2, 1.0), (7, -1.2, 0.71)]):
    r, B, R, Ib = load(rid); FL = float(luttinger_frequency(abs(n12) * 1e16)); Bmax = B.max()
    print("=" * 70, f"\nrun {rid} n={n12:+.1f}e12  F_L={FL:.2f} T  I_bias={Ib*1e9:.2f} nA")
    sel = B >= blo_full
    cf = np.polyfit(B[sel], R[sel], 5); dR = R[sel] - np.polyval(cf, B[sel])
    axs[0, j].plot(1 / B[sel], dR, lw=0.7); axs[0, j].set_xlabel("1/B (1/T)"); axs[0, j].set_ylabel("dRxx (Ohm)")
    axs[0, j].set_title(f"run {rid}: n={n12:+.1f}e12 D=0 — bg-subtracted (deg 5 in B), B >= {blo_full} T")
    mid = 2 / (1 / blo_full + 1 / Bmax)
    wins = [("full", (blo_full, Bmax), "k"), ("low-B half", (blo_full, mid), "tab:blue"), ("high-B half", (mid, Bmax), "tab:red")]
    if rid == 6: wins.append(("1.3-10", (1.3, Bmax), "tab:green"))
    res[rid] = {}
    for lab, (a, b), c in wins:
        f, sp = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False, nfft=4096)
        sp = sp[0]; dF = 1 / (1 / a - 1 / b)
        pk = peaks(f, sp, 1.5, 2.2 * FL)
        print(f"  {lab:12s} [{a:.2f},{b:.2f}] T dF={dF:.2f}: peaks (F, rel amp) = {pk}")
        res[rid][lab] = dict(win=(a, b), dF=dF, peaks=pk)
        axs[1, j].plot(f, sp / sp[(f > 1.5)].max(), c, lw=1, label=f"{lab} [{a:.2f},{b:.2f}] T, dF {dF:.2f}")
    axs[1, j].axvline(FL, color="g", ls="--", label=f"F_L {FL:.1f} T (g=4)")
    axs[1, j].set_xlim(0, 2.0 * FL); axs[1, j].set_ylim(0, 1.1); axs[1, j].set_xlabel("F (T)"); axs[1, j].legend(fontsize=7)
    axs[1, j].set_title("1/B FFT (normalized, F > 1.5 T)")
fig.tight_layout(); fig.savefig("hera_scratch/spot_fft.png", dpi=110)
json.dump(res, open("hera_scratch/spot_fft.json", "w"), indent=1)

print("\n=== model F(n) [T], m*/m_e (n in 1e12 cm^-2; ABAB orbits sorted by F; ABCA single) ===")
tab = {}
for n in [0.6, 0.8, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 3.25, -0.6, -0.8, -1.0, -1.27]:
    FL = float(luttinger_frequency(abs(n) * 1e16))
    try:
        ef, orbs = m.abab_fs(n * 1e16); ms = m.abab_mstar(n * 1e16)
        Ft, mA = m.abca_mstar(n * 1e16)
        fr = [round(F / FL, 3) for F, k in orbs]
        print(f"n={n:+5.2f}: F_L={FL:5.2f} | ABAB F={[round(F,2) for F,k in orbs]} frac={fr} m*={[round(mm,3) for F,mm in ms]} | ABCA F={Ft:.2f} m*={mA:.3f}")
        tab[n] = dict(FL=FL, abab=[(float(F), float(k)) for F, k in orbs], abab_m=[float(mm) for F, mm in ms], abca=(float(Ft), float(mA)))
    except Exception as e:
        print(f"n={n}: {e}")
json.dump(tab, open("hera_scratch/model_table.json", "w"), indent=1)

print("\n=== column order / timing ===")
for rid in (5, 6):
    r = open_run(f"data/{rid}"); mt = r.meta
    print(rid, r.cols, "| n_rows", len(r.data), "| wall", round(mt["end_time"] - mt["start_time"]), "s",
          "| slow/fast keys:", [k for k in mt if "setpoint" in k or "param" in k])
r5 = open_run("data/5").meta
print("run5 keys sample:", {k: (v if not isinstance(v, (list, dict)) else type(v).__name__) for k, v in r5.items() if k not in ("columns",)})
