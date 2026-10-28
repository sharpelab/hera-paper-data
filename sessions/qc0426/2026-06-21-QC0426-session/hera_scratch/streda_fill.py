import os, numpy as np, hera.analysis as a
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
MDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCR = os.path.join(MDIR, "hera_scratch")
run = a.open_run(os.path.join(MDIR, "data", "4"))
fg = a.fan_grids(run); B = np.asarray(fg.slow)
rg = a.resistance_grids(fg); R1 = rg.R["sr1"]  # (rows, ncol)
ncol = R1.shape[1]
ns_cm = np.linspace(-0.7, -2.5, ncol)             # 1e12 cm^-2 (hole)
n_si = np.abs(ns_cm) * 1e16                         # m^-2
e=1.602176634e-19; h=6.62607015e-34
phi0 = h/e

# filling nu = n / (eB/h) = n*h/(eB) at each (B-row, n-col)
fig, ax = plt.subplots(1, 2, figsize=(14, 5))
# ρxx vs nu at several high-B rows; look for minima fillings
for Btarget in [7.9, 6.5, 5.0, 4.0]:
    r = int(np.argmin(np.abs(B - Btarget)))
    Brow = B[r]
    nu = n_si * h / (e * Brow)
    rxx = R1[r]                # Rxx vs n at this B
    bg = gaussian_filter1d(rxx, 10)          # smooth n-background
    dr = gaussian_filter1d(rxx - bg, 1.0)    # detrended oscillation
    ax[0].plot(nu, dr/np.abs(dr).max() + Btarget, lw=1, label=f"B={Brow:.1f}T")
    mins, _ = find_peaks(-dr, prominence=np.abs(dr).max()*0.15)
    for mi in mins:
        ax[0].plot(nu[mi], dr[mi]/np.abs(dr).max() + Btarget, 'kv', ms=4)
    print(f"B={Brow:.2f}T: dRxx minima at nu = {np.round(np.sort(nu[mins]),1)}")
ax[0].set_xlabel("filling ν = n·h/(eB)"); ax[0].set_ylabel("Rxx (Ω)"); ax[0].set_title("Rxx vs ν (minima = LL gaps)")
ax[0].set_xlim(0, 16); ax[0].legend(fontsize=8)
for x in range(2, 16, 2):
    ax[0].axvline(x, color='b', ls=':', lw=0.4)   # even fillings
for x in range(4, 16, 4):
    ax[0].axvline(x, color='r', ls='--', lw=0.6)   # multiples of 4

# Streda: dip lines in (n,B). Track a few minima families across B-rows.
# For each B-row find Rxx minima in n; scatter in (n, B).
alln=[]; allB=[]
for r in range(0, len(B), 2):
    Brow=B[r]
    if Brow<1.5: continue
    rs=gaussian_filter1d(R1[r]-gaussian_filter1d(R1[r],10),1.0)
    mins,_=find_peaks(-rs, prominence=np.abs(rs).max()*0.15)
    for mi in mins:
        alln.append(n_si[mi]); allB.append(Brow)
alln=np.array(alln); allB=np.array(allB)
ax[1].scatter(alln/1e16, allB, s=4, c='k')
# overlay constant-nu lines n = nu*eB/h
for nu in [2,4,6,8,10,12]:
    bb=np.linspace(1.5,7.9,50); nn=nu*e*bb/h/1e16
    ax[1].plot(nn, bb, ('r--' if nu%4==0 else 'b:'), lw=0.7)
    ax[1].text(nu*e*7.9/h/1e16, 7.95, f"ν={nu}", fontsize=6)
ax[1].set_xlabel("|n| (1e12 cm⁻²)"); ax[1].set_ylabel("B (T)"); ax[1].set_title("Rxx minima + constant-ν lines (red=ν%4=0, blue=even)")
ax[1].set_xlim(0.5,2.6); ax[1].set_ylim(1.5,8.2)
fig.suptitle("Run 4 fan — Landau-level filling analysis (degeneracy discriminator)")
fig.tight_layout(); out=os.path.join(SCR,"run4_streda.png"); fig.savefig(out,dpi=110); print("saved",out)
