"""Fan design numbers: onset on the 10 mT segment, sr1 quantization, low-n R anchor, model F(n), grid + wall-clock."""
import numpy as np, warnings, sys, json
from hera.analysis import open_run, sdh_onset, luttinger_frequency, fan_grids, resistance_grids, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count"); import fs_count_b0 as M
CAL = json.load(open("hera_scratch/cal_run5.json")); c_tg, c_bg, n_off, D_off = CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]

r = open_run("data/6"); B = r.col("magnet_field"); X = r.col("sr1_X"); R = X/(r.col("sr0_X")/-1e6)
# --- onset on the 10 mT segment only (the 50 mT leg below 1 T under-samples a 7 T tone below ~0.85 T)
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always"); on = sdh_onset(R, B, b_lo=1.0, r_full_scale=5000.)
    for ww in w: print("warn:", ww.message)
print(on.summary())
# --- sr1_X quantization at 50 uV FS
d = np.diff(np.sort(np.unique(np.round(X, 12)))); d = d[d > 0]
print(f"\nsr1_X quantization at 50 uV FS: min step {d.min():.3e} V = {d.min()/10e-9:.3f} Ohm; median step {np.median(d):.3e} V; unique values {len(np.unique(X))}/{len(X)}")
# --- low-n R anchor from run 5 at (n=1.5, D=0), (n=1.0, D=0)
g = fan_grids("data/5"); rg = resistance_grids(g); R5 = np.abs(rg.R["sr1"]); Vbg5 = g.slow
fs = g.meta["fast_setpoints"]; Vtg5 = np.asarray(fs[0] if isinstance(fs[0], list) else fs)
for n in (1.0, 1.5, 2.0, 3.2):
    vt, vb = calc_gate_voltages(n, 0.0, c_tg, c_bg, n_off, D_off)
    i, j = np.argmin(np.abs(Vbg5 - vb)), np.argmin(np.abs(Vtg5 - vt))
    print(f"run5 R(B=0) at n={n:+.1f}, D=0: (Vtg,Vbg)=({vt:+.3f},{vb:+.3f}) -> grid ({Vtg5[j]:+.3f},{Vbg5[i]:+.3f}) R = {R5[i,j]:.0f} Ohm")
# --- model F(n) on the fan window
print("\nn[e12]  F_L    ABAB light/heavy (m*)            ABCA F (m*)")
for n in (1.5, 2.0, 2.5, 3.0, 3.2):
    ms = M.abab_mstar(n*1e16); _, topo, _, _, Fa = M.abca_fs(n*1e16); _, ma = M.abca_mstar(n*1e16)
    print(f"{n:+.1f}  {float(luttinger_frequency(n*1e16)):5.1f}  " + "  ".join(f"{F:5.1f} ({m:.3f})" for F, m in ms) + f"   {Fa:5.1f} ({ma:.3f}) {topo}")
# --- grid + cost
n_lo, n_hi, N_n = 1.5, 3.2, 51
ns = np.linspace(n_hi, n_lo, N_n); Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_off, D_off)
print(f"\nfast axis: n {n_hi}->{n_lo}, {N_n} pts, dn = {(n_hi-n_lo)/(N_n-1):.4f}e12; Vtg {Vt.min():+.4f}..{Vt.max():+.4f}, Vbg {Vb.min():+.4f}..{Vb.max():+.4f}")
FLmax = float(luttinger_frequency(n_hi*1e16)); dinv = 0.010
print(f"Delta(1/B) = {dinv} 1/T -> Nyquist F = {0.5/dinv:.0f} T; F_L(n_hi) = {FLmax:.1f} T (x{0.5/dinv/FLmax:.1f}); at 1.15 scale {1.15*FLmax:.1f} T (x{0.5/dinv/(1.15*FLmax):.1f})")
for B_lo in (1.0, 0.8, 0.7, 0.5):
    for B_hi in (7.0, 10.0):
        N_B = int(np.ceil((1/B_lo - 1/B_hi)/dinv)) + 1
        t_pt = 1.2 + 0.12; row = N_n*t_pt + 1.0 + 3.0 + 3.0
        ramp = (B_hi - B_lo)/0.137*60
        tot = N_B*row + ramp
        rays = 0.0967*B_lo/((n_hi-n_lo)/(N_n-1))
        dF = 1/(1/B_lo - 1/B_hi)
        print(f"B {B_lo}->{B_hi}: N_B {N_B:3d} rows, {row:.0f} s/row, ramp {ramp/60:.0f} min -> {tot/3600:.2f} h (x1.08 = {1.08*tot/3600:.2f} h); rays/dn at B_lo {rays:.2f}; dF {dF:.2f} T; partner periods at n=3.2 (7.3T) {7.3*(1/B_lo-1/B_hi):.1f}, n=2.0 (3.6T) {3.6*(1/B_lo-1/B_hi):.1f}")
# extension
ext = field_invB(0.3, 1.3, 129); print(f"\nextension: {len(ext)} pts 0.3->1.3 T uniform 1/B, d(1/B) = {np.abs(np.diff(1/ext)).mean():.4f}; dB at ends {ext[1]-ext[0]:.4f}, {ext[-1]-ext[-2]:.4f} T; time ramp {(1.3-0.3)/0.137:.1f} min + pts {len(ext)*3.1/60:.1f} min + 0->0.3 {0.3/0.137:.1f} min")
