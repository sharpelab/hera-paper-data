import json, gzip, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from sharpelab_nb.gates import stack_capacitance, calc_nD
from hera.analysis import fan_grids, resistance_grids, sdh_fft

c_tg=stack_capacitance([(15.6,3)]); c_bg=1.3136*c_tg
h=6.626e-34; e=1.602e-19
# single-band g=4 expectation: f[T] = n[1e12 cm^-2] * (h/(4e))*1e16
slope_g4 = (h/(4*e))*1e16     # T per 1e12 cm^-2
print(f"expected slope (single band, g=4): {slope_g4:.2f} T per 1e12 cm^-2")

pts=[]   # (n_gate, f_dominant)
for fid,(brlo,brhi),nlo,nhi in [(20,(4,8),0.6,4.0),(21,(5,8),3.6,10.0)]:
    m=json.load(open(f"data/{fid}/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
    d=np.loadtxt(gzip.open(f"data/{fid}/data.tsv.gz")); nf=len(m["fast_setpoints"][0]); B=np.array(m["slow_setpoints"][0]); nb=len(B); d=d[:nb*nf]
    tg=d[:,ci["DC_bias"]].reshape(nb,nf); bg=d[:,ci["k_bg_volt"]].reshape(nb,nf)
    na=calc_nD(tg,bg,c_tg,c_bg,-0.225,0)[0][0]; od=np.argsort(na); ns=na[od]
    fg=fan_grids(f"data/{fid}"); rg=resistance_grids(fg)
    fr,spec=sdh_fft(np.abs(rg.R["sr1"]), fg.slow, b_range=(brlo,brhi)); sp=spec[od]
    for j in np.where((ns>nlo)&(ns<nhi))[0]:
        s=sp[j]/(sp[j].max()+1e-9); pk,_=find_peaks(s,height=0.5,distance=15); pk=[p for p in pk if fr[p]>4]
        if pk:
            fdom=fr[pk[int(np.argmax([s[p] for p in pk]))]]   # strongest peak
            pts.append((ns[j], fdom))
pts=np.array(pts); ng,fd=pts[:,0],pts[:,1]
# fit through origin: f = a*n
a=np.sum(ng*fd)/np.sum(ng*ng)
print(f"measured slope (fit f=a*n through origin): {a:.2f} T per 1e12 cm^-2  over n={ng.min():.1f}-{ng.max():.1f}")
print(f"ratio measured/expected(g4) = {a/slope_g4:.3f}  -> n_SdH/n_gate = {a/slope_g4:.3f}")
print(f"=> single g=4 band carries {a/slope_g4*100:.0f}% of the gate density (lever-arm consistent to {abs(1-a/slope_g4)*100:.0f}%)")
plt.figure(figsize=(7,5))
plt.plot(ng,fd,"o",ms=4,label="SdH dominant freq (sr1)")
nn=np.linspace(0,ng.max(),50)
plt.plot(nn,slope_g4*nn,"k--",label=f"single band g=4 ({slope_g4:.1f} T/unit)")
plt.plot(nn,a*nn,"r-",label=f"fit ({a:.1f} T/unit)")
plt.xlabel("n_gate (1e12 cm^-2)"); plt.ylabel("SdH frequency (T)"); plt.legend(); plt.title("SdH lever-arm cross-check (Nyquist-clean windows)")
plt.tight_layout(); plt.savefig("hera_scratch/leverarm.png",dpi=110); print("saved leverarm.png")
