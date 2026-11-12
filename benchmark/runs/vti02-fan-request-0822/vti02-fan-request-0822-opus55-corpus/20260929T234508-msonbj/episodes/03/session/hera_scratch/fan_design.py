"""Landau-fan design numbers: model F(n) table, onset on the well-sampled record, worst-corner R, gate line, cost."""
import sys, json, warnings
import numpy as np
from hera.analysis import open_run, resolve_channels, sdh_onset, luttinger_frequency, fan_grids, resistance_grids, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs

D = "/home/hera/measurements/zack/20260822-vti-02/data"
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

print("=== model F(n), u_D = 0 ===")
print(" n12   F_L    ABAB orbits (F, m*)                     ABCA (topo, F, m*)")
for n in [1.0, 1.4, 1.6, 1.8, 2.0, 2.4, 2.8, 3.2]:
    ab = fs.abab_mstar(n * 1e16)
    E, topo, nc, nf, Fa = fs.abca_fs(n * 1e16)
    _, ma = fs.abca_mstar(n * 1e16)
    print(f"{n:4.1f} {float(luttinger_frequency(n*1e16)):6.2f}  " + "  ".join(f"({F:5.2f},{m:.3f})" for F, m in ab) + f"   {topo} {Fa:5.2f} {ma:.3f}")

def trace(rid):
    r = open_run(f"{D}/{rid}"); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = (r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain)
    o = np.argsort(B); return B[o], R[o]

print("\n=== onset on the uniformly-sampled segments (run 6: 10 mT above 1 T; run 7: 20 mT throughout) ===")
for rid, blo in ((6, 1.0), (7, 0.3)):
    B, R = trace(rid)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, b_lo=blo, r_full_scale=5000.0)
    for x in w: print("WARN:", x.message)
    print(f"run {rid} (b_lo={blo}):"); print(on.summary())

print("\n=== R along D = 0 at B = 0 from gatemap run 5 (nearest pixel) ===")
g = fan_grids(f"{D}/5"); rg = resistance_grids(g); R5 = np.abs(rg.R["sr1"])
fsp = g.meta["fast_setpoints"]; Vtg = np.asarray(fsp[0] if isinstance(fsp[0], list) else fsp); Vbg = np.asarray(g.slow)
for n in [1.0, 1.4, 1.6, 2.0, 2.4, 2.8, 3.2]:
    vt, vb = calc_gate_voltages(n, 0.0, **CAL)
    i, j = np.argmin(abs(Vbg - vb)), np.argmin(abs(Vtg - vt))
    print(f" n {n:.1f}: (Vtg, Vbg) = ({vt:+.3f}, {vb:+.3f}) R0 = {R5[i, j]:.0f} Ohm")
for rid in (6, 7):
    B, R = trace(rid)
    print(f"run {rid}: R(<0.4 T) {R[B<0.4].mean():.0f}, max {R.max():.0f} at {B[np.argmax(R)]:.2f} T, R(>9.8) {R[B>9.8].mean():.0f}, min {R.min():.0f} at {B[np.argmin(R)]:.2f}")
