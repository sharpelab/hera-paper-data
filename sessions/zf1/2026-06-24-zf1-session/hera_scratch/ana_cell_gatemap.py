# Run data/4 — Step 1 pristine-field gate map (raw first)
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance, calc_nD
g4 = run(4); print(summarize_run(g4))
NSLOW, NFAST = 81, 69
V_TG = np.linspace(-7, 6, NSLOW); V_BG = np.linspace(-4, 4.2, NFAST)
def _gp(g, name):
    return g.col_at(g.col_indices(name)[0])
R4 = (_gp(g4, "sr830_3_X").reshape(NSLOW, NFAST) / 100.0) / 1e-9   # 4T Rxx [ohm] (gain 100, I_bias 1 nA)
import matplotlib.colors as mc
ln = mc.LogNorm(vmin=2, vmax=np.nanmax(R4))

# CNP ridge (4T) per slow row + robust linear fit -> cap ratio
cb, ct = [], []
for i in range(NSLOW):
    j = int(np.argmax(gaussian_filter1d(np.nan_to_num(R4[i]), 1.2)))
    if j in (0, NFAST-1):
        continue
    cb.append(V_BG[j]); ct.append(V_TG[i])
cb, ct = np.array(cb), np.array(ct)
m = np.ones(len(cb), bool)
for _ in range(3):
    sl, ic = np.polyfit(cb[m], ct[m], 1); res = ct - (sl*cb + ic); m = np.abs(res) < 2*np.std(res[m]) + 1e-9
ratio = -sl
print(f"CNP fit: dVtg/dVbg={sl:.4f}  intercept={ic:.4f}  ->  c_bg/c_tg={ratio:.4f}  (prior 1.18, dev {100*(ratio-1.18)/1.18:+.1f}%)")

# (n,D) reprojection with fitted ratio, CNP -> n=0
c_tg = stack_capacitance([(23.6,3)]); c_bg = c_tg*ratio
n_off = -calc_nD(ic, 0.0, c_tg, c_bg)[0]
TG, BG = np.meshgrid(V_TG, V_BG, indexing="ij")
nmap, Dmap = calc_nD(TG, BG, c_tg, c_bg, n_offset=n_off)   # n [1e12 cm^-2], D [V/nm]

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].pcolormesh(V_BG, V_TG, np.clip(R4,1,None), shading="auto", norm=ln)
ax[0].plot(cb, sl*cb+ic, "w--", lw=1)
ax[0].set_xlabel("V_bg (V)"); ax[0].set_ylabel("V_tg (V)"); ax[0].set_title("data/4: 4T Rxx (log) + CNP fit")
im = ax[1].pcolormesh(nmap, Dmap, np.clip(R4,1,None), shading="auto", norm=ln)
ax[1].set_xlabel("n (1e12 cm^-2)"); ax[1].set_ylabel("D (V/nm)"); ax[1].set_title("4T Rxx -> (n,D); CNP at n=0")
fig.colorbar(im, ax=ax[1], label="ohm"); plt.tight_layout(); plt.show()
print("leakage: |I_tg|max[pA]=%.0f |I_bg|max[pA]=%.0f" %
      (np.abs(g4.col('k_tg_curr')).max()*1e12, np.abs(g4.col('k_bg_curr')).max()*1e12))
