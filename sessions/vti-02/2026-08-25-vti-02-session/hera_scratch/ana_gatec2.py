"""Gate C: four legs -> ridge positions, leakage, and the two-point cap ratio.

Raw first (plot_raw per leg), then the reduced read.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from hera.analysis import open_run, summarize_run

BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"
SCRATCH = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch"
RUNS = [0, 1, 2, 3]


def load(rid):
    r = open_run(f"{BASE}/{rid}")
    volt_cols = [c for c in r.cols if c.endswith("_volt")]
    xcol = max(volt_cols, key=lambda c: np.ptp(r.col(c)))
    V = r.col(xcol)
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    R = r.col("sr1_X") / I
    return dict(rid=rid, run=r, xcol=xcol, V=V, I=I, R=R,
                itg=r.col("k_2400_tg_curr"), ibg=r.col("k_2400_bg_curr"),
                T=r.col("T_sample"))


def ridges(V, R, smooth=2.0, prom_frac=0.03):
    """Peaks in R(V), smoothed; prominence as a fraction of the R span."""
    o = np.argsort(V)
    Vs, Rs = V[o], R[o]
    Rsm = gaussian_filter1d(Rs, smooth)
    prom = prom_frac * np.ptp(Rsm)
    idx, props = find_peaks(Rsm, prominence=prom)
    out = []
    for i, p in zip(idx, props["prominences"]):
        # parabolic refine on the smoothed curve
        if 0 < i < len(Vs) - 1:
            y0, y1, y2 = Rsm[i - 1], Rsm[i], Rsm[i + 1]
            d = y0 - 2 * y1 + y2
            shift = 0.5 * (y0 - y2) / d if d != 0 else 0.0
            dv = np.median(np.diff(Vs))
            vpk = Vs[i] + shift * dv
        else:
            vpk = Vs[i]
        out.append((vpk, Rsm[i], p, bool(0 < i < len(Vs) - 1)))
    return Vs, Rsm, out


legs = [load(i) for i in RUNS]

print("=" * 78)
print("GATE C — four legs")
print("=" * 78)
all_ridges = {}
for d in legs:
    r = d["run"]
    tag = [c for c in r.meta.get("comments", []) if str(c).startswith("leg:")]
    print(f"\n--- run {d['rid']}  {d['xcol']}  {tag[0] if tag else ''}")
    print(f"    rows {len(d['V'])}, interrupted={r.interrupted}")
    print(f"    R_xx  med {np.median(d['R']):7.2f}  min {d['R'].min():7.2f}  max {d['R'].max():7.2f} ohm")
    print(f"    I     med {np.median(d['I']):.4e} A  (spread {np.ptp(d['I']):.2e})")
    print(f"    sr1 load max {np.abs(r.col('sr1_X')).max()/5e-4:.3f} of full scale")
    print(f"    I_tg  base {d['itg'][0]:+.3e}  max excess {np.abs(d['itg']-d['itg'][0]).max():.3e} A")
    print(f"    I_bg  base {d['ibg'][0]:+.3e}  max excess {np.abs(d['ibg']-d['ibg'][0]).max():.3e} A")
    print(f"    T     {d['T'].min():.3f}-{d['T'].max():.3f} K")
    Vs, Rsm, pk = ridges(d["V"], d["R"])
    d["Vs"], d["Rsm"], d["pk"] = Vs, Rsm, pk
    for vpk, rpk, prom, interior in pk:
        print(f"    RIDGE at {d['xcol']} = {vpk:+.4f} V   R = {rpk:7.2f} ohm   "
              f"prominence {prom:6.2f} ohm   {'interior' if interior else 'EDGE'}")
    all_ridges[d["rid"]] = pk

# ---- two-point cap ratio from the TG-axis and BG-axis intercepts ----
print("\n" + "=" * 78)
print("two-point cap-ratio estimate")
print("=" * 78)
tg_pk = sorted([p[0] for p in all_ridges[0] + all_ridges[1]])
bg_pk = sorted([p[0] for p in all_ridges[2] + all_ridges[3]])
print(f"  TG-axis ridges (V_bg = 0): {['%+.4f' % v for v in tg_pk]}")
print(f"  BG-axis ridges (V_tg = 0): {['%+.4f' % v for v in bg_pk]}")
print("  a CNP line through (Vtg_i, 0) and (0, Vbg_i) has slope dVtg/dVbg = -Vtg_i/Vbg_i,")
print("  and c_bg/c_tg = -slope = Vtg_i/Vbg_i")
if len(tg_pk) == len(bg_pk):
    # pair by sign
    for vt in tg_pk:
        cands = [vb for vb in bg_pk if np.sign(vb) == np.sign(vt)]
        if cands:
            vb = min(cands, key=lambda x: abs(abs(x) - abs(vt)))
            print(f"    ridge (Vtg={vt:+.4f}, Vbg={vb:+.4f})  ->  c_bg/c_tg = {vt/vb:.4f}")
print(f"  geometry prior c_bg/c_tg = {9.5/11:.4f}  (t_tg/t_bg = 9.5/11 nm)")

# ---- figures ----
fig, axes = plt.subplots(2, 4, figsize=(17, 7.5), squeeze=False)
for k, d in enumerate(legs):
    ax = axes[0][k]
    ax.plot(d["V"], d["R"], ".", ms=3, color="0.6", label="raw")
    ax.plot(d["Vs"], d["Rsm"], "-", lw=1.2, color="C0", label="smoothed")
    for vpk, rpk, prom, interior in d["pk"]:
        ax.axvline(vpk, color="C3", lw=0.9, ls="--")
        ax.annotate(f"{vpk:+.3f} V\n{rpk:.0f} Ω", (vpk, rpk), textcoords="offset points",
                    xytext=(4, 6), fontsize=8, color="C3")
    ax.set_xlabel(f"{d['xcol']} (V)")
    ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {d['rid']}: 0 → {d['V'][np.argmax(np.abs(d['V']))]:+g} V", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)

    ax = axes[1][k]
    ax.plot(d["V"], d["itg"] * 1e12, ".-", ms=2, lw=0.7, label="$I_{tg}$")
    ax.plot(d["V"], d["ibg"] * 1e12, ".-", ms=2, lw=0.7, label="$I_{bg}$")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel(f"{d['xcol']} (V)")
    ax.set_ylabel("gate current (pA)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
fig.suptitle("Gate C — vti-02, B = 0, $V_{si}$ = 0, T = 1.18 K, $I_{bias}$ = 49.2 nA", y=0.995)
fig.tight_layout()
fig.savefig(f"{SCRATCH}/gatec.png", dpi=120)
print(f"\nwrote {SCRATCH}/gatec.png")
