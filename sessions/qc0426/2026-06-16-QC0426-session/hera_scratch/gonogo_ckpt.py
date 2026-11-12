import numpy as np, json
m=json.load(open("data/2/metadata.json")); ci={c:i for i,c in enumerate(m["columns"])}
d=np.loadtxt("data/2/data.tsv")
print("interrupted:", m["interrupted"], " pts so far:", d.shape[0], "/316")
B=d[:,ci["magnet_mag"]]; I=d[:,ci["sr0_X"]]/(-1e6); I_bias=5e-9
print(f"B reached: {B.min():.3f} -> {B.max():.3f} T")
print(f"drain I nA: med {np.median(I)*1e9:.2f} min {I.min()*1e9:.2f} max {I.max()*1e9:.2f}")
print(f"leak k_bg {np.abs(d[:,ci['k_bg_curr']]).max():.1e} k_2410 {np.abs(d[:,ci['k_2410_curr']]).max():.1e} A")
for nm in ("sr1_X","sr2_X","sr3_X"):
    R=d[:,ci[nm]]/I_bias
    print(f"{nm}: R range [{R.min():.0f},{R.max():.0f}] ohm, std {R.std():.0f}")
# crude oscillation check: detrend Rxx vs B and look for sign changes (wiggle count) above ~0.5T
sel=B>0.5
if sel.sum()>20:
    R1=d[sel,ci["sr1_X"]]/I_bias; Bs=B[sel]
    dt=R1-np.poly1d(np.polyfit(Bs,R1,3))(Bs)
    sc=np.sum(np.diff(np.sign(dt))!=0)
    print(f"sr1 detrended sign-changes (B>0.5T, {sel.sum()} pts): {sc}  rms {dt.std():.1f} ohm")
