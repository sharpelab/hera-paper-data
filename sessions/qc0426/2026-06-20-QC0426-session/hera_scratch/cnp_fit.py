import json, os, sys, numpy as np
from scipy.ndimage import gaussian_filter1d

def load_run(d):
    meta = json.load(open(os.path.join(d, "metadata.json")))
    cols = meta["columns"]
    p = os.path.join(d, "data.tsv.gz")
    if not os.path.exists(p):
        p = os.path.join(d, "data.tsv")
    a = np.loadtxt(p)
    return meta, cols, a

def ridge(d, chan="sr1_X", I_bias=5e-9, smooth=1.5, edge_frac=0.02):
    meta, cols, a = load_run(d)
    idx = {c: i for i, c in enumerate(cols)}
    slow, fast = cols[1], cols[2]
    bg, tg = a[:, idx[slow]], a[:, idx[fast]]
    R = a[:, idx[chan]] / I_bias
    tg_lo, tg_hi = tg.min(), tg.max(); span = tg_hi - tg_lo
    out = []
    for b in np.unique(bg):
        m = bg == b
        if m.sum() < 10:
            continue
        o = np.argsort(tg[m]); tgr = tg[m][o]; r = R[m][o]
        rs = gaussian_filter1d(r, smooth)
        tg_argmax = tgr[np.argmax(rs)]
        sel = rs >= 0.98 * rs.max()                 # railed-plateau-robust center
        tg_center = tgr[sel].mean()
        edge = (tg_center < tg_lo + edge_frac * span) or (tg_center > tg_hi - edge_frac * span)
        out.append(dict(bg=b, tg_argmax=tg_argmax, tg_center=tg_center,
                        rmax=rs.max(), nplateau=int(sel.sum()), edge=edge))
    return out

def fit(d, chan):
    rows = ridge(d, chan)
    bg = np.array([r["bg"] for r in rows])
    tgc = np.array([r["tg_center"] for r in rows])
    good = np.array([not r["edge"] for r in rows])
    p = np.polyfit(bg[good], tgc[good], 1)
    slope, intercept = p
    resid = tgc[good] - np.polyval(p, bg[good])
    print(f"{chan}: slope={slope:+.4f}  c_bg/c_tg={-slope:+.4f}  b(intercept)={intercept:+.4f}V  "
          f"rms_resid={resid.std()*1e3:.1f}mV  nrows={good.sum()}/{len(bg)} edge_excl={(~good).sum()}  "
          f"plateau~{np.median([r['nplateau'] for r in rows]):.0f}pts")
    return slope, intercept

d = sys.argv[1] if len(sys.argv) > 1 else "data/0"
print("run:", d)
for ch in ["sr1_X", "sr2_X"]:
    fit(d, ch)
