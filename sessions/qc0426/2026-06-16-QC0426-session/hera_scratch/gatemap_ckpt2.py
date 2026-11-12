import numpy as np, json, os
run="data/1"; meta=json.load(open(os.path.join(run,"metadata.json")))
cols=meta["columns"]; idx={c:i for i,c in enumerate(cols)}
dat=np.loadtxt(os.path.join(run,"data.tsv")); nfast=101
nr=dat.shape[0]//nfast; dat=dat[:nr*nfast].reshape(nr,nfast,-1)
I_bias=5e-9
bg=dat[:,0,idx["k_bg_volt"]]; tg=dat[0,:,idx["DC_bias"]]
print("BG rows:", np.round(bg,2))
print("TG range:", tg.min(), tg.max())
# leakage
print("max|k_bg_curr| =%.2e  max|k_2410_curr| =%.2e A"%(
   np.abs(dat[:,:,idx["k_bg_curr"]]).max(), np.abs(dat[:,:,idx["k_2410_curr"]]).max()))
# drain current health
I=dat[:,:,idx["sr0_X"]]/(-1e6)
print("drain I nA: med %.2f min %.2f max %.2f"%(np.median(I)*1e9,I.min()*1e9,I.max()*1e9))
# CNP ridge per row (sr1, sr2) via gaussian-smoothed argmax
from scipy.ndimage import gaussian_filter1d
for nm,c in [("sr1","sr1_X"),("sr2","sr2_X")]:
    R=dat[:,:,idx[c]]/I_bias
    print(f"\n{nm} Rxx peak per BG row:")
    for r in range(nr):
        sm=gaussian_filter1d(np.abs(R[r]),2.0); j=np.argmax(sm)
        print(f"  BG={bg[r]:+.2f}  CNP@TG={tg[j]:+.3f}  Rpk={R[r,j]:.0f}ohm  (pred TG~{-1.3*bg[r]:+.2f})")
# any dead/flat channel?
for nm in ("sr1_X","sr2_X","sr3_X"):
    x=dat[:,:,idx[nm]].ravel()
    print(f"{nm}: span {x.max()-x.min():.2e} V {'FLAT' if np.allclose(x,x[0]) else 'ok'}")
