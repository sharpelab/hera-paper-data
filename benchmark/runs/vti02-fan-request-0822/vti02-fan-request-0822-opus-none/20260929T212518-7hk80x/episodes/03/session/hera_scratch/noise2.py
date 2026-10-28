import numpy as np
from hera.analysis import open_run, fan_grids
# run 5: gatemap at sr1 sens 100 uV; run 4: same map at 20 uV (aborted). Compare fast-axis pt-to-pt noise in nV.
for rid, sens in [(4, 20e-6), (5, 100e-6)]:
    f = fan_grids(f'data/{rid}')
    V = f.grid('sr1_X')                      # volts, gain 1
    Vtg = f.grid('k_2400_tg_volt')
    # pick rows far from the CNP ridge -> flat region; use robust pt-to-pt on the flattest 20% of rows
    d = np.diff(V, axis=1)
    sig = np.std(d, axis=1)/np.sqrt(2)
    # per-row: use MAD of second difference to kill real slope/curvature
    d2 = np.diff(V, n=2, axis=1)
    mad = np.median(np.abs(d2 - np.median(d2, axis=1, keepdims=True)), axis=1)*1.4826/np.sqrt(6)
    q = np.nanpercentile(mad, 20)
    print(f'run {rid}  sens {sens*1e6:.0f} uV  nrows {f.nrows}: median pt-noise {np.median(mad)*1e9:6.1f} nV, '
          f'quiet-20% {q*1e9:6.1f} nV  ({q/sens*100:.4f} % FS)   -> R-noise at 10 nA: {q/10e-9:.2f} Ohm')
