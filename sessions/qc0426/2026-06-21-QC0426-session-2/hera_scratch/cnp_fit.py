import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import fan_grids, resistance_grids, GateCalibration

fan = fan_grids("data/1")
ci = {c: i for i, c in enumerate(fan.cols)}
g = fan.data.reshape(fan.nrows, fan.nfast, len(fan.cols))
VTG = g[:, :, ci["DC_bias"]]          # (41,81) fast axis values
VBG = g[:, 0, ci["k_2400_volt"]]      # (41,)  slow axis values per row
tg_axis = VTG[0]                       # fast axis grid (same each row)
rg = resistance_grids(fan)

def extract_ridge(Rgrid):
    A = np.abs(Rgrid)
    As = gaussian_filter1d(A, sigma=1.5, axis=1)   # smooth along TG
    jpk = np.argmax(As, axis=1)
    vtg_cnp = tg_axis[jpk]
    rpk = A[np.arange(len(jpk)), jpk]
    edge = (jpk <= 1) | (jpk >= fan.nfast - 2)     # edge-clipped guard
    return vtg_cnp, rpk, jpk, edge

fits = {}
for ch in ("sr1", "sr2"):
    vtg_cnp, rpk, jpk, edge = extract_ridge(rg.R[ch])
    keep = ~edge
    # continuity guard: drop points >3*std from a first-pass linear fit
    c0 = np.polyfit(VBG[keep], vtg_cnp[keep], 1)
    resid = vtg_cnp - np.polyval(c0, VBG)
    good = keep & (np.abs(resid) < 3 * np.std(resid[keep]))
    slope, intc = np.polyfit(VBG[good], vtg_cnp[good], 1)
    rms = np.std(vtg_cnp[good] - np.polyval([slope, intc], VBG[good]))
    fits[ch] = dict(slope=slope, intc=intc, rms=rms, ngood=int(good.sum()),
                    nedge=int(edge.sum()), vtg_cnp=vtg_cnp, good=good, rpk=rpk)
    print(f"{ch}: slope dVtg/dVbg = {slope:+.4f}  -> c_bg/c_tg = {-slope:.4f} | "
          f"intercept(Vtg@Vbg=0) = {intc:+.4f} V | rms {rms*1e3:.1f} mV | "
          f"ngood {good.sum()}/{fan.nrows} (edge-clipped {edge.sum()})")

print(f"\ngeometry-prior ratio c_bg/c_tg = t_tg/t_bg = 15.6/12 = {15.6/12:.4f}")

# Cross-channel agreement
s1, s2 = fits["sr1"]["slope"], fits["sr2"]["slope"]
print(f"cross-channel slope agreement: {abs(s1-s2)/abs(0.5*(s1+s2))*100:.1f}% "
      f"(rms ~{0.5*(fits['sr1']['rms']+fits['sr2']['rms'])*1e3:.1f} mV)")

# Build calibration: anchor c_tg at geometry prior (t_tg=15.6nm); set ratio from fit (use sr1)
ratio = -fits["sr1"]["slope"]
t_tg = 15.6e-9
t_bg_eff = t_tg / ratio            # impose fitted ratio, keep c_tg absolute (geometry-prior scale)
cal0 = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0)
# n_offset so the fitted CNP line maps to n=0: at Vbg=0, Vtg_cnp = intercept
b = fits["sr1"]["intc"]
n0, d0 = cal0.n_D(b, 0.0)
cal = GateCalibration.from_thicknesses(t_tg, t_bg_eff, 0.0, n_offset=-n0)
print(f"\nratio used (sr1) = {ratio:.4f} -> t_bg_eff = {t_bg_eff*1e9:.3f} nm")
print(f"n_offset set so CNP(Vtg={b:.3f},Vbg=0) -> n=0; raw n there was {n0:.3e} m^-2")

# Closure check: n along fitted ridge should be ~0
vtg_line = np.polyval([fits["sr1"]["slope"], fits["sr1"]["intc"]], VBG)
n_line, D_line = cal.n_D(vtg_line, VBG)
print(f"closure: |n| residual along fitted ridge max = {np.abs(n_line).max():.3e} m^-2 "
      f"({np.abs(n_line).max()/1e16:.3e} e12 cm^-2); D range {D_line.min():.3e}..{D_line.max():.3e} V/m")

# ---- plot: map (log|R|) + ridge + fit, per channel ----
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, ch in zip(axes, ("sr1", "sr2")):
    A = np.abs(rg.R[ch])
    im = ax.pcolormesh(tg_axis, VBG, np.log10(A + 1), shading="nearest", cmap="viridis")
    f = fits[ch]
    ax.plot(f["vtg_cnp"][f["good"]], VBG[f["good"]], "r.", ms=5, label="CNP argmax")
    ax.plot(np.polyval([f["slope"], f["intc"]], VBG), VBG, "w--", lw=1.2,
            label=f"fit slope {f['slope']:+.3f}")
    ax.set_xlabel("V_tg (DC_bias) [V]"); ax.set_ylabel("V_bg [V]")
    ax.set_title(f"{ch}  log10|Rxx|  (run 1, B=0)"); ax.legend(loc="upper right", fontsize=8)
    fig.colorbar(im, ax=ax, label="log10(|R|+1)")
fig.tight_layout(); fig.savefig("hera_scratch/cnp_map.png", dpi=110)
print("saved hera_scratch/cnp_map.png")
