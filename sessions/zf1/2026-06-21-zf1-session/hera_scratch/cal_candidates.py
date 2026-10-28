import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d, gaussian_filter
from hera.analysis import open_run, GateCalibration

r = open_run("data/2"); cfg = json.load(open("data/2/metadata.json"))["measurement_config"]
N_bg, N_tg = 121, 81
tg = r.col("k_tg_volt").reshape(N_tg,N_bg)
bg = r.col("k_bg_volt").reshape(N_tg,N_bg)
I  = (r.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg,N_bg)
V4 = (r.col("sr830_3_X")/cfg["sr3_gain"]).reshape(N_tg,N_bg)
Rxx = V4/I
TGv = tg[:,0]            # per-row TG
BGv = bg[0,:]           # per-row BG axis

# ---- caps (prior; ratio confirmed by slope below) ----
EPS0=8.8541878128e-12; E=1.602176634e-19
kap=3.0; t_tg=23.6e-9; t_bg=20e-9
c_tg=EPS0*kap/t_tg; c_bg=EPS0*kap/t_bg
print(f"prior c_bg/c_tg = {c_bg/c_tg:.3f}")

# ---- CNP ridge extraction (diagonal channel CNP), windowed around prior ----
slope_prior = -c_tg/c_bg            # dBG/dTG along n=0
bg_cnp=[]; tg_used=[]
for j in range(N_tg):
    bge = slope_prior*TGv[j]        # expected BG_cnp (intercept~0)
    win = (BGv > bge-1.2) & (BGv < bge+1.2)
    if win.sum()<5: continue
    prof = gaussian_filter1d(Rxx[j], 1.5)
    idx = np.where(win)[0]
    k = idx[np.nanargmax(prof[idx])]
    # reject edge-clipped
    if k<=1 or k>=N_bg-2: continue
    bg_cnp.append(BGv[k]); tg_used.append(TGv[j])
bg_cnp=np.array(bg_cnp); tg_used=np.array(tg_used)
m,b = np.polyfit(tg_used, bg_cnp, 1)        # BG_cnp = m*TG + b
resid = np.std(bg_cnp-(m*tg_used+b))
ratio_fit = -1.0/m                          # c_bg/c_tg = -1/(dBG/dTG)
print(f"fitted ridge: BG_cnp = {m:.4f}*TG + {b:.4f}   resid={resid*1e3:.0f} mV")
print(f"cap ratio c_bg/c_tg: prior {c_bg/c_tg:.3f}  fitted {ratio_fit:.3f}")
print(f"CNP at TG=0 -> BG={b:.3f} V (run1 gave -0.017)")

# ---- n_offset so CNP ridge -> n=0 (using prior caps) ----
n_raw_on_ridge = (c_tg*tg_used + c_bg*(m*tg_used+b))/E
n_offset = -np.mean(n_raw_on_ridge)
cal = GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=n_offset, D_offset=0.0)
n,D = cal.n_D(tg, bg)
n_cm = n*1e-4            # cm^-2
D_vnm = D*1e-9          # V/nm
print(f"n range {n_cm.min():.2e}..{n_cm.max():.2e} cm^-2;  D range {D_vnm.min():.2f}..{D_vnm.max():.2f} V/nm")
# closure
nclose = (c_tg*tg_used + c_bg*(m*tg_used+b))/E + n_offset
print(f"closure |n| on ridge max = {np.max(np.abs(nclose))*1e-4:.2e} cm^-2")

# ---- plot Rxx in (n,D) ----
fig,ax=plt.subplots(1,2,figsize=(13,5.5))
sc=ax[0].scatter(n_cm.ravel()/1e11, D_vnm.ravel(), c=np.clip(Rxx.ravel(),0,120), s=6, cmap='inferno')
ax[0].set_xlabel("n (1e11 cm^-2)"); ax[0].set_ylabel("D (V/nm)"); ax[0].set_title("4T Rxx (Ω) in (n,D)")
plt.colorbar(sc,ax=ax[0])
# candidate prior box: D<0, |D|>=0.5, n in [-6,-4]e11
ax[0].add_patch(plt.Rectangle((-6,-1.0),2,0.5,fill=False,ec='cyan',lw=2))
ax[0].axhline(0,color='gray',lw=.5); ax[0].axvline(0,color='gray',lw=.5)

# residual map: Rxx minus a smooth background (highlight local dips/domes)
Rs = gaussian_filter(np.clip(Rxx,0,200), 3)
dR = np.clip(Rxx,0,200)-Rs
sc=ax[1].scatter(n_cm.ravel()/1e11, D_vnm.ravel(), c=dR.ravel(), s=6, cmap='coolwarm', vmin=-15, vmax=15)
ax[1].set_xlabel("n (1e11 cm^-2)"); ax[1].set_ylabel("D (V/nm)"); ax[1].set_title("Rxx - smooth bkg (local dips=blue)")
plt.colorbar(sc,ax=ax[1]); ax[1].axhline(0,color='gray',lw=.5)
ax[1].add_patch(plt.Rectangle((-6,-1.0),2,0.5,fill=False,ec='k',lw=2))
plt.tight_layout(); plt.savefig("hera_scratch/cal_nD.png",dpi=100); print("saved cal_nD.png")

# ---- focus: hole side, high |D| — list lowest-Rxx pockets away from CNP ----
mask = (n_cm < -2e11) & (np.abs(D_vnm) > 0.4) & (np.abs(n)>0)  # finite hole density, away from CNP
# only off-CNP (Rxx not the ridge): exclude points within 0.3e11 of n=0
offcnp = mask & (np.abs(n_cm) > 0.5e11)
print(f"\nHole-side high-|D| metallic Rxx: median {np.nanmedian(Rxx[offcnp]):.1f} Ω, "
      f"min {np.nanmin(Rxx[offcnp]):.1f} Ω")
# candidate prior box stats
box = (n_cm>-6e11)&(n_cm<-4e11)&(D_vnm<-0.5)&(D_vnm>-1.2)
if box.sum()>0:
    print(f"PRIOR candidate box (n[-6,-4]e11, D[-1.2,-0.5]): {box.sum()} pts, "
          f"Rxx median {np.nanmedian(Rxx[box]):.1f} Ω min {np.nanmin(Rxx[box]):.1f} Ω")
else:
    print("PRIOR candidate box: NO points in map coverage")
