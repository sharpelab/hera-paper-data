import numpy as np, glob, os
from hera.analysis import open_run

Vdc = np.linspace(-5,5,25); Idc = Vdc/1e8*1e9  # nA
rows = []
rids = sorted(int(os.path.basename(d)) for d in glob.glob('data/*') if os.path.basename(d).isdigit())
for rid in [r for r in rids if r >= 14]:
    try:
        r = open_run(f'data/{rid}')
        if r.recipe != 'temperature-dependence':
            continue
        T = np.nanmean(r.col('T'))*1e3
        dVdI = (r.col('sr830_3_X')/100.0)/1e-9
        zb = dVdI[np.argmin(np.abs(Idc))]
        Rn = np.median(dVdI[np.abs(Idc)>40]); thr = 0.5*Rn
        p = Idc>=0; n = Idc<=0
        Ip,Rp = Idc[p][np.argsort(Idc[p])], dVdI[p][np.argsort(Idc[p])]
        In,Rn_ = Idc[n][np.argsort(-Idc[n])], dVdI[n][np.argsort(-Idc[n])]
        icp = Ip[np.argmax(Rp>thr)] if (Rp>thr).any() else 0.0
        icn = In[np.argmax(Rn_>thr)] if (Rn_>thr).any() else 0.0
        Ic = (abs(icp)+abs(icn))/2
        rows.append((rid, T, zb, Ic, Rn))
    except Exception as e:
        rows.append((rid, None, None, None, str(e)[:30]))

print(f"{'run':>3} {'T(mK)':>7} {'zeroБias':>9} {'Ic(nA)':>7} {'Rn(Ω)':>7}")
for rid,T,zb,Ic,Rn in rows:
    if T is None: print(f"{rid:>3}  (err {Rn})"); continue
    print(f"{rid:>3} {T:7.1f} {zb:9.1f} {Ic:7.0f} {Rn:7.1f}")
