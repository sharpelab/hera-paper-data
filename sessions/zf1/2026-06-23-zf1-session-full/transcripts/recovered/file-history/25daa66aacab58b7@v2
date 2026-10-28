import numpy as np
from hera.analysis import open_run, summarize_run

run = open_run('data/4')
print(summarize_run(run))
print('interrupted:', run.interrupted)

# --- leakage (whole map went to the validator corners) ---
itg = np.abs(run.col('k_tg_curr')); ibg = np.abs(run.col('k_bg_curr'))
print(f"\nLEAKAGE  k_tg_curr max |I| = {itg.max():.3e} A   (med {np.median(itg):.2e})")
print(f"         k_bg_curr max |I| = {ibg.max():.3e} A   (med {np.median(ibg):.2e})")
print(f"  rows over 1 nA: tg {np.sum(itg>1e-9)}  bg {np.sum(ibg>1e-9)}")
print(f"  rows over 100 pA: tg {np.sum(itg>1e-10)}  bg {np.sum(ibg>1e-10)}")

# --- geometry / axes (regular grid; avoid duplicate-col ambiguity) ---
NT, NB = 41, 61
V_tg = np.linspace(-7.0, 6.0, NT)   # slow
V_bg = np.linspace(-4.0, 4.2, NB)   # fast
n_rows = run.col('sr830_3_X').size
print(f"\nrows {n_rows} (expect {NT*NB})")

def R_of(name, gain=100.0, ibias=1e-9):
    x = run.col(name)[:NT*NB].reshape(NT, NB)
    return (x/gain)/ibias   # 4-wire: R = (X/gain)/I_bias

R4 = R_of('sr830_3_X')   # 4T longitudinal 30-31
R2 = R_of('sr830_2_X')   # 2T 5-4
print(f"\nR4 (4T) range: {np.nanmin(R4):.1f} .. {np.nanmax(R4):.3e}  Ohm")
print(f"R2 (2T) range: {np.nanmin(R2):.1f} .. {np.nanmax(R2):.3e}  Ohm")
# rail check on R4
rail = np.isclose(R4, 2180, rtol=0.03)
print(f"R4 railed (~2.18k) fraction: {rail.mean():.2%}")

# --- CNP ridge: per TG row, BG of max resistance. Use 2T (4T rails). ---
from scipy.ndimage import gaussian_filter1d
Vbg_cnp = np.full(NT, np.nan)
edge_clipped = []
for i in range(NT):
    prof = gaussian_filter1d(R2[i], 1.5)
    j = int(np.nanargmax(prof))
    if j <= 1 or j >= NB-2:
        edge_clipped.append(i)            # CNP at window edge -> exclude
        continue
    Vbg_cnp[i] = V_bg[j]
good = ~np.isnan(Vbg_cnp)
print(f"\nCNP located in {good.sum()}/{NT} rows; edge-clipped rows (TG idx): {edge_clipped}")

# fit V_bg_cnp = m*V_tg + b   (fast=BG, slow=TG)
m, b = np.polyfit(V_tg[good], Vbg_cnp[good], 1)
resid = Vbg_cnp[good] - (m*V_tg[good]+b)
print(f"fit: V_bg_cnp = {m:.4f}*V_tg + {b:.4f}   (rms resid {np.std(resid):.3f} V)")
# along CNP n=0: c_tg dVtg + c_bg dVbg = 0 -> dVbg/dVtg = m = -c_tg/c_bg
cbg_over_ctg = -1.0/m
print(f"\nCAP RATIO  c_bg/c_tg = -1/m = {cbg_over_ctg:.3f}")
print(f"  geometry prior (t_tg/t_bg = 23.6/20)         = {23.6/20:.3f}")
print(f"  device-card stated cap ratio                 = 1.18")

np.savez('hera_scratch/map1_reformed.npz', V_tg=V_tg, V_bg=V_bg, R4=R4, R2=R2,
         Vbg_cnp=Vbg_cnp, m=m, b=b, cbg_over_ctg=cbg_over_ctg)
print("\nsaved hera_scratch/map1_reformed.npz")
