# Landau-fan design numbers: model F(n) table, timing calibration, dynamic-range anchor.
import numpy as np, sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
from hera.analysis import open_run

E = 1.602176634e-19; H = 6.62607015e-34
h4e = H / (4 * E)

print("=== model F(n) table, electron side (units: n in 1e12 cm^-2, F in T) ===")
print(f"{'n':>5} {'F_L':>6} | ABAB orbits (F, m*)                | ABCA F_total")
for n12 in [0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2]:
    n = n12 * 1e16
    FL = h4e * n
    _, orbs = M.abab_fs(n)
    ms = M.abab_mstar(n)
    ab = ", ".join(f"{F:.1f}T(m*={m:.3f})" for (F, _), (_, m) in zip(orbs, ms))
    try:
        _, topo, ncomp, nfreq, Ftot = M.abca_fs(n)
        abca = f"{Ftot:.1f}T ({topo}, {ncomp} comp)"
    except Exception as e:
        abca = f"err {e}"
    print(f"{n12:5.1f} {FL:6.1f} | {ab:35s} | {abca}")
    # harmonic-vs-heavy discriminator: 3x light vs heavy across n
    if len(orbs) >= 2:
        Fl_, Fh_ = orbs[0][0], orbs[-1][0]
        print(f"        3x light = {3*Fl_:.1f}  vs heavy = {Fh_:.1f}   (heavy/light = {Fh_/Fl_:.2f}; partition h = {Fh_/FL:.3f})")

print("\n=== timing calibration (runs 6, 7: dt per point minus ramp+settle) ===")
for fid, dB, in [(6, 0.01), (7, 0.02)]:
    r = open_run(f"/home/hera/measurements/zack/20260822-vti-02/data/{fid}")
    t = r.col("time"); B = r.col("magnet_field")
    dt = np.diff(t)
    # use only the fine-step segment (uniform)
    dBs = np.abs(np.diff(B))
    m = np.isclose(dBs, dB, atol=dB * 0.3)
    med = np.median(dt[m])
    ramp = dB / (0.137 / 60.0)
    print(f"run {fid}: median dt = {med:.2f} s at dB={dB*1e3:.0f} mT (ramp {ramp:.1f} s + settle 3 s) -> reads+overhead = {med - ramp - 3:.2f} s/pt; total {t[-1]-t[0]:.0f} s = {(t[-1]-t[0])/60:.1f} min for {len(t)} pts")

print("\n=== dynamic range: R(n, D=0) from gatemap run 5 along the D=0 line ===")
r5 = open_run("/home/hera/measurements/zack/20260822-vti-02/data/5")
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
vtg = r5.col("k_2400_tg_volt"); vbg = r5.col("k_2400_bg_volt"); x1 = r5.col("sr1_X")
R = x1 / 10e-9
from sharpelab_nb.gates import calc_nD, calc_gate_voltages
nn, DD = calc_nD(vtg, vbg, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
for n0 in [0.8, 1.2, 2.0, 3.2]:
    m = (np.abs(nn - n0) < 0.08) & (np.abs(DD) < 0.02)
    if m.sum():
        print(f"n={n0:+.1f}e12 D~0: R = {np.median(R[m]):.0f} Ohm ({m.sum()} px)")
print("\n=== gate endpoints for the fan fast axis ===")
for n0 in [0.8, 3.2]:
    vt, vb = calc_gate_voltages(n0, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    print(f"n={n0:+.2f}e12, D=0 -> Vtg={vt:+.4f}, Vbg={vb:+.4f}")

print("\n=== fan grid + price ===")
FL_max = h4e * 3.2e16
dinvB = 1.0 / (3 * FL_max)
B_lo, B_hi = 1.0, 10.0
NB = int(np.floor((1/B_lo - 1/B_hi) / dinvB)) + 1
invB = np.linspace(1/B_lo, 1/B_hi, NB)
Bv = np.round(1.0 / invB, 4)
Nn = 71
ppt = None  # fill from timing above by hand
print(f"d(1/B) = {dinvB:.5f} 1/T (1/3 per period of F_L={FL_max:.1f}); N_B = {NB}; B rows {Bv[0]}..{Bv[-1]} T")
print(f"dB at low edge {Bv[0]-Bv[1]:.4f} T ... hmm ascending: first steps {np.diff(Bv)[:3]}, last {np.diff(Bv)[-3:]}")
print(f"N_n = {Nn}, dn = {2.4/(Nn-1):.4f}e12; rays at B=1 T: dn_ray = {4*E/H*1.0/1e16:.4f}e12 -> {4*E/H*1.0/1e16/(2.4/(Nn-1)):.2f} samples/ray")
for fast_read in [0.8]:
    tpt = 1.8 + fast_read
    grid = NB * Nn * tpt
    ramp = (B_hi - B_lo) / 0.137 * 60
    turn = NB * 3.5
    print(f"fast dwell 1.8 s (6 tau) + reads {fast_read:.1f} -> {tpt:.1f} s/pt: grid {grid/3600:.2f} h + traverse {ramp/60:.0f} min + turnaround {turn/60:.0f} min = {(grid+ramp+turn)/3600:.2f} h")
