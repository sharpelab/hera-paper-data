import numpy as np, json, os

run="data/1"
meta=json.load(open(os.path.join(run,"metadata.json")))
# column names: try plural then singular schema
cols = meta.get("columns") or meta.get("cols")
if cols is None:
    # derive from params
    cols = []
    for k in ("slow_params","params","fast_params"):
        v=meta.get(k)
        if v: cols += (v if isinstance(v,list) else [v])
print("meta keys:", list(meta.keys())[:20])
print("columns:", cols)

dat=np.loadtxt(os.path.join(run,"data.tsv"))
print("raw shape:", dat.shape)
nfast=101
nrows_done=dat.shape[0]//nfast
print(f"complete fast-rows: {nrows_done} / 41  ({dat.shape[0]} pts)")

# map columns by header order recorded in metadata
hdr = meta.get("columns") or meta.get("column_names")
print("header:", hdr)
