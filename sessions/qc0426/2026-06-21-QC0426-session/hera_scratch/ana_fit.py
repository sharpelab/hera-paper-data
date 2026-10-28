def ridge(Rg, Vtg, s=1.5):
    A = np.abs(Rg); v = np.full(A.shape[0], np.nan); pk = v.copy(); clip = np.zeros(A.shape[0], bool)
    for i in range(A.shape[0]):
        j = int(np.argmax(gaussian_filter1d(A[i], s))); v[i] = Vtg[j]; pk[i] = A[i, j]
        if j <= 1 or j >= len(Vtg)-2: clip[i] = True
    return v, pk, clip
fits = {}
for cid in ("sr1", "sr2"):
    v, pk, clip = ridge(rg.R[cid], Vtg); keep = ~clip & np.isfinite(v)
    p, cov = np.polyfit(Vbg[keep], v[keep], 1, cov=True)
    fits[cid] = dict(slope=p[0], intercept=p[1], keep=keep, v=v,
                     rms=np.sqrt(np.mean((v[keep]-np.polyval(p, Vbg[keep]))**2)))
    print(f"[{cid}] Vtg={p[0]:.4f}*Vbg+{p[1]:.4f}  ratio={-p[0]:.4f}  serr={np.sqrt(cov[0,0]):.4f}  rms={fits[cid]['rms']*1e3:.0f}mV  kept {keep.sum()}/{len(Vbg)}")
best = min(fits, key=lambda c: fits[c]['rms']); slope = fits[best]['slope']; ratio = -slope
c_tg = stack_capacitance([(15.6, 3)]); c_bg = ratio*c_tg
cal = a.GateCalibration(c_tg=c_tg, c_bg=c_bg)
n_off = float(-cal.density(fits[best]['intercept'], 0.0))
cal = a.GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=n_off)
print(f"\nCAL (channel {best}): c_tg={c_tg:.4e}  c_bg={c_bg:.4e} F/m^2  ratio={ratio:.4f} (geom 1.300)  n_offset={n_off:.3e} m^-2")
print(f"CNP at Vbg=0: Vtg={fits[best]['intercept']:.3f} V ; D=0 line: Vtg={ratio:.4f}*Vbg ; scale=geometry prior")
fig, ax = plt.subplots(1, 2, figsize=(11, 4.3))
for k, cid in enumerate(("sr1", "sr2")):
    R = np.abs(rg.R[cid]); im = ax[k].imshow(R/1e3, origin="lower", aspect="auto", extent=ext, cmap="viridis",
                                              vmax=np.nanpercentile(R, 99)/1e3)
    f = fits[cid]; ax[k].scatter(f['v'][f['keep']], Vbg[f['keep']], s=12, c='r')
    ax[k].plot(np.polyval([f['slope'], f['intercept']], Vbg), Vbg, 'w--', lw=1.2)
    ax[k].set_title(f"{cid}: slope {f['slope']:.3f}"); ax[k].set_xlabel("V_tg [V]"); ax[k].set_ylabel("V_bg [V]")
fig.suptitle("CNP ridge fit overlay"); fig.tight_layout(); plt.show()
