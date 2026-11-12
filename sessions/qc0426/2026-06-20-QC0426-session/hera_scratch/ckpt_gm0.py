import json, numpy as np, os
d = "data/0"
meta = json.load(open(os.path.join(d, "metadata.json")))
cols = meta["columns"]
print("columns:", cols)
print("interrupted:", meta.get("interrupted"), "| rows expected:", len(meta["slow_setpoints"])*len(meta["fast_setpoints"]))

tsv = os.path.join(d, "data.tsv")
a = np.loadtxt(tsv)
print("rows so far:", a.shape)
idx = {c: i for i, c in enumerate(cols)}

# leakage check
for cur in [c for c in cols if c.endswith("_curr")]:
    v = a[:, idx[cur]]
    print(f"{cur}: max|I|={np.abs(v).max():.3e} A   (threshold 1e-9)")

# locate CNP ridge in TG per BG row: argmax of sr1 R = V/I_bias
slow = cols[1]; fast = cols[2]
I_bias = 5e-9
sr1 = a[:, idx["sr1_X"]] / I_bias
bg = a[:, idx[slow]]; tg = a[:, idx[fast]]
print("\nCNP ridge (sr1 argmax) per BG row:")
for b in np.unique(bg):
    m = bg == b
    if m.sum() < 5: continue
    tgr = tg[m]; r = sr1[m]
    k = np.argmax(r)
    railed = np.sum(r > 4.2e3)
    print(f"  BG={b:+.2f}  CNP_TG={tgr[k]:+.3f}V  Rpk={r[k]:.0f}Ω  n_railed(>4.2k)={railed}/{m.sum()}  TGrange[{tgr.min():.1f},{tgr.max():.1f}]")
