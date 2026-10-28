import os
import numpy as np
import hera.analysis as a
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

MDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(MDIR, "hera_scratch")
run = a.open_run(os.path.join(MDIR, "data", "0"))
fg = a.fan_grids(run)

# Axes: slow = k_2400_volt (BG), fast = DC_bias (TG)
Vbg = np.asarray(fg.slow)
Vtg = fg.grid("DC_bias")[0, :]
nslow, nfast = fg.grid("DC_bias").shape
print(f"grid: {nslow} BG rows x {nfast} TG cols")
print(f"Vbg [{Vbg.min():.3f},{Vbg.max():.3f}] step {np.diff(Vbg).mean():.3f}")
print(f"Vtg [{Vtg.min():.3f},{Vtg.max():.3f}] step {np.diff(Vtg).mean():.3f}")

# Leakage
ibg = np.abs(fg.grid("k_2400_curr"))
isi = np.abs(fg.grid("k_2410_curr"))
print(f"\nLEAKAGE |I_bg|max={ibg.max():.2e} A  |I_si|max={isi.max():.2e} A  (soft ceiling 1e-9)")

# Resistance grids (gain-applied, measured-I denominator)
rg = a.resistance_grids(fg)
print("R channels:", list(rg.R.keys()))

# --- CNP ridge extraction per Rxx channel ---
def extract_ridge(Rgrid, Vtg, sigma=1.5):
    """For each BG row, argmax of |Rxx| along Vtg (smoothed). Return Vtg_cnp, peakR, clipped mask."""
    absR = np.abs(Rgrid)
    vcnp = np.full(absR.shape[0], np.nan)
    peak = np.full(absR.shape[0], np.nan)
    clipped = np.zeros(absR.shape[0], bool)
    for i in range(absR.shape[0]):
        row = gaussian_filter1d(absR[i], sigma)
        j = int(np.nanargmax(row))
        vcnp[i] = Vtg[j]
        peak[i] = absR[i, j]
        if j <= 1 or j >= len(Vtg) - 2:
            clipped[i] = True
    return vcnp, peak, clipped

# Rxx channels are sr1 (T3-T4) and sr2 (B4-B5); sr3 is Hall (skip for CNP)
rxx_channels = [c for c in rg.R.keys() if c in ("sr1", "sr2")]
fits = {}
for cid in rxx_channels:
    vcnp, peak, clipped = extract_ridge(rg.R[cid], Vtg)
    keep = ~clipped & np.isfinite(vcnp)
    # polyfit Vtg_cnp vs Vbg over surviving rows
    p, cov = np.polyfit(Vbg[keep], vcnp[keep], 1, cov=True)
    slope, intercept = p
    resid = vcnp[keep] - np.polyval(p, Vbg[keep])
    rms = np.sqrt(np.mean(resid**2))
    fits[cid] = dict(slope=slope, intercept=intercept, rms=rms,
                     nkeep=int(keep.sum()), nclip=int(clipped.sum()),
                     vcnp=vcnp, peak=peak, keep=keep,
                     slope_err=np.sqrt(cov[0, 0]))
    print(f"\n[{cid}] CNP fit  Vtg = {slope:.4f}*Vbg + {intercept:.4f}")
    print(f"   slope_err {np.sqrt(cov[0,0]):.4f}  rms_resid {rms*1e3:.1f} mV  rows kept {keep.sum()}/{nslow} (clipped {clipped.sum()})")
    print(f"   ratio c_bg/c_tg = -slope = {-slope:.4f}   peakR range [{np.nanmin(peak)/1e3:.1f},{np.nanmax(peak)/1e3:.1f}] kOhm")

# Geometry prior
geom_ratio = 15.6 / 12.0   # c ~ kappa/t, same kappa -> t_bg/t_tg
print(f"\nGeometry-prior ratio c_bg/c_tg = t_tg/t_bg = 15.6/12 = {geom_ratio:.4f}")

# --- (n,D) calibration from chosen channel (sr1 default; will pick best below) ---
best = min(fits, key=lambda c: fits[c]["rms"])
slope = fits[best]["slope"]; intercept = fits[best]["intercept"]
ratio = -slope
# anchor c_tg at geometry prior, set c_bg from ratio
from sharpelab_nb.gates import stack_capacitance
c_tg = stack_capacitance([(15.6, 3)])
c_bg_geom = stack_capacitance([(12, 3), (0, 3.9)])
c_bg = ratio * c_tg
print(f"\nChosen channel for cal: {best} (lowest rms)")
print(f"c_tg(geom)={c_tg:.4e}  c_bg(geom)={c_bg_geom:.4e}  c_bg(from ratio)={c_bg:.4e}")

cal = a.GateCalibration(c_tg=c_tg, c_bg=c_bg)
# n_offset so fitted line maps to n=0: b is Vtg intercept at Vbg=0
b = intercept
n_at_line = cal.density(b, 0.0)
print(f"n at (Vtg={b:.3f},Vbg=0) before offset = {n_at_line:.3e} m^-2")
n_offset = -n_at_line
cal2 = a.GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=n_offset)
# closure: n along the fitted ridge should be ~0
vc = fits[best]["vcnp"][fits[best]["keep"]]
vb = Vbg[fits[best]["keep"]]
n_ridge = np.array([cal2.density(vt, vbg) for vt, vbg in zip(vc, vb)])
print(f"closure: |n| max along ridge = {np.abs(n_ridge).max():.3e} m^-2 (target ~0)")
print(f"n_offset = {n_offset:.3e} m^-2  -> CNP at (Vtg,Vbg=0) = {b:.3f} V")

