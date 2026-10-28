# (2) analysis: CNP location + 4T SNR
icnp = int(np.nanargmax(r2))
r3s  = gaussian_filter1d(r3, 3)
ipk  = int(np.nanargmax(r3s))
noise = np.nanstd(r3[np.abs(bg) > 2.5])
print(f"2T CNP : BG={bg[icnp]:+.3f} V, R2={r2[icnp]/1e3:.1f} kΩ (baseline {np.nanmin(r2)/1e3:.1f} kΩ)")
print(f"4T peak: BG={bg[ipk]:+.3f} V, R3={r3s[ipk]:.0f} Ω; metallic noise σ={noise:.0f} Ω -> SNR~{r3s[ipk]/noise:.1f}")
print(f"leakage: |I_tg|max={np.nanmax(np.abs(g.col('k_tg_curr'))):.1e} A, |I_bg|max={np.nanmax(np.abs(g.col('k_bg_curr'))):.1e} A")

fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(bg, r3, '.', ms=3, alpha=.4, label="4T raw")
ax.plot(bg, r3s, 'k-', label="4T σ=3")
ax.axvline(bg[icnp], c='r', ls=':', label="2T CNP")
ax.set_xlabel("BG (V)"); ax.set_ylabel("4T R (Ω)"); ax.legend(); plt.tight_layout(); plt.show()
