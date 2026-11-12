import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, fan_grids, resistance_grids

rid = sys.argv[1] if len(sys.argv)>1 else "7"
run = open_run(f"data/{rid}"); print(summarize_run(run)); print("interrupted:", run.interrupted)

# --- reassign T from the LIVE Probe1 logfile (setup pointed at dead Probe2) ---
def probe1_T(path=r"C:\Users\toploader\temperature_logs\Probe1_MixingCh_low.txt"):
    ts=[];T=[]
    with open(path,'rb') as f:
        for ln in f.read().decode(errors='replace').splitlines():
            c=ln.split('\t')
            if len(c)>=3:
                try: ts.append(float(c[0].split()[0])); T.append(float(c[-3]))
                except: pass
    return np.array(ts),np.array(T)
p_ts,p_T = probe1_T()
t_row = run.col("time")
T_real = np.interp(t_row, p_ts, p_T)*1e3            # mK, per row, from Probe1
print(f"Probe1 T reassigned: row T {T_real.min():.0f}–{T_real.max():.0f} mK (stale 'T' col was flat 33.7)")

f = fan_grids(f"data/{rid}"); rg = resistance_grids(f)
dVdI = np.abs(rg.R["sr830_3"])                       # (nrows_heater, nfast_bias)
Idc  = f.grid("dc205_1_voltage")/1e8*1e9             # nA
hv   = f.slow
nrow, nfast = dVdI.shape
Treal_grid = T_real[:nrow*nfast].reshape(nrow, nfast)
Hcur = f.grid("heater_curr")*1e6 if "heater_curr" in f.cols else None

print("\nheaterV  T(mK)   Ic(nA)  dVdI(0)  normal  hcur(uA)")
res=[]
for i in range(nrow):
    idc=Idc[i]; r=dVdI[i]; o=np.argsort(idc); idc,r=idc[o],r[o]
    T_i=np.nanmean(Treal_grid[i])
    zb=r[np.abs(idc)<3].mean(); nm=r[np.abs(idc)>24].mean(); thr=zb+0.5*(nm-zb)
    above=np.abs(idc[(np.abs(idc)>0)&(r>=thr)])
    Ic=above.min() if (above.size and (nm-zb)>5) else 0.0
    hc=np.nanmean(Hcur[i]) if Hcur is not None else float('nan')
    res.append((hv[i],T_i,Ic,zb,nm,hc))
    print(f"  {hv[i]:4.1f}  {T_i:6.1f}  {Ic:6.1f}  {zb:6.2f}  {nm:6.1f}  {hc:7.1f}")
res=np.array(res); Tarr=res[:,1]; Icarr=res[:,2]
oo=np.argsort(Tarr); Ts=Tarr[oo]; Ics=Icarr[oo]; Tc=np.nan
for k in range(len(Ts)-1):
    if Ics[k]>2 and Ics[k+1]<=2: Tc=0.5*(Ts[k]+Ts[k+1]); break
print(f"\nIc(base={Tarr.min():.0f}mK)={Icarr[np.argmin(Tarr)]:.1f} nA")
print(f"Tc (Ic->0, threshold conv.) ≈ {Tc:.0f} mK" if np.isfinite(Tc) else "Tc: Ic not extinguished in range")

fig,ax=plt.subplots(1,2,figsize=(13,5))
for i in range(nrow):
    o=np.argsort(Idc[i]); ax[0].plot(Idc[i][o],dVdI[i][o],label=f"{Tarr[i]:.0f} mK")
ax[0].set_xlabel("I_dc (nA)"); ax[0].set_ylabel("dV/dI (Ω)"); ax[0].set_title(f"Run {rid}: dV/dI(Idc) vs T (Probe1)"); ax[0].legend(fontsize=7,ncol=2)
ax[1].plot(Tarr,Icarr,"o-"); ax[1].set_xlabel("T (mK, Probe1)"); ax[1].set_ylabel("Ic (nA)")
if np.isfinite(Tc): ax[1].axvline(Tc,color="r",ls="--",label=f"Tc≈{Tc:.0f} mK"); ax[1].legend()
ax[1].set_title("Ic(T) — supercurrent melting"); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig(f"hera_scratch/tdep_run{rid}.png",dpi=120)
print(f"saved hera_scratch/tdep_run{rid}.png")
