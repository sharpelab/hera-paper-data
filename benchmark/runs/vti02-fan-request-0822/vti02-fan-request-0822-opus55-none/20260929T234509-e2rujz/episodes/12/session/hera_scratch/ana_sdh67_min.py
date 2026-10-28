import numpy as np
from pathlib import Path
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, resolve_channels
D = Path(__file__).resolve().parent.parent / "data"
h, e = 6.62607015e-34, 1.602176634e-19
for rid, n12 in [(6, 3.2), (7, -1.2)]:
    r = open_run(D / str(rid)); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1); o = np.argsort(B); B = B[o]
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))[o]
    Rs = gaussian_filter1d(R, 2)
    m = B > 0.8
    pk, _ = find_peaks(-Rs[m], prominence=8)
    Bm = B[m][pk]
    nu_nom = abs(n12) * 1e16 * h / (e * Bm)
    print(f"run {rid} (n nominal {n12:+.2f}e12): minima")
    for b, nu, rr in zip(Bm, nu_nom, Rs[m][pk]):
        print(f"   B={b:6.3f} T  R={rr:6.1f}  nu_nom={nu:6.2f}")
    # zero-resistance plateaus
    z = (Rs < 10) & (B > 0.8)
    print("  frac of B>0.8 with R<10 Ohm:", z[m].mean().round(2))
