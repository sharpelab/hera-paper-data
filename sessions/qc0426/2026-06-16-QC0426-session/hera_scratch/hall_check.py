import numpy as np, json
m=json.load(open("data/3/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
d=np.loadtxt("data/3/data.tsv.gz"); nfast=36; nr=d.shape[0]//nfast; g=d[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci["magnet_mag"]]; I_bias=5e-9; e=1.602177e-19
n_gate=np.linspace(-1.4e12,-5.0e12,nfast)
# classical Hall regime: below SdH onset
sel=(B>=0.5)&(B<=1.8)
print("low-field Hall window B[0.5,1.8]:",sel.sum(),"rows")
print(" n_gate[1e12]  n_Hall[1e12]  ratio  (Rxy slope)")
rats=[]
for j in range(0,nfast,3):
    Rxy=g[sel,j,ci["sr3_X"]]/I_bias
    p=np.polyfit(B[sel],Rxy,1)  # Rxy = slope*B + c ; slope = 1/(n e) (signed)
    nH=1.0/(e*p[0])             # m^-2 (signed)
    r=abs(nH)/abs(n_gate[j]*1e4)
    rats.append(r)
    print(f"  {n_gate[j]/1e12:+.2f}      {nH/1e16:+.2f}        {r:.2f}")
print(f"\nmean |n_Hall|/|n_gate| = {np.mean(rats):.2f} +/- {np.std(rats):.2f}")
print("ratio ~1 => geometry n-scale confirmed (QH/Hall lever-arm); single-carrier Hall consistent with one dominant pocket")
