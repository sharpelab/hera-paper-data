"""Fig 5: dV/dI(I_dc, T) map + Ic(T) from the switching-peak position. Run 12."""
import numpy as np
import matplotlib; import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
g=run(12); print(summarize_run(g)); print("interrupted:",g.interrupted)
Vdc=g.col_at(g.col_indices('dc205_1_voltage')[0]); Idc=Vdc/1e8*1e9        # nA
dVdI=(g.col_at(g.col_indices('sr830_3_X')[0])/100)/0.5e-9                 # ohm
T=g.col('T')*1e3; hv=g.col_at(g.col_indices('heater_volt')[0]); B=g.col_at(g.col_indices('magnet_field')[0])
print(f"B {B.mean()*1e3:.3f} mT; T {T[T>10].min():.0f}-{T.max():.0f} mK; T-glitches {int((T<10).sum())}/{len(T)}")

hvu=np.unique(hv); Igrid=np.sort(np.unique(np.round(Idc,1)))
Z=np.full((len(hvu),len(Igrid)),np.nan); Trow=np.full(len(hvu),np.nan)
for i,h in enumerate(hvu):
    m=(hv==h)&(T>10)
    if m.sum()<5: continue
    Trow[i]=np.nanmean(T[m])
    for x,r in zip(Idc[m],dVdI[m]): Z[i,np.argmin(np.abs(Igrid-x))]=r

# Ic(T): mean |I| of the +/- switching peaks (max dV/dI on each side); 0 if no peak above normal+margin
Ic=np.full(len(hvu),np.nan)
for i in range(len(hvu)):
    row=Z[i]; m=np.isfinite(row)
    if m.sum()<20: continue
    norm=np.nanmedian(row[np.abs(Igrid)>70])           # normal dV/dI at high bias
    pos=(Igrid>2)&m; neg=(Igrid<-2)&m
    pk_p=Igrid[pos][np.argmax(row[pos])]; pk_n=Igrid[neg][np.argmax(row[neg])]
    peakval=0.5*(np.max(row[pos])+np.max(row[neg]))
    Ic[i]=0.5*(abs(pk_p)+abs(pk_n)) if peakval>1.3*norm else 0.0   # peak must exceed normal by 30%
jbase=np.nanargmin(Trow)
print(f"Ic(base T={Trow[jbase]:.0f} mK) = {Ic[jbase]:.0f} nA")
# Tc from Ic->0 (last T with Ic>2 nA)
good=np.isfinite(Ic)&np.isfinite(Trow)
Tc_ic = Trow[good][Ic[good]>2].max() if (Ic[good]>2).any() else np.nan
print(f"Ic->0 (last T with Ic>2 nA) ~ {Tc_ic:.0f} mK  (cf Fig 3 Tc=235 mK)")

def edges(c):
    c=np.asarray(c,float); e=np.empty(len(c)+1); e[1:-1]=0.5*(c[:-1]+c[1:]); e[0]=c[0]-0.5*(c[1]-c[0]); e[-1]=c[-1]+0.5*(c[-1]-c[-2]); return e
oi=np.argsort(Trow); m2=np.isfinite(Trow[oi])
fig,ax=plt.subplots(1,2,figsize=(13,5))
pc=ax[0].pcolormesh(edges(Igrid),edges(Trow[oi][m2]),Z[oi][m2],cmap='magma',vmin=0,vmax=120,shading='flat')
plt.colorbar(pc,ax=ax[0],label=r'$dV/dI$ ($\Omega$)',extend='max')
ax[0].plot(Ic[oi][m2],Trow[oi][m2],'c.-',ms=3,lw=0.8,label='+Ic(T)'); ax[0].plot(-Ic[oi][m2],Trow[oi][m2],'c.-',ms=3,lw=0.8)
ax[0].set_xlabel(r'$I_{dc}$ (nA)'); ax[0].set_ylabel('T (mK)'); ax[0].set_title('Fig 5 — dV/dI(I_dc,T) at optimum, B_eff0 (run 12)'); ax[0].legend(fontsize=8)
ax[1].plot(Trow[oi][m2],Ic[oi][m2],'o-',ms=3); ax[1].axhline(0,color='k',lw=0.5)
ax[1].axvline(235,color='r',ls='--',lw=1,label='Fig 3 Tc=235 mK'); ax[1].set_xlabel('T (mK)'); ax[1].set_ylabel(r'$I_c$ (nA)')
ax[1].set_title('Ic(T) -> 0 at Tc'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
