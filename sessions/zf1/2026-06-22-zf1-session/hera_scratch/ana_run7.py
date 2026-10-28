# --- Run 7: T-dependence Ic(T). T REASSIGNED from live Probe1 (setup pointed at dead Probe2). ---
g7 = open_run(Path(file_path)/"7"); print(summarize_run(g7))
def _probe1_T(path=r"C:\Users\toploader\temperature_logs\Probe1_MixingCh_low.txt"):
    ts=[];T=[]
    for ln in open(path,'rb').read().decode(errors='replace').splitlines():
        c=ln.split('\t')
        if len(c)>=3:
            try: ts.append(float(c[0].split()[0])); T.append(float(c[-3]))
            except: pass
    return np.array(ts),np.array(T)
p_ts,p_T=_probe1_T()
T_real=np.interp(g7.col("time"),p_ts,p_T)*1e3        # mK from Probe1
f7=fan_grids(Path(file_path)/"7"); rg7=resistance_grids(f7)
dVdI=np.abs(rg7.R["sr830_3"]); Idc=f7.grid("dc205_1_voltage")/1e8*1e9
nrow,nfast=dVdI.shape; Tg=T_real[:nrow*nfast].reshape(nrow,nfast)
Tarr=[];Icarr=[]
for i in range(nrow):
    idc=Idc[i]; r=dVdI[i]; o=np.argsort(idc); idc,r=idc[o],r[o]
    zb=r[np.abs(idc)<3].mean(); nm=r[np.abs(idc)>24].mean(); thr=zb+0.5*(nm-zb)
    ab=np.abs(idc[(np.abs(idc)>0)&(r>=thr)]); Ic=ab.min() if (ab.size and nm-zb>5) else 0.0
    Tarr.append(np.nanmean(Tg[i])); Icarr.append(Ic)
Tarr=np.array(Tarr);Icarr=np.array(Icarr)
Tc=np.nan; oo=np.argsort(Tarr)
for k in range(len(oo)-1):
    if Icarr[oo][k]>2 and Icarr[oo][k+1]<=2: Tc=0.5*(Tarr[oo][k]+Tarr[oo][k+1]);break
print(f"T reassigned from Probe1: {Tarr.min():.0f}-{Tarr.max():.0f} mK; Ic(base)={Icarr[np.argmin(Tarr)]:.1f} nA; Tc≈{Tc:.0f} mK")
fig,ax=plt.subplots(1,2,figsize=(13,5))
for i in range(nrow):
    o=np.argsort(Idc[i]); ax[0].plot(Idc[i][o],dVdI[i][o],label=f"{Tarr[i]:.0f} mK")
ax[0].set_xlabel("I_dc (nA)"); ax[0].set_ylabel("dV/dI (Ω)"); ax[0].set_title("Run 7 — dV/dI(Idc) vs T (RAW; T from Probe1)"); ax[0].legend(fontsize=7,ncol=2)
ax[1].plot(Tarr,Icarr,"o-"); ax[1].axvline(Tc,color="r",ls="--",label=f"Tc≈{Tc:.0f} mK")
ax[1].set_xlabel("T (mK, Probe1)"); ax[1].set_ylabel("Ic (nA)"); ax[1].set_title("Ic(T) — supercurrent melting"); ax[1].legend(); ax[1].grid(alpha=.3)
plt.show()
