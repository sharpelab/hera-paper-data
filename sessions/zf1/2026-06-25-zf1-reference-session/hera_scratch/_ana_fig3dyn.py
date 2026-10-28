# Run 4 — Fig 3 (dynamic, 90 s dwell): R(T,n) map + the sample-probe T-lag diagnostic
g = run(4)
print(summarize_run(g)); print("interrupted:", g.interrupted)
vtg=g.col_at(g.col_indices('k_tg_volt')[0]); vbg=g.col_at(g.col_indices('k_bg_volt')[0])
n11=cal.n_D(vtg,vbg)[0]/1e4/1e11
T=g.col('T')*1e3; R=(g.col_at(g.col_indices('sr830_3_X')[0])/100)/1e-9
hv=g.col_at(g.col_indices('heater_volt')[0])

# build map (recorded T per heater step)
hvu=np.unique(hv); hvu=hvu[np.argsort(-hvu)]
n_grid=np.sort(np.unique(np.round(n11,3)))
def nidx(x): return np.argmin(np.abs(n_grid-x))
Z=np.full((len(hvu),len(n_grid)),np.nan); Trow=np.full(len(hvu),np.nan)
for i,h in enumerate(hvu):
    m=hv==h; Trow[i]=np.nanmean(T[m])
    for x,r in zip(n11[m],R[m]): Z[i,nidx(x)]=r

fig,ax=plt.subplots(1,2,figsize=(13,5))
def edges(c):
    c=np.asarray(c,float); e=np.empty(len(c)+1); e[1:-1]=0.5*(c[:-1]+c[1:]); e[0]=c[0]-0.5*(c[1]-c[0]); e[-1]=c[-1]+0.5*(c[-1]-c[-2]); return e
oi=np.argsort(Trow)
pc=ax[0].pcolormesh(edges(n_grid),edges(Trow[oi]),Z[oi],cmap='inferno',vmin=0,vmax=55,shading='flat')
plt.colorbar(pc,ax=ax[0],label=r'$R_{xx}$ ($\Omega$)')
ax[0].axvline(-5.0,color='w',ls='--',lw=0.8); ax[0].set_xlabel(r'$n$ ($10^{11}$ cm$^{-2}$)'); ax[0].set_ylabel('recorded T (mK)')
ax[0].set_title('Fig 3 dynamic (90 s dwell) — dome shape OK, T-axis biased')

# overlay: map R(T) at optimum (dynamic) vs warm-up equilibrium
sel=np.abs(n11-(-5.0))<0.011; o=np.argsort(T[sel])
ax[1].plot(T[sel][o],R[sel][o],'.-',ms=3,label='dynamic map (cooling, 90 s)')
Tw=np.array([48.6,100.3,157.7,228.9,262.4,316.6,363.8,428.4,480.3]); Rw=np.array([0.41,0.56,2.94,5.81,17.29,38.37,40.49,42.65,42.95])
ax[1].plot(Tw,Rw,'ks-',ms=5,label='warm-up (equilibrium)')
ax[1].axhline(0,color='k',lw=0.5); ax[1].set_xlabel('recorded T (mK)'); ax[1].set_ylabel(r'$R_{xx}$ ($\Omega$)')
ax[1].set_title('R(T) at optimum: dynamic vs equilibrium'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
print("dynamic Tc(50%-norm) ~223 mK vs equilibrium ~280 mK -> ~50 mK low (sample lags probe during cooling)")
