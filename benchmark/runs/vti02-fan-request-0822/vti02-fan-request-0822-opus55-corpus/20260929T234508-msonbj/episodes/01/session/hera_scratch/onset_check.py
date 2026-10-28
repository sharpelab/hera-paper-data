import numpy as np, warnings
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_onset, fan_grids, resistance_grids, GateCalibration
D = Path("data")
def trace(rid):
    r = open_run(D / str(rid)); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I); o = np.argsort(B)
    return B[o], R[o], np.median(np.abs(I)), r
for rid, lo in ((6, 0.85), (6, 1.0), (7, 0.3), (7, 0.5)):
    B, R, Ib, r = trace(rid); m = B >= lo - 1e-6
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R[m], B[m], b_lo=lo, r_full_scale=50e-6 / Ib)
    print(f"--- run {rid}, record from {lo} T:"); print(on.summary())
    for x in w: print("   warn:", str(x.message)[:160])
# timing calibration
for rid in (5, 6, 7):
    r = open_run(D / str(rid)); t = r.col("time"); print(f"run {rid}: {len(t)} pts, {(t.max()-t.min())/60:.1f} min, {(t.max()-t.min())/len(t):.2f} s/pt")
# run 6 per-point overhead in 10 mT region: dt vs dB
B, R, Ib, r = trace(6); t = r.col("time"); Bu = r.col("magnet_field")
dt = np.diff(t); dB = np.abs(np.diff(Bu)); m = (dB > 0.008) & (dB < 0.012)
print(f"run 6 10 mT steps: median dt {np.median(dt[m]):.2f} s (bare ramp {0.01/0.137*60:.2f} s) -> overhead {np.median(dt[m]) - 0.01/0.137*60:.2f} s/pt")
# R along D=0 at B=0 from gatemap run 5
g = fan_grids(str(D / "5")); rg = resistance_grids(g); Rm = np.abs(rg.R["sr1"])
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0] if isinstance(fs[0], list) else fs); Vbg = g.slow
from sharpelab_nb.gates import calc_nD
N, Dd = calc_nD(Vtg[None, :], Vbg[:, None], 2.796e-3, 2.161e-3, -0.0894, -0.013)
for n0 in (2.0, 2.5, 3.0, 3.2):
    m = (np.abs(N - n0) < 0.1) & (np.abs(Dd) < 0.03)
    print(f"R(B=0, n={n0}, D~0) = {np.median(Rm[m]):.0f} Ohm ({m.sum()} px)")
