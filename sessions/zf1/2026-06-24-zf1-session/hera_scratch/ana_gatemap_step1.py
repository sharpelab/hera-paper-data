"""Step-1 gatemap analysis (data/4): TSV-first reform, leakage check,
CNP-ridge fit -> cap ratio, candidate-region hunt, PNGs. Scratch-first;
promote the clean version to the ana notebook after."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, summarize_run
from sharpelab_nb.gates import stack_capacitance, calc_nD

RUN = "data/4"
NSLOW, NFAST = 81, 69
V_TG = np.linspace(-7.0, 6.0, NSLOW)   # slow
V_BG = np.linspace(-4.0, 4.2, NFAST)   # fast
GAINV = 100.0
I_BIAS = 1e-9

r = open_run(RUN)
print(summarize_run(r))
print("interrupted:", r.interrupted)

def colp(name):  # planned (first occurrence) col
    idxs = r.col_indices(name)
    return r.col_at(idxs[0])

n_rows = len(colp("sr830_3_X"))
print("rows:", n_rows, "expected:", NSLOW*NFAST)
full = (n_rows == NSLOW*NFAST)
nfull = n_rows // NFAST  # complete slow rows available
print("complete slow rows:", nfull, "/", NSLOW)

# --- leakage (final) ---
itg = np.abs(r.col("k_tg_curr")); ibg = np.abs(r.col("k_bg_curr"))
print("LEAKAGE |I_tg|max[pA]=%.1f |I_bg|max[pA]=%.1f  pts>100pA: tg=%d bg=%d"
      % (itg.max()*1e12, ibg.max()*1e12, int((itg>1e-10).sum()), int((ibg>1e-10).sum())))

# --- reform 4T / 2T R grids (use available complete rows) ---
def grid(name):
    x = colp(name)[:nfull*NFAST].reshape(nfull, NFAST)
    return (x / GAINV) / I_BIAS
R4 = grid("sr830_3_X")   # 4T (30-31)
R2 = grid("sr830_2_X")   # 2T (5-4)
vtg = V_TG[:nfull]
print("R4 (4T) range[ohm]: %.1f .. %.1f   median %.1f" % (np.nanmin(R4), np.nanmax(R4), np.nanmedian(R4)))

# --- CNP ridge from 4T, per slow row ---
cnp_vbg, cnp_vtg = [], []
for i in range(nfull):
    row = gaussian_filter1d(np.nan_to_num(R4[i]), 1.2)
    j = int(np.argmax(row))
    if j in (0, NFAST-1):     # edge-clipped: CNP not in window
        continue
    cnp_vbg.append(V_BG[j]); cnp_vtg.append(vtg[i])
cnp_vbg = np.array(cnp_vbg); cnp_vtg = np.array(cnp_vtg)
print("CNP ridge rows used:", len(cnp_vtg), "/", nfull)

# robust linear fit V_tg vs V_bg with iterative outlier rejection
def robust_fit(x, y, niter=3):
    m = np.ones(len(x), bool)
    for _ in range(niter):
        s, b = np.polyfit(x[m], y[m], 1)
        resid = y - (s*x + b)
        m = np.abs(resid) < 2*np.std(resid[m]) + 1e-9
    return s, b, m
if len(cnp_vtg) >= 5:
    slope, icpt, mask = robust_fit(cnp_vbg, cnp_vtg)  # V_tg = slope*V_bg + icpt
    ratio = -slope                                    # c_bg/c_tg = -dVtg/dVbg
    print("CNP fit: dVtg/dVbg = %.4f  intercept = %.4f  (rows kept %d/%d)"
          % (slope, icpt, int(mask.sum()), len(mask)))
    print("=> c_bg/c_tg = %.4f   (prior 1.18, dev %.1f%%)" % (ratio, 100*(ratio-1.18)/1.18))
else:
    slope = icpt = ratio = None
    print("CNP fit skipped (too few ridge rows)")

# --- reproject to (n,D) with fitted ratio (absolute scale = geometry prior) ---
c_tg = stack_capacitance([(23.6,3)]); c_bg_prior = stack_capacitance([(20.0,3)])
c_bg = c_tg*ratio if ratio else c_bg_prior
n_off = -calc_nD(icpt, 0.0, c_tg, c_bg)[0] if ratio else 0.0   # CNP -> n=0
TG, BG = np.meshgrid(vtg, V_BG, indexing="ij")
nmap, Dmap = calc_nD(TG, BG, c_tg, c_bg, n_offset=n_off)   # n[cm^-2], D[V/nm] per house convention

# --- candidate hunt: low 4T R away from CNP, in the prior SC region ---
# prior: D<0 (holes->WSe2), |D|>~0.5 V/nm, n ~ -4..-6 e11 cm^-2
mask_reg = (Dmap < -0.3) & (nmap < 0)
if mask_reg.any():
    Rsel = np.where(mask_reg, R4, np.nan)
    k = np.nanargmin(Rsel)
    ii, jj = np.unravel_index(k, R4.shape)
    print("LOW-R candidate in D<0 region: R=%.2f ohm at V_tg=%.2f V_bg=%.2f  (n=%.3e cm^-2, D=%.3f V/nm)"
          % (R4[ii,jj], vtg[ii], V_BG[jj], nmap[ii,jj], Dmap[ii,jj]))

# --- PNGs ---
fig, ax = plt.subplots(1, 2, figsize=(13,5))
im0 = ax[0].pcolormesh(V_BG, vtg, np.clip(R4,0,None), shading="auto",
                       norm=matplotlib.colors.LogNorm(vmin=max(1,np.nanmin(R4[R4>0])), vmax=np.nanmax(R4)))
if ratio: ax[0].plot(cnp_vbg, slope*cnp_vbg+icpt, "w--", lw=1)
ax[0].set_xlabel("V_bg (V)"); ax[0].set_ylabel("V_tg (V)"); ax[0].set_title("4T Rxx (log) + CNP fit"); fig.colorbar(im0, ax=ax[0])
im1 = ax[1].pcolormesh(nmap, Dmap, np.clip(R4,0,None), shading="auto",
                       norm=matplotlib.colors.LogNorm(vmin=max(1,np.nanmin(R4[R4>0])), vmax=np.nanmax(R4)))
ax[1].axhline(-0.5, color="c", ls=":"); ax[1].set_xlabel("n (cm^-2)"); ax[1].set_ylabel("D (V/nm)")
ax[1].set_title("4T Rxx -> (n,D)"); fig.colorbar(im1, ax=ax[1])
plt.tight_layout(); plt.savefig("hera_scratch/gatemap_step1_4T.png", dpi=110)
print("saved hera_scratch/gatemap_step1_4T.png")
