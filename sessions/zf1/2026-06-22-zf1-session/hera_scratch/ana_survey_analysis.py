# --- Run 2 analysis: cap-ratio refinement + candidate hunt ---
from scipy.ndimage import gaussian_filter1d
tg = f2.slow
pred = lambda vt: -0.850*vt + 0.133            # recon prior, for CNP search window
cnp_bg = np.full(len(tg), np.nan)
for i in range(len(tg)):
    p = pred(tg[i])
    if not (-3.7 <= p <= 3.9): continue
    bg = VB[i]; sel = np.abs(bg-p) <= 1.3
    if sel.sum() < 5: continue
    cnp_bg[i] = bg[sel][int(np.argmax(gaussian_filter1d(Rxx[i][sel],1.0)))]
gd = np.isfinite(cnp_bg)
slope, b0 = np.polyfit(tg[gd], cnp_bg[gd], 1); resid = cnp_bg[gd]-(slope*tg[gd]+b0)
print(f"CAP-RATIO (4T CNP, {gd.sum()} in-window rows): Vbg={slope:+.4f}·Vtg{b0:+.4f}")
print(f"  c_bg/c_tg = {-1/slope:.4f}  (geometry prior 1.18)  resid rms={np.std(resid):.4f} V")

# candidate hunt
metal = np.abs(N) > 1.0
win = (D<=-0.35)&(D>=-0.65)&(N<=-3.0)&(N>=-8.0)
print(f"\nmetallic background Rxx median = {np.median(Rxx[metal]):.1f} Ω")
print(f"proximity-SC window Rxx: min={Rxx[win].min():.1f} med={np.median(Rxx[win]):.1f} max={Rxx[win].max():.1f} Ω")
print(f"hole-side (n<0) sub-6Ω pockets: {((Rxx<6)&(N<0)&metal).sum()}  -> {'NONE' if ((Rxx<6)&(N<0)&metal).sum()==0 else 'present'}")

# low-R focused map to show absence of suppression
fig, ax = plt.subplots(1, 2, figsize=(14,5))
pc=ax[0].pcolormesh(tg, VB[0], np.clip(Rxx,0,40).T, vmin=0, vmax=40, shading="nearest", cmap="inferno")
ax[0].plot(tg[gd], cnp_bg[gd], "c.", ms=2); ax[0].plot(tg, slope*tg+b0, "w-", lw=.7)
ax[0].set_xlabel("V_tg (V)"); ax[0].set_ylabel("V_bg (V)"); ax[0].set_title("Rxx linear 0–40 Ω (suppression hunt)"); fig.colorbar(pc,ax=ax[0])
m=(D<=-0.2)&(D>=-0.78)&(N<=0)&(N>=-12)
sc=ax[1].scatter(N[m],D[m],c=np.clip(Rxx[m],0,40),vmin=0,vmax=40,s=12,cmap="inferno")
ax[1].axhline(-0.5,color="c",ls=":",lw=.7); ax[1].axvline(-5,color="c",ls=":",lw=.7)
ax[1].set_xlabel("n (1e11 cm⁻²)"); ax[1].set_ylabel("D (V/nm)"); ax[1].set_title("Hole-side D<0 zoom, Rxx 0–40 Ω"); fig.colorbar(sc,ax=ax[1])
plt.show()