np.save(os.path.join(SCR, "cnp_fits.npy"), fits, allow_pickle=True)

# --- Plot raw maps + ridge overlay ---
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
ext = [Vtg.min(), Vtg.max(), Vbg.min(), Vbg.max()]
for ax, cid, label in [(axes[0], "sr1", "sr1 T3-T4 |Rxx|"),
                       (axes[1], "sr2", "sr2 B4-B5 |Rxx|"),
                       (axes[2], "sr3", "sr3 T5-B6 Rxy (signed)")]:
    R = rg.R[cid]
    if cid == "sr3":
        im = ax.imshow(R/1e3, origin="lower", aspect="auto", extent=ext, cmap="RdBu_r",
                       vmin=-1, vmax=1)
        plt.colorbar(im, ax=ax, label="Rxy (kOhm)")
    else:
        im = ax.imshow(np.abs(R)/1e3, origin="lower", aspect="auto", extent=ext,
                       cmap="viridis", vmax=np.nanpercentile(np.abs(R), 99)/1e3)
        plt.colorbar(im, ax=ax, label="|Rxx| (kOhm)")
        f = fits.get(cid)
        if f:
            ax.scatter(f["vcnp"][f["keep"]], Vbg[f["keep"]], s=12, c="r", label="CNP ridge")
            ax.plot(np.polyval([f["slope"], f["intercept"]], Vbg), Vbg, "w--", lw=1.2,
                    label=f"fit slope {f['slope']:.2f}")
            ax.legend(loc="upper right", fontsize=8)
    ax.set_xlabel("V_tg (DC_bias) [V]"); ax.set_ylabel("V_bg (k_2400) [V]")
    ax.set_title(label)
fig.suptitle("QC0426 Run 0 — 0 T TG-BG gate map (Vsi=0, 0.5V/5nA)")
fig.tight_layout()
out = os.path.join(SCR, "run0_gatemap.png")
fig.savefig(out, dpi=110)
print("\nsaved", out)

# ===== Calibration consequences: D=0 line + accessible n-range (Step 2 inputs) =====
print("\n===== CALIBRATION SUMMARY =====")
print(f"CNP line:  V_tg = {slope:.4f}*V_bg + {intercept:.4f}   (ratio c_bg/c_tg = {ratio:.4f})")
print(f"c_tg={c_tg:.4e} F/m^2  c_bg={c_bg:.4e} F/m^2  n_offset={n_offset:.4e} m^-2  (scale=geometry prior)")
e = 1.602176634e-19
h = 6.62607015e-34
# D=0 line: c_tg*Vtg = c_bg*Vbg  -> Vtg = ratio*Vbg.  Clip to validators TG[-6,7], BG[-4.5,4.5]
def along_D0(Vbg):
    return ratio*Vbg
# realized BG range so both gates in range (Vtg=ratio*Vbg in [-6,7], Vbg in [-4.5,4.5])
vbg_lo = max(-4.5, -6.0/ratio); vbg_hi = min(4.5, 7.0/ratio)
print(f"\nD=0 line Vtg=ratio*Vbg; realized Vbg in [{vbg_lo:.3f},{vbg_hi:.3f}] (both gates in validators)")
for vbg in [vbg_lo, 0.0, vbg_hi]:
    vtg = along_D0(vbg)
    n, D = cal2.n_D(vtg, vbg)
    print(f"  Vbg={vbg:+.3f} Vtg={vtg:+.3f} -> n={n/1e16:+.3f}e16 m^-2 = {n/1e4/1e12:+.3f}e12 cm^-2, D={D/1e9:+.4f} GV/m")
# density extremes along D=0
n_lo = cal2.density(along_D0(vbg_lo), vbg_lo); n_hi = cal2.density(along_D0(vbg_hi), vbg_hi)
print(f"accessible |n| along D=0: hole to {n_lo/1e4/1e12:.2f}e12 cm^-2, electron to {n_hi/1e4/1e12:.2f}e12 cm^-2")

# Step 2 feasibility: F_L = (h/4e)*n ; Nyquist Delta(1/B)<=1/(2 F_L)
print("\n--- Step 2 feasibility (F_L = h n /4e) ---")
for ncm in [1.0e12, 2.0e12, 3.0e12]:
    nSI = ncm*1e4*1e12/1e12*1e0  # ncm in cm^-2 -> m^-2
    nSI = ncm*1e4  # cm^-2 -> m^-2 (1 cm^-2 = 1e4 m^-2)... careful
    nSI = ncm*1e4
    FL = h*nSI/(4*e)
    dinvB = 1/(2*FL)
    print(f"  n={ncm:.1f}e12 cm^-2: F_L={FL:.2f} T, Nyquist d(1/B)<={dinvB:.4f} 1/T  (e.g. need ~{1/dinvB:.1f} ... )")
