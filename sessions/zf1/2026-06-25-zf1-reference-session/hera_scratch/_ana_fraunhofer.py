"""Fig 2 Fraunhofer: dV/dI(I_dc, B_perp) map + Ic(B). Central lobe should sit at B_eff0."""
import numpy as np
import matplotlib; import matplotlib.pyplot as plt
import scipy.constants as cst
from hera.analysis import open_run, summarize_run
B_EFF0=-0.366  # mT
g=run(13); print(summarize_run(g)); print("interrupted:",g.interrupted)
Bc=g.col_at(g.col_indices('magnet_field')[0])*1e3            # controller mT
Idc=g.col_at(g.col_indices('dc205_1_voltage')[0])/1e8*1e9    # nA
dVdI=(g.col_at(g.col_indices('sr830_3_X')[0])/100)/0.5e-9    # ohm
T=g.col('T')*1e3
print(f"T {T[T>10].min():.0f}-{T.max():.0f} mK (base, watch flux heating); rows {len(Bc)}")

Bu=np.unique(np.round(Bc,4)); Igrid=np.sort(np.unique(np.round(Idc,1)))
Z=np.full((len(Bu),len(Igrid)),np.nan); Brow=np.full(len(Bu),np.nan)
for i,b in enumerate(Bu):
    m=np.abs(Bc-b)<0.02
    if m.sum()<20: continue
    Brow[i]=np.nanmean(Bc[m])
    for x,r in zip(Idc[m],dVdI[m]): Z[i,np.argmin(np.abs(Igrid-x))]=r
Btrue=Brow-B_EFF0   # true sample field, mT

# Ic(B): mean |I| of +/- switching peaks; 0 if no peak above 1.3x normal
Ic=np.full(len(Bu),np.nan)
for i in range(len(Bu)):
    row=Z[i]; mm=np.isfinite(row)
    if mm.sum()<20: continue
    norm=np.nanmedian(row[np.abs(Igrid)>70]); pos=(Igrid>2)&mm; neg=(Igrid<-2)&mm
    if not (pos.any() and neg.any()): continue
    pkv=0.5*(np.max(row[pos])+np.max(row[neg]))
    Ic[i]=0.5*(abs(Igrid[pos][np.argmax(row[pos])])+abs(Igrid[neg][np.argmax(row[neg])])) if pkv>1.3*norm else 0.0
good=np.isfinite(Ic)&np.isfinite(Btrue)
icen=np.nanargmax(np.where(good,Ic,-1)); Bcen=Btrue[icen]
print(f"central lobe (max Ic={Ic[icen]:.0f} nA) at B_true={Bcen:+.3f} mT (expect ~0 = B_eff0 self-check)")
# lobe width: FWHM-ish where Ic drops to ~0 around center
zc=Btrue[good][(Ic[good]<2)&(Btrue[good]>Bcen)]; zc2=Btrue[good][(Ic[good]<2)&(Btrue[good]<Bcen)]
if len(zc) and len(zc2):
    dB=zc.min()-zc2.max(); A=cst.h/(2*cst.e)/(dB*1e-3); print(f"central-lobe full width ~{dB:.2f} mT -> Phi0/A => A~{A*1e12:.2f} um^2 (if single-junction lobe)")

def edges(c):
    c=np.asarray(c,float); e=np.empty(len(c)+1); e[1:-1]=0.5*(c[:-1]+c[1:]); e[0]=c[0]-0.5*(c[1]-c[0]); e[-1]=c[-1]+0.5*(c[-1]-c[-2]); return e
oi=np.argsort(Btrue); m2=np.isfinite(Btrue[oi])
fig,ax=plt.subplots(1,2,figsize=(13,5))
pc=ax[0].pcolormesh(edges(Igrid),edges(Btrue[oi][m2]),Z[oi][m2],cmap='magma',vmin=0,vmax=90,shading='flat')
plt.colorbar(pc,ax=ax[0],label=r'$dV/dI$ ($\Omega$)',extend='max')
ax[0].plot(Ic[oi][m2],Btrue[oi][m2],'c.-',ms=2,lw=0.7); ax[0].plot(-Ic[oi][m2],Btrue[oi][m2],'c.-',ms=2,lw=0.7)
ax[0].axhline(0,color='w',ls='--',lw=0.7)
ax[0].set_xlabel(r'$I_{dc}$ (nA)'); ax[0].set_ylabel(r'$B_\perp$ true (mT)'); ax[0].set_title('Fig 2 Fraunhofer — dV/dI(I_dc, B) (run 13)')
ax[1].plot(Btrue[oi][m2],Ic[oi][m2],'o-',ms=3); ax[1].axvline(0,color='r',ls='--',lw=1,label='B_eff0')
ax[1].set_xlabel(r'$B_\perp$ true (mT)'); ax[1].set_ylabel(r'$I_c$ (nA)'); ax[1].set_title('Ic(B): central lobe at B_eff0'); ax[1].legend(fontsize=8)
plt.tight_layout(); plt.show()
