import json, gzip, os, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance, calc_nD

c_tg = stack_capacitance([(15.6,3)]); c_bg = 1.3136*c_tg; n_off, D_off = -0.225, 0.0
FILES = [18, 22, 23]

def cnp_vs_D(fid, ch):
    m=json.load(open(f"data/{fid}/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
    d=np.loadtxt(gzip.open(f"data/{fid}/data.tsv.gz"))
    _vec=lambda x: np.array(x[0] if isinstance(x[0],list) else x)
    bg=_vec(m["slow_setpoints"]); nf=len(_vec(m["fast_setpoints"])); nb=len(bg); d=d[:nb*nf]
    tgc=d[:,ci["DC_bias"]].reshape(nb,nf); bgc=d[:,ci["k_bg_volt"]].reshape(nb,nf)
    V=d[:,ci[ch]].reshape(nb,nf); Ib=5e-9
    Ds,Rs=[],[]
    for i in range(nb):
        s=gaussian_filter1d(np.abs(V[i]),1.5); j=int(np.argmax(s))
        if j<=1 or j>=nf-2: continue
        _,D=calc_nD(tgc[i,j],bgc[i,j],c_tg,c_bg,n_off,D_off)
        Ds.append(D); Rs.append(np.abs(V[i,j])/Ib)
    o=np.argsort(Ds); return np.array(Ds)[o], np.array(Rs)[o]

plt.figure(figsize=(9,6)); print(f"{'region':>10} {'pair':>9} {'Rmin[kO]':>9} {'Rmax[kO]':>9} {'growth':>7}")
cmap=plt.cm.tab10; k=0
for fid in FILES:
    if not os.path.exists(f"data/{fid}/data.tsv.gz"): print(f"  data/{fid} not ready"); continue
    m=json.load(open(f"data/{fid}/metadata.json")); mc=m["measurement_config"]
    for ch in ["sr1_X","sr2_X","sr3_X"]:
        pair=mc.get(ch[:3], "?")
        if "-" not in str(pair): continue
        D,R=cnp_vs_D(fid,ch)
        if len(R)<5: continue
        g=R.max()/max(R.min(),1)
        style="-" if "&" not in pair else "--"
        plt.semilogy(D,R/1e3,"o"+style,ms=3,lw=1,color=cmap(k%10),label=f"{pair} (f{fid}, x{g:.0f})")
        print(f"{ch[:3]+'/f'+str(fid):>10} {pair:>9} {R.min()/1e3:9.2f} {R.max()/1e3:9.1f} {g:7.0f}")
        k+=1
plt.axhline(0.25,ls=":",c="gray"); plt.xlabel("D (V/nm)"); plt.ylabel("CNP Rxx (kOhm)")
plt.title("Multi-region CNP Rxx vs D (B=0) — whole-device ABC test"); plt.legend(fontsize=7,ncol=2)
plt.tight_layout(); plt.savefig("hera_scratch/multiregion.png",dpi=110); print("saved multiregion.png")
