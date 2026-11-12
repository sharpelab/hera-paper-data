"""Runs 6 & 7 — library sdh_fft spectra + Landau-index check on the minima."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_fft, luttinger_frequency

def trace(rid):
    g = open_run(f"data/{rid}")
    c = list(g.cols); d = np.asarray(g.data)
    p1 = g.meta["instruments"]["sr1"]["snapshot"]["parameters"]
    Ib = p1["amplitude"]["value"] / g.meta["measurement_config"]["bias_resistor"]
    B = d[:, c.index("magnet_field")]; R = d[:, c.index("sr1_X")] / Ib
    o = np.argsort(B); return B[o], R[o]

for rid, n_spot in ((6, 3.2), (7, -1.2)):
    B, R = trace(rid)
    FL = float(luttinger_frequency(abs(n_spot) * 1e16))
    print(f"\n===== run {rid}  n={n_spot:+.2f}e12  F_L={FL:.2f} T =====")
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for ax, (blo, bhi) in zip(axes.ravel(), [(1.0, 10.0), (1.0, 4.0), (3.0, 10.0), (0.5, 10.0)]):
        m = (B >= blo) & (B <= bhi)
        f, spec = sdh_fft(R[m].reshape(-1, 1), B[m], nfft=8192, bg_degree=5, log=True)
        s = spec[0]
        span = 1/blo - 1/bhi
        k = (f > 1.0) & (f < 2.5 * FL + 20)
        fk, sk = f[k], s[k]
        idx, props = find_peaks(sk, prominence=0.05 * (sk.max() - np.median(sk)))
        order = np.argsort(-sk[idx])[:8]
        print(f"  B[{blo},{bhi}] df={1/span:.2f} T  (Nyquist f_max={0.5/((1/B[m][0]-1/B[m][-1])/m.sum()):.0f} T)")
        for i in idx[order]:
            print(f"      f={fk[i]:7.2f} T  amp={sk[i]:8.3f}  f/F_L={fk[i]/FL:5.3f}  periods={fk[i]*span:5.1f}")
        ax.plot(fk, sk, lw=0.9)
        ax.plot(fk[idx[order]], sk[idx[order]], 'rv', ms=4)
        for x0, col in ((FL, 'k'), (0.72*FL, 'r'), (0.28*FL, 'b')):
            ax.axvline(x0, color=col, ls='--', lw=0.8)
        ax.set_title(f"run {rid} B[{blo},{bhi}]  df={1/span:.1f} T", fontsize=9); ax.set_xlabel("F (T)")
    fig.tight_layout(); fig.savefig(f"hera_scratch/fft4_run{rid}.png", dpi=110); plt.close(fig)

    # Landau index: minima of R above 1 T
    m = B >= 1.0
    Bw, Rw = B[m], R[m]
    Rd = Rw - np.polyval(np.polyfit(Bw, Rw, 5), Bw)
    mins, _ = find_peaks(-Rd, prominence=np.std(Rd) * 0.5)
    Bm = Bw[mins]
    print("  minima B (T):", np.round(Bm, 3))
    print("  minima 1/B  :", np.round(1/Bm, 4))
    if len(Bm) > 2:
        d = np.diff(np.sort(1/Bm))
        print("  D(1/B) between adjacent minima:", np.round(d, 4), " -> F=1/D:", np.round(1/d, 1))
