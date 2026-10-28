import json, sys, numpy as np
run = sys.argv[1] if len(sys.argv) > 1 else "data/4"
try:
    md = json.load(open(f"{run}/metadata.json")); cols = md["columns"]
    a = np.genfromtxt(f"{run}/data.tsv", delimiter="\t", invalid_raise=False)
    if a.ndim == 1: a = a[None, :]
    a = a[~np.isnan(a).any(axis=1)]
    ix = {}; [ix.setdefault(c, j) for j, c in enumerate(cols)]
    itg = np.abs(a[:, ix["k_tg_curr"]]).max() * 1e12
    ibg = np.abs(a[:, ix["k_bg_curr"]]).max() * 1e12
    print(f"{len(a)} {itg:.1f} {ibg:.1f}")
except Exception as e:
    print(f"0 0 0")
