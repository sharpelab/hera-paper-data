"""Summarize one T-ladder bias sweep: heater V, T, fridge T, Ic, R0, Rn."""
import json, gzip, os, sys
import numpy as np
run=sys.argv[1]
try:
    md=json.load(open(f"{run}/metadata.json")); cols=md["columns"]
    p=f"{run}/data.tsv"; f=gzip.open(p+".gz","rt") if os.path.exists(p+".gz") else open(p)
    a=np.genfromtxt(f,delimiter="\t",invalid_raise=False); f.close(); a=a[~np.isnan(a).any(axis=1)]
    ix={};[ix.setdefault(c,j) for j,c in enumerate(cols)]
    vidx=[i for i,c in enumerate(cols) if "dc205" in c]
    Idc=a[:,vidx[0]]/1e8*1e9; Iac=0.5e-9
    dVdI=(a[:,ix["sr830_3_X"]]/100)/Iac
    T=a[:,ix["T"]]*1e3
    fT=a[:,ix["T_fridge"]]*1e3 if "T_fridge" in ix else np.array([np.nan])
    hV=a[:,ix["heater_volt"]] if "heater_volt" in ix else np.array([np.nan])
    Rn=np.median(dVdI[np.abs(Idc)>45]); R0=np.median(dVdI[np.abs(Idc)<3])
    thr=0.5*Rn
    # Ic = |Idc| where dVdI first reaches thr (from 0 outward), averaged +/-
    def ic(sign):
        m=(np.sign(Idc)==sign)&(np.abs(Idc)>1); x=np.abs(Idc[m]); y=dVdI[m]; o=np.argsort(x); x,y=x[o],y[o]
        c=np.where(y>=thr)[0]; return x[c[0]] if len(c) else np.nan
    icv=np.nanmean([ic(1),ic(-1)])
    print(f"{run}: heater={np.median(hV):.2f}V T={np.median(T):.1f}mK(drift {T.max()-T.min():.1f}) fridgeT={np.median(fT):.1f}mK R0={R0:.1f}Ω Rn={Rn:.1f}Ω Ic={icv:.1f}nA")
except Exception as ex:
    print(f"{run}: not ready ({ex})")
