# Run 5 — Figure 3 (settled, quantitative): R(T,n) at D=-0.64, B_eff0; 1-tau dwell
g = run(5)
print(summarize_run(g)); print("interrupted:", g.interrupted)
vtg=g.col_at(g.col_indices('k_tg_volt')[0]); vbg=g.col_at(g.col_indices('k_bg_volt')[0])
n11=cal.n_D(vtg,vbg)[0]/1e4/1e11
T=g.col('T')*1e3; R=(g.col_at(g.col_indices('sr830_3_X')[0])/100)/1e-9
hv=g.col_at(g.col_indices('heater_volt')[0])
itg=np.abs(g.col('k_tg_curr')).max(); print(f"leak<{itg:.1e} A; B={g.col_at(g.col_indices('magnet_field')[0]).mean()*1e3:.3f} mT; T {T.min():.0f}-{T.max():.0f} mK")

# map on recorded-T per heater step
hvu=np.unique(hv); n_grid=np.sort(np.unique(np.round(n11,3)))
def nidx(x): return np.argmin(np.abs(n_grid-x))
Z=np.full((len(hvu),len(n_grid)),np.nan); Trow=np.full(len(hvu),np.nan); drift=np.full(len(hvu),np.nan)
for i,h in enumerate(hvu):
    m=hv==h; Trow[i]=np.nanmean(T[m]); drift[i]=np.ptp(T[m])
    for x,r in zip(n11[m],R[m]): Z[i,nidx(x)]=r
print(f"per-row T-drift: median {np.nanmedian(drift):.1f} mK")

# Tc(n) 50%-normal
Tc=np.full(len(n_grid),np.nan)
for j in range(len(n_grid)):
    col=Z[:,j]; Rn=np.nanmedian(col[Trow>420])
    if not np.isfinite(Rn) or Rn<5: continue
    oo=np.argsort(Trow); tt,rr=Trow[oo],col[oo]
    for k in range(1,len(rr)):
        if np.isfinite(rr[k-1]) and rr[k-1]<0.5*Rn<=rr[k]:
            f=(0.5*Rn-rr[k-1])/(rr[k]-rr[k-1]); Tc[j]=tt[k-1]+f*(tt[k]-tt[k-1]); break
jopt=nidx(-5.0)
print(f"Tc(optimum n=-5.0) = {Tc[jopt]:.0f} mK ; Tc range {np.nanmin(Tc):.0f}-{np.nanmax(Tc):.0f} mK")

def edges(c):
    c=np.asarray(c,float); e=np.empty(len(c)+1); e[1:-1]=0.5*(c[:-1]+c[1:]); e[0]=c[0]-0.5*(c[1]-c[0]); e[-1]=c[-1]+0.5*(c[-1]-c[-2]); return e
fig,ax=plt.subplots(1,2,figsize=(13,5)); oi=np.argsort(Trow)
pc=ax[0].pcolormesh(edges(n_grid),edges(Trow[oi]),Z[oi],cmap='inferno',vmin=0,vmax=55,shading='flat')
plt.colorbar(pc,ax=ax[0],label=r'$R_{xx}$ ($\Omega$)'); ax[0].plot(n_grid,Tc,'c.-',ms=3,lw=1,label='Tc (50%-normal)')
ax[0].axvline(-5.0,color='w',ls='--',lw=0.8); ax[0].set_xlabel(r'$n$ ($10^{11}$ cm$^{-2}$)'); ax[0].set_ylabel('recorded T (mK)')
ax[0].set_title('Fig 3 — R(T,n) at D=-0.64, B_eff0 (run 5, settled)'); ax[0].legend(fontsize=8)
# R(T) at optimum: run 5 (up) vs run 4 (down) bracket
sel=np.abs(n11-(-5.0))<0.011; o=np.argsort(T[sel])
ax[1].plot(T[sel][o],R[sel][o],'o-',ms=3,label=f'run 5 up (1tau): Tc={Tc[jopt]:.0f} mK')
g4=run(4); n4=cal.n_D(g4.col_at(g4.col_indices('k_tg_volt')[0]),g4.col_at(g4.col_indices('k_bg_volt')[0]))[0]/1e4/1e11
T4=g4.col('T')*1e3; R4=(g4.col_at(g4.col_indices('sr830_3_X')[0])/100)/1e-9; s4=np.abs(n4-(-5.0))<0.011; o4=np.argsort(T4[s4])
ax[1].plot(T4[s4][o4],R4[s4][o4],'.-',ms=2,alpha=0.5,color='gray',label='run 4 down (dyn): Tc~223 mK')
ax[1].axhline(0,color='k',lw=0.5); ax[1].set_xlabel('recorded T (mK)'); ax[1].set_ylabel(r'$R_{xx}$ ($\Omega$)')
ax[1].set_title('R(T) at optimum: up/down bracket -> true Tc ~228-235 mK'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
