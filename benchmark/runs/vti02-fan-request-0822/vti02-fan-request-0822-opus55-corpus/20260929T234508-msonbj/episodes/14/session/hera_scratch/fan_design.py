import numpy as np
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import open_run, resolve_channels, luttinger_frequency
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
for n in [3.27, 3.25, 3.2, 2.0, 1.8]:
    vt, vb = calc_gate_voltages(n, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    print(f"n={n}: Vtg {vt:+.4f} Vbg {vb:+.4f}")
# run 6 R in low field
r = open_run("data/6"); ch = {c.cid: c for c in resolve_channels(r.meta)}
B = r.col("magnet_field"); R = np.abs((r.col("sr1_X")/ch["sr1"].gain)/(r.col("sr0_X")/ch["sr0"].gain))
for lo, hi in [(0, 0.3), (0.3, 1.0), (1.0, 1.5), (1.5, 3)]:
    m = (B >= lo) & (B < hi); print(f"run6 B[{lo},{hi}): R {R[m].min():.1f}-{R[m].max():.1f} med {np.median(R[m]):.1f}; point-to-point rms {np.std(np.diff(R[m]))/np.sqrt(2):.2f} Ohm")
t = r.col("time"); m = B > 1.0
print("run6 s/pt above 1 T:", np.median(np.diff(t[m])))
# extension grid
dinv = 0.01
Bext = 1/np.arange(1/0.3, 1/1.5 - 1e-9, -dinv)
print("ext pts", len(Bext), Bext[:3], Bext[-3:], "max dB", np.diff(Bext).max(), "ramp s", (1.5-0.3)/(0.137/60), "overhead s", len(Bext)*3.1)
for Blo in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
    NB = int(round((1/Blo - 0.1)/dinv)) + 1
    dn_max = Blo/(2*10.34); dn = 0.025 if dn_max >= 0.025/1.0*1.0 and Blo >= 0.6 else 0.02
    Nn = int(round(1.25/dn)) + 1
    row = Nn*(1.8+0.12) + 6.5
    tot = NB*row + (10-Blo)/(0.137/60) + 400
    print(f"B_lo {Blo}: N_B {NB}, dn {dn} (Nyq2 {dn_max:.4f}, pts/period {Blo/(10.34*dn):.2f}), N_n {Nn}, row {row:.0f}s, total {tot/3600:.2f} h")
