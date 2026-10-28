import numpy as np
from pathlib import Path
from hera.analysis import open_run, resolve_channels, fan_grids, resistance_grids, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
D = Path(__file__).resolve().parent.parent / "data"
# --- noise vs sensitivity: point-to-point scatter (diff/sqrt2) of R in smooth regions
r6 = open_run(D/"6"); ch = {c.cid: c for c in resolve_channels(r6.meta)}
R6 = (r6.col("sr1_X")/ch["sr1"].gain)/(r6.col("sr0_X")/ch["sr0"].gain); B6 = r6.col_at(r6.col_indices("magnet_field")[-1])
m = B6 < 1.0; print(f"run 6 (50 uV FS) B<1 T: p2p noise {np.std(np.diff(R6[m]))/np.sqrt(2):.2f} Ohm")
g = fan_grids(str(D/"5")); R5 = np.abs(resistance_grids(g).R["sr1"])
cols = slice(50, 66)  # high Vtg, metallic-ish region
print(f"run 5 (100 uV FS) metallic cols: p2p noise along fast {np.median(np.std(np.diff(R5[:, cols], axis=1), axis=1))/np.sqrt(2):.2f} Ohm (includes real slope)")
print(f"run 5 row-to-row noise (same Vtg, adjacent Vbg): {np.median(np.std(np.diff(R5[:, cols], axis=0), axis=0))/np.sqrt(2):.2f} Ohm")
# --- gate path along region-A D = 0
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.round(np.linspace(-1.24, 3.24, 113), 4)
Vt, Vb = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n {n_vec[0]}..{n_vec[-1]} step {n_vec[1]-n_vec[0]:.3f}, {len(n_vec)} pts; Vtg {Vt.min():+.4f}..{Vt.max():+.4f} (lim -0.3, 1.0); Vbg {Vb.min():+.4f}..{Vb.max():+.4f} (lim -1.3, 2.0)")
print(f"per-pt dVtg {np.diff(Vt).mean()*1e3:.2f} mV, dVbg {np.diff(Vb).mean()*1e3:.2f} mV; n=0 at index {np.argmin(abs(n_vec))}")
nn, DD = calc_nD(Vt, Vb, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"]); print("roundtrip max |dn|, |D|:", abs(nn-n_vec).max(), abs(DD).max())
# --- field grid: B-uniform 0.2 T from 10 down to 5.2, then 1/B-uniform (d(1/B)=0.008) from 5.0 to 0.8
Bhi = np.round(np.arange(10.0, 5.1999, -0.2), 4)
invB = np.linspace(0.2, 1.25, int(round((1.25-0.2)/0.008))+1)
Blo = 1/invB
B_vec = np.concatenate([Bhi, Blo])
print(f"B rows {len(B_vec)} ({len(Bhi)} B-uniform + {len(Blo)} 1/B-uniform, d(1/B)={invB[1]-invB[0]:.5f}); B {B_vec[0]}..{B_vec[-1]:.4f}; max step {np.abs(np.diff(B_vec)).max():.3f} T; min step {np.abs(np.diff(B_vec)).min()*1e3:.1f} mT")
print(f"Nyquist F on 1/B part: {1/(2*(invB[1]-invB[0])):.1f} T; dF (0.8-5 T part) {1/(1.25-0.2):.2f} T; dF (0.8-10) {1/(1.25-0.1):.2f} T")
print("F_L at n ends (region A):", float(luttinger_frequency(1.24e16)), float(luttinger_frequency(3.24e16)), " region B top (n+0.43):", float(luttinger_frequency(3.67e16)))
# --- price: calibrated from run 5 (megasweep 66x63, fast 1 s, slow 3 s -> 81.2 min => 1.10 s/pt + row overhead)
pp = 1.10 + 0.04          # + second gate set per point
fly = (np.ptp(Vt)/0.005 + np.ptp(Vb)/0.005) * 0.006
row = len(n_vec)*pp + fly + 3.0 + 3.0 + 1.0   # slow_delay 3, magnet settle 3, ramp poll ~1
ramp_fan = (B_vec[0]-B_vec[-1]) / (0.137/60)
pre = 10.0 / (0.137/60)
tot = len(B_vec)*row + ramp_fan + pre
print(f"flyback {fly:.1f} s; row {row:.0f} s; rows {len(B_vec)} -> meas {len(B_vec)*row/3600:.2f} h; fan ramps {ramp_fan/60:.0f} min; pre-ramp 0->10 T {pre/60:.0f} min; total {tot/3600:.2f} h (+7% = {1.07*tot/3600:.2f} h)")
t_hi = len(Bhi)*row + (10-5.2)/(0.137/60)
print(f"10->5.2 T block (QH region) lands {t_hi/60:.0f} min after the fan starts")
np.savez(Path(__file__).parent/"fan_grid.npz", n=n_vec, Vtg=Vt, Vbg=Vb, B=B_vec)
