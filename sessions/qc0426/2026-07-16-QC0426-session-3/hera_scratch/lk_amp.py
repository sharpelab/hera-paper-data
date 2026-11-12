# LK ladder amplitude extraction: per-run T + un-normalized tone amplitudes.
# usage: menv python hera_scratch/lk_amp.py <run_id> [<run_id> ...]
import sys
import numpy as np
from hera.analysis import open_run, sdh_fft

for rid in [int(a) for a in sys.argv[1:]]:
    r = open_run(f"data/{rid}")
    B = r.col_at(1)
    T = r.col("T_sample")
    R = r.col("sr1_X") / 20e-9
    freqs, spec = sdh_fft(R[:, None], B, b_range=(3.2, 8.0), bg_degree=5)
    a = spec[0]  # un-normalized — LK uses absolute amplitudes in a fixed window
    def amp(F, w):
        m = (freqs > F - w) & (freqs < F + w)
        return a[m].max() if m.any() else np.nan
    print(f"run {rid}: T {np.mean(T):6.3f} K (drift {np.ptp(T)*1e3:4.0f} mK) | "
          f"A(11.1)={amp(11.1,3):8.3g}  A(55.3)={amp(55.3,4):8.3g}  A(66.4)={amp(66.4,4):8.3g}"
          f"{'  INTERRUPTED' if r.interrupted else ''}")
