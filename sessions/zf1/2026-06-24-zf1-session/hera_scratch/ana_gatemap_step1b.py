"""Refined look: reveal sub-ridge low-R structure + hunt LOCAL dips in the
prior SC region (D<0, |D|>~0.5, n~ -0.4..-0.6 e12 cm^-2)."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run
from sharpelab_nb.gates import stack_capacitance, calc_nD

NSLOW,NFAST=81,69
V_TG=np.linspace(-7,6,NSLOW); V_BG=np.linspace(-4,4.2,NFAST)
r=open_run("data/4")
def colp(n):
    i=r.col_indices(n); return r.col_at(i[0])
R4=(colp("sr830_3_X").reshape(NSLOW,NFAST)/100.0)/1e-9

c_tg=stack_capacitance([(23.6,3)]); c_bg=c_tg*1.1833
n_off=-calc_nD(0.1634,0.0,c_tg,c_bg)[0]
TG,BG=np.meshgrid(V_TG,V_BG,indexing="ij")
nmap,Dmap=calc_nD(TG,BG,c_tg,c_bg,n_offset=n_off)
print("n range[e12 cm^-2]: %.2f..%.2f   D range[V/nm]: %.2f..%.2f"%(nmap.min(),nmap.max(),Dmap.min(),Dmap.max()))

# where are the genuinely-low-R points (<6 ohm)? localized pocket or dense edge?
lowmask=R4<6.0
print("pts R4<6ohm:",int(lowmask.sum()))
for thr in (4,6,8,10):
    m=R4<thr
    if m.any():
        print("  R4<%2d ohm: n[%.2f,%.2f] D[%.2f,%.2f]  Vtg[%.1f,%.1f] Vbg[%.1f,%.1f]"%(
            thr,nmap[m].min(),nmap[m].max(),Dmap[m].min(),Dmap[m].max(),
            TG[m].min(),TG[m].max(),BG[m].min(),BG[m].max()))

# prior SC region mask
reg=(Dmap<-0.45)&(Dmap>-0.75)&(nmap>-1.0)&(nmap<0.2)
print("prior-region pts:",int(reg.sum()))
if reg.any():
    Rr=np.where(reg,R4,np.nan)
    print("  prior-region R4 min=%.2f med=%.2f max=%.2f"%(np.nanmin(Rr),np.nanmedian(Rr),np.nanmax(Rr)))
    k=np.nanargmin(Rr); ii,jj=np.unravel_index(k,R4.shape)
    print("  min in prior region: R=%.2f at n=%.3f D=%.3f (Vtg=%.2f Vbg=%.2f)"%(
        R4[ii,jj],nmap[ii,jj],Dmap[ii,jj],V_TG[ii],V_BG[jj]))

# tight-scale plots
fig,ax=plt.subplots(1,2,figsize=(14,5))
im0=ax[0].pcolormesh(nmap,Dmap,R4,shading="auto",vmin=2,vmax=40,cmap="viridis")
ax[0].axhline(-0.5,color="w",ls=":"); ax[0].set_title("4T Rxx (2-40 ohm) -> (n,D)")
ax[0].set_xlabel("n (e12 cm^-2)"); ax[0].set_ylabel("D (V/nm)"); fig.colorbar(im0,ax=ax[0])
# zoom prior region in raw gate space
im1=ax[1].pcolormesh(V_BG,V_TG,R4,shading="auto",vmin=2,vmax=40,cmap="viridis")
ax[1].set_title("4T Rxx (2-40 ohm) raw"); ax[1].set_xlabel("V_bg"); ax[1].set_ylabel("V_tg"); fig.colorbar(im1,ax=ax[1])
plt.tight_layout(); plt.savefig("hera_scratch/gatemap_step1_lowR.png",dpi=120)
print("saved hera_scratch/gatemap_step1_lowR.png")
