import json, datetime as dt
rows = json.load(open('inventory_raw.json'))
print('| run | start (local) | type | fast / slow | pts | dt s | h | sr0 sens/τ | sr1 sens/τ | f, amp | sr1 cols | T_sample K | B T | nplc | comment |')
print('|'+'---|'*15)
for r in rows:
    st = dt.datetime.fromtimestamp(float(r['start'])).strftime('%m-%d %H:%M') if r['start'] else '?'
    s0 = r.get('sr0', {}); s1 = r.get('sr1', {})
    sc = ','.join(c[4:] for c in r['cols'] if c.startswith('sr1_'))
    T = r.get('rng_T_sample'); Bm = r.get('rng_magnet_field')
    npl = r.get('k_2400_tg', {}).get('nplci')
    cm = ((r['mc'] or {}).get('comments') or r['comments'] or '')
    cm = cm if isinstance(cm, str) else str(cm)
    print(f"| {r['day']}-r{r['run']} | {st} | {r['type']} | {r['fast']} / {r['slow']} | {r.get('npts')} | {r.get('dt_med',0):.2f} | {r.get('dur_h',0):.2f} | "
          f"{s0.get('sensitivity')}/{s0.get('time_constant')} | {s1.get('sensitivity')}/{s1.get('time_constant')} | {s1.get('frequency')},{s1.get('amplitude')} | {sc} | "
          f"{'' if T is None else '%.3f-%.3f'%tuple(T)} | {'' if Bm is None else '%.2f-%.2f'%tuple(Bm)} | {npl} | {cm[:70]} |")
