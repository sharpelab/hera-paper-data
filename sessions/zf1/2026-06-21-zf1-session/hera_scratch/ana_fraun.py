import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run

def load(fid):
    r=open_run(f"data/{fid}"); cfg=json.load(open(f"data/{fid}/metadata.json"))["measurement_config"]
    B=r.col("magnet_field")*1e3
    Idc=r.col("dc205_1_voltage")/cfg["bias_resistor"]*1e9
    dVdI=(r.col("sr830_3_X")/cfg["sr3_gain"])/(r.col("sr830_1_X")/cfg["sr1_gain"])
    return B,Idc,dVdI

B=[];I=[];R=[]
for fid in (14,15):
    b,i,r=load(fid); B.append(b);I.append(i);R.append(r)
B=np.concatenate(B);I=np.concatenate(I);R=np.concatenate(R)
Bv=np.unique(B)
# Ic(B) at 30% of normal (~40 Ohm -> 12 Ohm) per branch
Rn=40.0; th=0.3*Rn
ic=[]
for b in Bv:
    m=B==b; ii=I[m]; rr=R[m]; o=np.argsort(ii); ii,rr=ii[o],rr[o]
    pos=ii[ii>0]; Rp=rr[ii>0]; icp=pos[np.argmax(Rp>th)] if np.any(Rp>th) else np.nan
    neg=ii[ii<0][::-1]; Rneg=rr[ii<0][::-1]; icn=neg[np.argmax(Rneg>th)] if np.any(Rneg>th) else np.nan
    ic.append((b,icp,icn))
ic=np.array(ic)
ib=ic[np.nanargmax(ic[:,1]),0]
print(f"effective zero (max Ic) at B={ib:+.2f} mT; max Ic+~{np.nanmax(ic[:,1]):.1f} nA")
print(f"Ic->0 (B_c_perp) by ~{Bv[np.nanargmax((ic[:,1]<1)&(Bv>ib))] if np.any((ic[:,1]<1)&(Bv>ib)) else np.nan:.1f} mT (+side)")

fig,ax=plt.subplots(1,2,figsize=(13,5))
# 2D dV/dI(Idc,B)
from scipy.interpolate import griddata
bi=np.linspace(B.min(),B.max(),60); ii=np.linspace(I.min(),I.max(),80)
BB,II=np.meshgrid(bi,ii)
G=griddata((B,I),R,(BB,II),method='linear')
pc=ax[0].pcolormesh(bi,ii,np.clip(G,0,40),shading='auto',cmap='inferno')
ax[0].set(xlabel="B (mT)",ylabel="I_dc (nA)",title="dV/dI (Ω) — Ic(B) central lobe");plt.colorbar(pc,ax=ax[0])
ax[1].plot(ic[:,0],ic[:,1],'o-',ms=4,label='Ic+'); ax[1].plot(ic[:,0],-ic[:,2],'o-',ms=4,label='|Ic-|')
ax[1].axvline(ib,c='gray',ls=':',label=f'B_eff~{ib:+.1f}mT')
ax[1].set(xlabel="B (mT)",ylabel="Ic (nA)",title="Ic vs B⊥ (30% threshold)");ax[1].legend();ax[1].grid(alpha=.3); ax[1].axhline(0,c='gray',lw=.5)
plt.tight_layout(); plt.savefig("hera_scratch/fraun.png",dpi=110); print("saved fraun.png")
