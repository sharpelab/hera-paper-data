"""Plot 0.75 mT map; assemble B_c2(T) from Tc(B) across all field maps; extract xi (GL)."""
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import scipy.constants as cst
from hera.analysis import open_run, GateCalibration
N_OFF=-0.362e11*1e4; cal=GateCalibration.from_thicknesses(23.6e-9,20e-9,0,n_offset=N_OFF)
B_EFF0=-0.366  # mT

def analyze(rid):
    g=open_run(f"data/{rid}")
    n11=cal.n_D(g.col_at(g.col_indices('k_tg_volt')[0]),g.col_at(g.col_indices('k_bg_volt')[0]))[0]/1e4/1e11
    T=g.col('T')*1e3; R=(g.col_at(g.col_indices('sr830_3_X')[0])/100)/1e-9; hv=g.col_at(g.col_indices('heater_volt')[0])
    Btrue=g.col_at(g.col_indices('magnet_field')[0]).mean()*1e3 - B_EFF0
    hvu=np.unique(hv); n_grid=np.sort(np.unique(np.round(n11,3))); jo=np.argmin(np.abs(n_grid+5.0))
    Z=np.full((len(hvu),len(n_grid)),np.nan); Trow=np.full(len(hvu),np.nan)
    for i,h in enumerate(hvu):
        m=(hv==h)&(T>10)
        if m.sum()<5: continue
        Trow[i]=np.nanmean(T[m])
        for x,r in zip(n11[m],R[m]):
            Z[i,np.argmin(np.abs(n_grid-x))]=r
    Ttop=np.nanmax(Trow); col=Z[:,jo]; Rn=np.nanmedian(col[Trow>Ttop-30]); oo=np.argsort(Trow); tt,rr=Trow[oo],col[oo]; Tc=np.nan
    for k in range(1,len(rr)):
        if np.isfinite(rr[k-1]) and rr[k-1]<0.5*Rn<=rr[k] and tt[k]>45:
            Tc=tt[k-1]+(0.5*Rn-rr[k-1])/(rr[k]-rr[k-1])*(tt[k]-tt[k-1]); break
    return Btrue, Tc, (n_grid,Trow,Z,jo)

fields={5:'B_eff0',10:'+0.75',6:'+1',9:'+1.25',7:'+2'}
pts=[]
for rid in fields:
    Btrue,Tc,_=analyze(rid); pts.append((Btrue,Tc)); print(f"run {rid}: B_true={Btrue:.2f} mT, Tc={Tc:.0f} mK")
pts=np.array(sorted(pts)); Bv,Tcv=pts[:,0],pts[:,1]

# B_c2(T): fit B vs Tc (linear GL). B_c2(0)=intercept at T=0; slope=dB_c2/dT
m,c=np.polyfit(Tcv,Bv,1)   # B = m*T + c (mT vs mK)
Bc2_0=c  # mT at T=0
Tc0=-c/m  # T where B->0 (zero-field Tc)
Phi0=cst.h/(2*cst.e)
xi=np.sqrt(Phi0/(2*np.pi*Bc2_0*1e-3))   # m
print(f"\nB_c2(T) linear fit: dB_c2/dT = {m:.4f} mT/mK = {m*1000:.1f} mT/K")
print(f"B_c2(0) (T=0 intercept) = {Bc2_0:.2f} mT ; zero-field Tc (B=0 intercept) = {Tc0:.0f} mK")
print(f"xi_GL(0) = sqrt(Phi0/(2pi B_c2(0))) = {xi*1e9:.0f} nm = {xi*1e6:.2f} um")
print(f"(prior handoff: xi ~ 0.4 um order-of-magnitude)")

fig,ax=plt.subplots(1,2,figsize=(13,5))
# left: 0.75 mT map
_,_,( n_grid,Trow,Z,jo)=analyze(10)
def edges(x):
    x=np.asarray(x,float); e=np.empty(len(x)+1); e[1:-1]=0.5*(x[:-1]+x[1:]); e[0]=x[0]-0.5*(x[1]-x[0]); e[-1]=x[-1]+0.5*(x[-1]-x[-2]); return e
oi=np.argsort(Trow); m2=np.isfinite(Trow[oi])
pc=ax[0].pcolormesh(edges(n_grid),edges(Trow[oi][m2]),Z[oi][m2],cmap='inferno',vmin=0,vmax=55,shading='flat')
plt.colorbar(pc,ax=ax[0],label=r'$R_{xx}$ ($\Omega$)'); ax[0].axvline(-5.0,color='w',ls='--',lw=0.8)
ax[0].set_xlabel(r'$n$ ($10^{11}$ cm$^{-2}$)'); ax[0].set_ylabel('T (mK)'); ax[0].set_title('Fig 4 — R(T,n) at +0.75 mT (run 10)')
# right: B_c2(T) + GL fit -> xi
ax[1].plot(Tcv,Bv,'o',ms=8,label='Tc(B) data (50%-normal)')
Tline=np.linspace(0,Tc0,50); ax[1].plot(Tline,m*Tline+c,'r--',label=f'GL fit: B_c2(0)={Bc2_0:.2f} mT')
ax[1].set_xlabel('T (mK)'); ax[1].set_ylabel(r'$B_{c2}$ (mT, true)'); ax[1].set_xlim(0,260); ax[1].set_ylim(0,Bc2_0*1.1)
ax[1].set_title(f'B$_{{c2}}$(T) -> xi$_{{GL}}$(0) = {xi*1e9:.0f} nm'); ax[1].legend(fontsize=9); ax[1].grid(alpha=0.3)
plt.tight_layout(); plt.savefig('hera_scratch/bc2_xi.png',dpi=140); print('saved hera_scratch/bc2_xi.png')
