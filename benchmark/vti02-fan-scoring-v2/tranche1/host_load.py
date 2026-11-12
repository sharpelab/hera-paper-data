# Host load on edhar over the tranche windows, from telegraf -> InfluxDB on the NAS.
# Run: INFLUX_TOKEN="$(zkey influx-read)" python3 host_load.py
import os, json, urllib.request, urllib.error, csv, io, statistics as st, sys
tok=os.environ['INFLUX_TOKEN']; url='http://192.168.1.49:8086'; org='zoumez'; bucket='metrics'
def q(flux):
    req=urllib.request.Request(url+'/api/v2/query?org='+org,data=json.dumps({'query':flux,'type':'flux'}).encode(),
        headers={'Authorization':'Token '+tok,'Content-Type':'application/json','Accept':'application/csv'})
    try: txt=urllib.request.urlopen(req,timeout=60).read().decode()
    except urllib.error.HTTPError as e: print('HTTP',e.code,e.read()[:200]); return []
    return [r for r in csv.DictReader(io.StringIO(txt)) if r.get('_value') not in (None,'','_value')]
def stats(name,rows,scale=1.0):
    v=sorted(float(r['_value'])*scale for r in rows)
    if not v: print(f"{name}: no data"); return
    print(f"{name:34s} n={len(v):4d} mean={st.mean(v):7.2f} median={v[len(v)//2]:7.2f} p95={v[int(.95*len(v))]:7.2f} max={v[-1]:7.2f} min={v[0]:7.2f}")
def window(label,a,b):
    R=f'|> range(start: {a}, stop: {b}) |> filter(fn:(r)=> r.host=="edhar")'
    print('==',label,a,b)
    stats('cpu busy % of 32 threads', q(f'from(bucket:"{bucket}") {R} |> filter(fn:(r)=> r._measurement=="cpu" and r.cpu=="cpu-total" and r._field=="usage_idle") |> map(fn:(r)=>({{r with _value: 100.0 - r._value}}))'))
    stats('cpu iowait %', q(f'from(bucket:"{bucket}") {R} |> filter(fn:(r)=> r._measurement=="cpu" and r.cpu=="cpu-total" and r._field=="usage_iowait")'))
    stats('load1', q(f'from(bucket:"{bucket}") {R} |> filter(fn:(r)=> r._measurement=="system" and r._field=="load1")'))
    stats('mem used GiB', q(f'from(bucket:"{bucket}") {R} |> filter(fn:(r)=> r._measurement=="mem" and r._field=="used")'),1/2**30)
    stats('mem available GiB', q(f'from(bucket:"{bucket}") {R} |> filter(fn:(r)=> r._measurement=="mem" and r._field=="available")'),1/2**30)
    stats('swap used GiB', q(f'from(bucket:"{bucket}") {R} |> filter(fn:(r)=> r._measurement=="swap" and r._field=="used")'),1/2**30)
window('baseline hour before','2026-09-29T20:15:00Z','2026-09-29T21:15:00Z')
window('tranche 1 episodes (12 slots)','2026-09-29T21:25:17Z','2026-09-29T22:29:25Z')
window('grading (8 slots)','2026-09-29T22:29:44Z','2026-09-29T22:38:53Z')
