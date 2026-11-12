# Run 7 — Figure 4b: R(T,n) at B = B_eff0 + 2 mT (field member, near B_c)
g = run(7)
print(summarize_run(g)); print("interrupted:", g.interrupted)
n11 = cal.n_D(g.col_at(g.col_indices('k_tg_volt')[0]), g.col_at(g.col_indices('k_bg_volt')[0]))[0]/1e4/1e11
T = g.col('T')*1e3; R = (g.col_at(g.col_indices('sr830_3_X')[0])/100)/1e-9; hv = g.col_at(g.col_indices('heater_volt')[0])
Bf = g.col_at(g.col_indices('magnet_field')[0])
print(f"B held {Bf.mean()*1e3:.3f} mT (std {Bf.std()*1e3:.3f}); leak<{np.abs(g.col('k_tg_curr')).max():.1e} A; T {T[T>10].min():.0f}-{T.max():.0f} mK")

hvu = np.unique(hv); n_grid = np.sort(np.unique(np.round(n11,3)))
def nidx(x): return np.argmin(np.abs(n_grid-x))
Z = np.full((len(hvu),len(n_grid)),np.nan); Trow = np.full(len(hvu),np.nan)
for i,h in enumerate(hvu):
    m = (hv==h)&(T>10)                       # mask T=0 glitches
    if m.sum()<5: continue
    Trow[i] = np.nanmean(T[m])
    for x,r in zip(n11[m],R[m]): Z[i,nidx(x)] = r

Ttop = np.nanmax(Trow); jo = nidx(-5.0)
col = Z[:,jo]; Rn = np.nanmedian(col[Trow>Ttop-30]); oo = np.argsort(Trow); tt,rr = Trow[oo],col[oo]; Tc = np.nan
for k in range(1,len(rr)):
    if np.isfinite(rr[k-1]) and rr[k-1]<0.5*Rn<=rr[k] and tt[k]>45:
        Tc = tt[k-1]+(0.5*Rn-rr[k-1])/(rr[k]-rr[k-1])*(tt[k]-tt[k-1]); break
floor = np.nanmedian(Z[(Trow>50)&(Trow<90),jo])
print(f"Tc(+2mT, 50%-normal) = {Tc:.0f} mK ; normal R = {Rn:.1f} ; base floor = {floor:.1f} ohm")

def edges(c):
    c=np.asarray(c,float); e=np.empty(len(c)+1); e[1:-1]=0.5*(c[:-1]+c[1:]); e[0]=c[0]-0.5*(c[1]-c[0]); e[-1]=c[-1]+0.5*(c[-1]-c[-2]); return e
oi = np.argsort(Trow); m2 = np.isfinite(Trow[oi])
fig,ax = plt.subplots(1,2,figsize=(13,5))
pc = ax[0].pcolormesh(edges(n_grid),edges(Trow[oi][m2]),Z[oi][m2],cmap='inferno',vmin=0,vmax=55,shading='flat')
plt.colorbar(pc,ax=ax[0],label=r'$R_{xx}$ ($\Omega$)'); ax[0].axvline(-5.0,color='w',ls='--',lw=0.8)
ax[0].set_xlabel(r'$n$ ($10^{11}$ cm$^{-2}$)'); ax[0].set_ylabel('T (mK)')
ax[0].set_title(f'Fig 4b — R(T,n) at {Bf.mean()*1e3:.2f} mT (B_eff0+2mT), run 7')
sel = np.abs(n11-(-5.0))<0.011; o = np.argsort(T[sel]); gd = T[sel][o]>45
ax[1].plot(T[sel][o][gd],R[sel][o][gd],'o-',ms=3); ax[1].axhline(0,color='k',lw=0.5)
ax[1].axvline(Tc,color='r',ls='--',label=f'Tc={Tc:.0f} mK'); ax[1].set_xlabel('T (mK)'); ax[1].set_ylabel(r'$R_{xx}$ ($\Omega$)')
ax[1].set_title('R(T) at optimum, +2 mT'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
