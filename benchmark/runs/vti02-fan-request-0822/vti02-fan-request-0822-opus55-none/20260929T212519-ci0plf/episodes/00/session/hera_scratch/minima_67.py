import numpy as np
from pathlib import Path
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, resolve_channels
for rid, n12 in [(6, 3.2), (7, -1.2)]:
    r = open_run(Path("data")/str(rid)); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/(r.col("sr0_X")/ch["sr0"].gain))
    o = np.argsort(B); B, R = B[o], R[o]
    Rs = gaussian_filter1d(R, 2)
    pk, pr = find_peaks(-Rs, prominence=8, distance=5)
    nu_fac = abs(n12)*1e16*6.62607e-34/1.602177e-19   # nu*B
    print(f"run {rid}: nu*B = {nu_fac:.1f} T (prior scale)")
    for p in pk:
        if B[p] > 0.8:
            print(f"  min B={B[p]:.3f} T  R={R[p]:6.1f}  nu_prior={nu_fac/B[p]:6.2f}  1/B={1/B[p]:.4f}")
