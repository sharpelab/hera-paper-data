import numpy as np, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, summarize_run, GateCalibration

run = open_run("data/1")
print(summarize_run(run))
md = json.load(open("data/1/metadata.json"))
nbg, ntg = len(md["slow_setpoints"]), len(md["fast_setpoints"])
print("grid:", nbg, "BG x", ntg, "TG   interrupted:", run.interrupted)

def grid(name):
    return np.asarray(run.col(name)).reshape(nbg, ntg)
BG = grid("k_2400_volt")      # slow, rows
TG = grid("DC_bias")          # fast
I  = grid("sr0_X") / 1e6      # A  (Ithaco |gain| 1e6)
bg_axis = BG[:, 0]; tg_axis = TG[0, :]
# leakage
ibg = np.abs(np.asarray(run.col("k_2400_curr"))); isi = np.abs(np.asarray(run.col("k_2410_curr")))
print(f"leakage: |I_bg|max={ibg.max():.2e} A  |I_si|max={isi.max():.2e} A")

R = {ch: grid(f"{ch}_X") / I for ch in ("sr1","sr2","sr3")}
SAT = 2e-5 / 5e-9   # sensitivity 2e-5 / I_bias 5nA ~ 4.37k clip ceiling

def cnp_ridge(Rxx):
    """CNP V_tg per BG row = centroid of the high-R plateau (robust to the 2e-5 clip)."""
    pos, clipped, edge = [], [], []
    for i in range(nbg):
        r = np.abs(Rxx[i]); rs = gaussian_filter1d(r, 2.0)
        thr = 0.90 * rs.max()
        sel = rs >= thr
        c = np.average(tg_axis[sel], weights=rs[sel])
        k = int(np.argmin(np.abs(tg_axis - c)))
        pos.append(c); clipped.append(r.max() >= 0.97*SAT)
        edge.append(k <= 1 or k >= ntg-2)
    return np.array(pos), np.array(clipped), np.array(edge)

cal_geom = GateCalibration.from_thicknesses(15.6e-9, 12e-9)   # prior; ratio c_bg/c_tg
print(f"geometry prior: c_tg={cal_geom.c_tg:.4e}  c_bg={cal_geom.c_bg:.4e}  ratio c_bg/c_tg={cal_geom.c_bg/cal_geom.c_tg:.4f}")

fits = {}
for ch in ("sr1","sr2"):
    vtg_cnp, clip, edge = cnp_ridge(R[ch])
    keep = ~edge
    p, cov = np.polyfit(bg_axis[keep], vtg_cnp[keep], 1, cov=True)
    slope, intercept = p; serr = np.sqrt(cov[0,0])
    resid = vtg_cnp[keep] - np.polyval(p, bg_axis[keep])
    fits[ch] = dict(slope=slope, intercept=intercept, serr=serr,
                    rms=np.sqrt(np.mean(resid**2)), vtg=vtg_cnp, clip=clip, edge=edge,
                    ratio=-slope)
    print(f"\n[{ch}] CNP fit: V_tg = {slope:+.4f}*V_bg + {intercept:+.4f}   "
          f"(slope_err {serr:.4f})  ratio c_bg/c_tg=-slope={-slope:.4f}")
    print(f"     ridge RMS resid {fits[ch]['rms']*1e3:.1f} mV   rows kept {keep.sum()}/{nbg}   "
          f"clipped rows {clip.sum()}   edge-excluded {edge.sum()}")

# --- raw maps + fitted-line overlay ---
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6), constrained_layout=True)
for a, ch in zip(ax, ("sr1","sr2","sr3")):
    Z = np.clip(np.abs(R[ch])/1e3, 0, 5)
    im = a.pcolormesh(tg_axis, bg_axis, Z, shading="auto", cmap="viridis")
    fig.colorbar(im, ax=a, label="|R| (kΩ, clip@5)")
    a.set_xlabel("V_tg (DC_bias, V)"); a.set_ylabel("V_bg (V)"); a.set_title(f"{ch} |R|")
    if ch in fits:
        f = fits[ch]
        a.plot(np.polyval([f["slope"], f["intercept"]], bg_axis), bg_axis, "r-", lw=1.2, label="CNP fit")
        a.plot(f["vtg"], bg_axis, "w.", ms=4, label="ridge")
        a.legend(loc="upper right", fontsize=7)
fig.suptitle("Run 1 — 0 T gate map, CNP ridge + fit")
fig.savefig("hera_scratch/gatemap_run1.png", dpi=110)
print("\nsaved hera_scratch/gatemap_run1.png")
