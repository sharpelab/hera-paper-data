# (2) cap ratio from CNP slope, (n,D) projection, candidate read
EPS0, E = 8.8541878128e-12, 1.602176634e-19
c_tg = EPS0*3/23.6e-9; c_bg = EPS0*3/20e-9
TGv, BGv = TG[:,0], BG[0,:]
slope_prior = -c_tg/c_bg
bg_cnp, tg_used = [], []
for j in range(N_tg):
    bge = slope_prior*TGv[j]
    win = (BGv > bge-1.2) & (BGv < bge+1.2)
    if win.sum() < 5: continue
    idx = np.where(win)[0]; prof = gaussian_filter1d(RXX[j], 1.5)
    k = idx[np.nanargmax(prof[idx])]
    if 1 < k < N_bg-2: bg_cnp.append(BGv[k]); tg_used.append(TGv[j])
bg_cnp, tg_used = np.array(bg_cnp), np.array(tg_used)
m, b = np.polyfit(tg_used, bg_cnp, 1)
ratio_fit = -1.0/m
n_offset = -c_bg*b/E
print(f"CNP ridge BG = {m:.4f}*TG + {b:+.4f}  (resid {np.std(bg_cnp-(m*tg_used+b))*1e3:.0f} mV)")
print(f"cap ratio c_bg/c_tg: prior 1.180  fitted {ratio_fit:.3f}   CNP@TG=0 -> BG={b:+.3f} V")

cal2 = GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=n_offset, D_offset=0.0)
n, D = cal2.n_D(TG, BG); n_cm = n*1e-4; D_vnm = D*1e-9

fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.5))
sc = ax[0].scatter(n_cm.ravel()/1e11, D_vnm.ravel(), c=np.clip(RXX.ravel(),0,120), s=6, cmap='inferno')
ax[0].set(title="4T Rxx (Ω) in (n,D)", xlabel="n (1e11 cm^-2)", ylabel="D (V/nm)")
ax[0].axhline(0,c='gray',lw=.5); ax[0].axvline(0,c='gray',lw=.5); plt.colorbar(sc, ax=ax[0])
ax[0].add_patch(plt.Rectangle((-6,-0.76),2,0.26,fill=False,ec='cyan',lw=2))  # accessible candidate region
Rs = gaussian_filter(np.clip(RXX,0,200), 3); dR = np.clip(RXX,0,200)-Rs
sc = ax[1].scatter(n_cm.ravel()/1e11, D_vnm.ravel(), c=dR.ravel(), s=6, cmap='coolwarm', vmin=-15, vmax=15)
ax[1].set(title="Rxx − smooth bkg  (local dips = blue)", xlabel="n (1e11 cm^-2)", ylabel="D (V/nm)")
ax[1].axhline(0,c='gray',lw=.5); plt.colorbar(sc, ax=ax[1])
plt.tight_layout(); plt.show()

box = (n_cm>-6e11)&(n_cm<-4e11)&(D_vnm<-0.5)&(D_vnm>-0.76)
print(f"max |D| reached: {np.abs(D_vnm).max():.2f} V/nm")
print(f"candidate box (n[-6,-4]e11, D[-0.76,-0.5]): {box.sum()} pts, "
      f"Rxx median {np.nanmedian(RXX[box]):.1f} Ω  min {np.nanmin(RXX[box]):.1f} Ω")
