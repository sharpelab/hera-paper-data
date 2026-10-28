import json, gzip, numpy as np
from pathlib import Path
from hera.analysis import open_run
for rid in (4,5,6,7):
    r = open_run(Path("data")/str(rid))
    m = r.meta
    t = r.col("time")
    print(f"--- run {rid}: {m.get('function')} rows={r.rows} start={m.get('start_time')} end={m.get('end_time')}")
    dur = t[-1]-t[0]
    print(f"    elapsed(time col) = {dur:.0f} s = {dur/60:.1f} min; per-point {dur/max(r.rows-1,1):.3f} s")
    for k in ("slow_delay","fast_delay","delay"):
        if k in m: print(f"    {k} = {m[k]}")
    fs = m.get("fast_setpoints")
    if fs is not None:
        f0 = fs[0] if isinstance(fs[0], list) else fs
        print(f"    nfast={len(f0)} fast={m.get('fast_param') or m.get('fast_params')}")
        ss = m.get("slow_setpoints"); s0 = ss[0] if isinstance(ss[0], list) else ss
        print(f"    nslow={len(s0)} slow={m.get('slow_param') or m.get('slow_params')} range {min(s0)}..{max(s0)}")
        # per-row time
        nf=len(f0); nr=r.rows//nf
        tt=t[:nr*nf].reshape(nr,nf)
        rowdur = tt[:,-1]-tt[:,0]
        gap = tt[1:,0]-tt[:-1,-1]
        print(f"    row sweep {np.median(rowdur):.1f}s ({np.median(rowdur)/nf*1000:.0f} ms/pt), turnaround {np.median(gap):.1f}s")
    inst = m.get("instruments", {})
    for nm in ("sr0","sr1"):
        d = inst.get(nm) or {}
        if d: print(f"    {nm}: sens={d.get('sensitivity')} tc={d.get('time_constant')} slope={d.get('filter_slope')}")
