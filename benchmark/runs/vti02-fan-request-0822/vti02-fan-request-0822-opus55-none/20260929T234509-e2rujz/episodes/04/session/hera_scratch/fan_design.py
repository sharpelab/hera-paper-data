import numpy as np, json
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, open_run
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
args = (CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
ns = np.linspace(-2, 4.5, 6501); Vt, Vb = calc_gate_voltages(ns, 0*ns, *args)
ok = (Vt >= -0.3+0.01) & (Vt <= 1.0-0.01) & (Vb >= -1.3+0.01) & (Vb <= 2.0-0.01)
print("D=0 window w/ 10 mV margin: n", ns[ok].min(), ns[ok].max())
for n_lo, n_hi, dn in [(-1.2, 3.25, 0.05)]:
    N = int(round((n_hi-n_lo)/dn))+1; n_vec = np.linspace(n_lo, n_hi, N)
    vt, vb = calc_gate_voltages(n_vec, 0*n_vec, *args)
    print(f"n {n_lo}..{n_hi} step {dn}: {N} pts; Vtg {vt.min():+.4f}..{vt.max():+.4f}, Vbg {vb.min():+.4f}..{vb.max():+.4f}; dVtg/pt {np.diff(vt).mean()*1e3:.1f} mV dVbg/pt {np.diff(vb).mean()*1e3:.1f} mV")
# per-point calibration from run 5 (gatemap, fast_delay 1 s) and run 6 (field steps)
r5 = open_run("data/5"); t = r5.col("time"); print("run5 s/pt (incl. turnaround):", (t[-1]-t[0])/len(t), "rows", 63)
tr = t.reshape(63, 66); print("run5 in-row s/pt:", np.median(np.diff(tr, axis=1)), " row turnaround s:", np.median(tr[1:,0]-tr[:-1,-1]))
r6 = open_run("data/6"); t6 = r6.col("time"); B6 = r6.col("magnet_field"); dt = np.diff(t6); dB = np.diff(B6)
m = (dB > 0.009) & (dB < 0.011); print("run6 10 mT step: median dt", np.median(dt[m]), "-> overhead beyond bare ramp", np.median(dt[m]) - 0.01/(0.137/60))
for Blo, Fn in [(1.0, 50), (1.2, 50), (0.8, 50), (1.0, 40)]:
    Nr = int(np.ceil((1/Blo-1/10.0)*2*Fn))+1; Bv = field_invB(Blo, 10.0, Nr)
    for Nf in [90]:
        row = Nf*1.21 + 3.5 + 3 + 6   # flyback, slow_delay, settle+reads at first pt
        ramp = (10.0-0)/0.137*60
        tot = Nr*row + ramp
        print(f"B {Blo}->10 1/B-uniform, F_nyq {Fn}: {Nr} rows, dF {1/(1/Blo-0.1):.2f} T, dB at 10 T {Bv[-1]-Bv[-2]:.2f} T, at {Blo} T {Bv[1]-Bv[0]:.3f}; Nf {Nf}: {tot/3600:.2f} h (+7% {tot*1.07/3600:.2f} h)")
