import numpy as np, json, os
d = "data/1"
meta = json.load(open(os.path.join(d,"metadata.json")))
# column order
cols = meta.get("columns") or meta.get("cols")
print("cols:", cols)
# load partial tsv (uncompressed during run)
tsv = os.path.join(d,"data.tsv")
raw = np.genfromtxt(tsv, delimiter="\t", names=None)
print("loaded rows:", raw.shape)
