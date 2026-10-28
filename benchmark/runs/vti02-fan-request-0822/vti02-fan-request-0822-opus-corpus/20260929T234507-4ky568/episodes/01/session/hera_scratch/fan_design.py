"""Fan design arithmetic: accessible D=0 window, Nyquist floors, timing from THIS session's runs."""
import numpy as np, json, gzip
from hera.analysis import open_run, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

print("=== accessible n at D = 0 ===")
for n in np.arange(0.0, 3.6, 0.25):
    vtg, vbg = calc_gate_voltages(n, 0.0, **CAL)
    ok = (TG_MIN <= vtg <= TG_MAX) and (BG_MIN <= vbg <= BG_MAX)
    print(f"  n={n:+5.2f}e12 -> Vtg={vtg:+.4f} Vbg={vbg:+.4f}  {'ok' if ok else 'OUT'}")
for n in (-1.0, -1.2, -1.3, -1.4, -1.5):
    vtg, vbg = calc_gate_voltages(n, 0.0, **CAL)
    print(f"  n={n:+5.2f}e12 -> Vtg={vtg:+.4f} Vbg={vbg:+.4f}  {'ok' if TG_MIN<=vtg<=TG_MAX else 'OUT (TG)'}")

# exact n at Vtg = TG_MAX
from scipy.optimize import brentq
f = lambda n: calc_gate_voltages(n, 0.0, **CAL)[0] - TG_MAX
n_ceiling = brentq(f, 0, 10)
fh = lambda n: calc_gate_voltages(n, 0.0, **CAL)[0] - TG_MIN
n_floor = brentq(fh, -10, 0)
print(f"\n  D=0 electron ceiling (Vtg=TG_MAX): n = {n_ceiling:.4f}e12")
print(f"  D=0 hole floor    (Vtg=TG_MIN): n = {n_floor:.4f}e12")

print("\n=== timing from this session's runs ===")
for rid in (5, 6, 7):
    run = open_run(f"data/{rid}")
    t = run.col("time"); dur = t.max() - t.min(); npts = len(t)
    print(f"  run {rid}: {npts} pts, {dur/60:.1f} min -> {dur/npts:.2f} s/pt   ({run.meta['comments'][0]})")
run5 = open_run("data/5")
t5 = run5.col("time"); v5 = run5.col("k_2400_bg_volt") if "k_2400_bg_volt" in run5.cols else None
print("  run5 cols:", run5.cols)

print("\n=== FAN DESIGN ===")
N_MAX, N_MIN = 3.15, 1.20
B_LO, B_HI = 0.8, 10.0
F_L_max = luttinger_frequency(N_MAX * 1e16)
print(f"  n window {N_MIN}..{N_MAX}e12 ; F_L(n_max) = {F_L_max:.2f} T (fastest expected tone)")
dinvB_nyq = 1 / (2 * F_L_max); dinvB_pref = 1 / (3 * F_L_max)
span = 1 / B_LO - 1 / B_HI
print(f"  1/B span {span:.4f} /T ; Nyquist d(1/B) <= {dinvB_nyq:.5f}, preferred {dinvB_pref:.5f}")
N_B = int(np.ceil(span / dinvB_pref)) + 1
print(f"  -> N_B = {N_B} rows  (actual d(1/B) = {span/(N_B-1):.5f} -> {1/(2*span/(N_B-1)):.1f} T Nyquist ceiling)")
print(f"  dF resolution = {1/span:.2f} T")
for n in (N_MIN, 2.0, 2.5, N_MAX):
    FL = luttinger_frequency(n * 1e16)
    f_part = 0.21 * FL; f_heavy = 0.66 * FL
    print(f"    n={n:.2f}e12: F_L={FL:5.2f}  partner~{f_part:5.2f} T -> {span*f_part:4.1f} periods ; "
          f"heavy~{f_heavy:5.2f} ; separation {f_heavy-f_part:5.2f} T vs 2dF={2/span:.2f}")
dn_ray = 4 * 1.602176634e-19 / 6.62607015e-34 * B_LO / 1e16
print(f"  n-axis: LL ray spacing at B_lo={B_LO} T is dn = {dn_ray:.4f}e12 ; need <= dn/2 = {dn_ray/2:.4f}e12")
N_n = int(np.ceil((N_MAX - N_MIN) / (dn_ray / 2))) + 1
print(f"  -> N_n = {N_n} (dn_grid = {(N_MAX-N_MIN)/(N_n-1):.4f}e12 = {dn_ray/((N_MAX-N_MIN)/(N_n-1)):.2f} pts/ray)")

# gate endpoints
for n in (N_MIN, N_MAX):
    vtg, vbg = calc_gate_voltages(n, 0.0, **CAL)
    print(f"  n={n}e12 -> Vtg={vtg:+.4f} Vbg={vbg:+.4f}")
B_vec = 1 / np.linspace(1 / B_LO, 1 / B_HI, N_B)
print(f"  B rows: {B_vec[0]:.3f} .. {B_vec[-1]:.3f} T ; dB first {B_vec[1]-B_vec[0]:.4f} T, last {B_vec[-1]-B_vec[-2]:.4f} T")
