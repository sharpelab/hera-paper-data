import json, numpy as np, gzip
from hera.analysis import open_run
for rid in range(8):
    r = open_run(f'data/{rid}')
    m = r.meta
    t = r.col('time')
    print(f'run {rid}: {m.get("function")} type {m.get("type")} rows {r.rows} recipe {r.recipe!r}')
    print(f'   start {m.get("start_time")} end {m.get("end_time")}  wall(t col) {(t[-1]-t[0])/60:.1f} min  mean dt {np.median(np.diff(t)):.3f} s')
    for k in ('slow_param','slow_params','fast_param','fast_params','param','params','slow_delay','fast_delay','delay'):
        if k in m: print(f'   {k}: {str(m[k])[:110]}')
    if 'fast_setpoints' in m:
        fs = m['fast_setpoints']; ss = m['slow_setpoints']
        fs0 = fs[0] if isinstance(fs[0], list) else fs
        print(f'   nfast {len(fs0)} nslow {len(ss[0]) if isinstance(ss[0],list) else len(ss)}')
    print('   cols:', m['columns'])
    mc = m.get('measurement_config', {})
    print('   mc:', {k: v for k, v in mc.items() if 'gain' in k or 'bias' in k.lower() or k in ('Si (V)',)})
