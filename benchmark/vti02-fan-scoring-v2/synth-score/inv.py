import sys, warnings; warnings.filterwarnings('ignore'); sys.dont_write_bytecode=True
sys.path.insert(0,'/data/sharpelab/hera-data/vti02-fan-scoring-v2/prereg-stats')
import common as C, numpy as np
eps=[r for r in C.inventory() if r['ending']=='fan' and r['cut']==C.CUT_0822]
live=[r for r in C.live_fans()]
for r in eps+live:
    d=r['doc']
    try:
        B,n,h,acq=C.design(r)
    except Exception as e:
        print('ERR',r['key'],e); continue
    li={x['name']:x for x in d['lockins']}
    print(f"{r['key'][-50:]:50s} {r.get('model','live'):6s} {r.get('source','g'):6s} {d.get('form')[:8]:8s} {d.get('field_mode')} slow={d.get('slow_axis')} B {B.min():.2f}-{B.max():.1f}x{B.size} n {n.min():+.2f}..{n.max():+.2f}x{n.size} I={acq['I']*1e9:.1f}nA tau={acq['tau']} sens={acq['sens']} fd={d.get('fast_delay_s')} h={h:.2f} lockins={list(li)}")
