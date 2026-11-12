import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

rid = sys.argv[1] if len(sys.argv)>1 else "5"
run = open_run(f"data/{rid}"); print(summarize_run(run)); print("interrupted:", run.interrupted)
Vdc = run.col_at(run.cols.index("dc205_1_voltage"))   # swept axis (also fp'd)
Idc = Vdc/1e8 * 1e9                              # nA  (100 MOhm bias resistor)
Iac = run.col("sr830_1_X")/(-1e6)
dVdI = np.abs((run.col("sr830_3_X")/100.0)/Iac)  # Ohm
o = np.argsort(Idc); Idc, dVdI = Idc[o], dVdI[o]
T = run.col("T"); itg=run.col("k_tg_curr"); ibg=run.col("k_bg_curr")
print(f"T={np.median(T)*1e3:.1f} mK; leakage |Itg|max={np.abs(itg).max():.1e} |Ibg|max={np.abs(ibg).max():.1e}; Iac med={np.median(Iac)*1e9:.3f} nA")

zb = dVdI[np.abs(Idc)<2].mean()                  # zero-bias dV/dI
nm = dVdI[np.abs(Idc)>120].mean()                # normal-state dV/dI
print(f"\nzero-bias dV/dI = {zb:.2f} Ω ; normal-state dV/dI = {nm:.1f} Ω")
thr = zb + 0.5*(nm-zb)
def ic_side(sign):
    m = (np.sign(Idc)==sign) & (dVdI>=thr)
    return np.abs(Idc[m]).min() if m.any() else np.nan
icp, icn = ic_side(+1), ic_side(-1)
print(f"threshold (half-rise) = {thr:.1f} Ω")
print(f"Ic+ = {icp:.1f} nA   Ic- = {icn:.1f} nA   (lobe = supercurrent if dV/dI~0 plateau below |Ic|)")
print(f"SC-lobe verdict: {'SUPERCURRENT-like (flat low-dVdI plateau + rise at Ic)' if zb<0.3*nm and np.isfinite(icp) else 'NO clear lobe (ohmic? check plot)'}")

fig, ax = plt.subplots(figsize=(8,5))
ax.plot(Idc, dVdI, ".-", ms=4)
ax.axhline(thr, color="grey", ls=":", lw=.8, label=f"half-rise {thr:.0f}Ω")
for ic,c in ((icp,"r"),(-icn,"b")):
    if np.isfinite(ic): ax.axvline(ic, color=c, ls="--", lw=.8)
ax.set_xlabel("I_dc (nA)"); ax.set_ylabel("dV/dI (Ω)")
ax.set_title(f"Run {rid}: bias spectroscopy at n=−4.65e11, D=−0.65  (Ic±≈{icp:.0f}/{icn:.0f} nA)")
ax.legend(); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(f"hera_scratch/biasspec_run{rid}.png", dpi=120)
print(f"saved hera_scratch/biasspec_run{rid}.png")
