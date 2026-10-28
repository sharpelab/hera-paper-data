"""Final committed fan design — the numbers that go in the cell + the markdown."""
import sys, numpy as np, importlib.util as iu


def L(n, p):
    s = iu.spec_from_file_location(n, p); m = iu.module_from_spec(s)
    sys.modules[n] = m; s.loader.exec_module(m); return m


fc = L("tet", "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py")
tri = L("tri", "/home/hera/measurement_env/hera/models/trilayer_fs_count/fs_count_b0.py")
from hera.analysis import luttinger_frequency, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
SCALE = 30.0 / 33.09          # measured global density rescale from run 6 (sum tone / F_L nominal)
N_MIN, N_MAX = 2.2, 3.2
B_LO, B_MAX = 0.65, 10.0
TAU, K = 0.3, 7
E_H = 2.417989e14

FL_max = float(luttinger_frequency(N_MAX * 1e16))
d_pref = 1.0 / (3 * FL_max)
span = 1 / B_LO - 1 / B_MAX
N_B = int(np.ceil(span / d_pref)) + 1
dn_ray = 4 * E_H * B_LO / 1e16
N_n = int(np.ceil((N_MAX - N_MIN) / (dn_ray / 2))) + 1

print(f"n_max={N_MAX}: F_L={FL_max:.2f} T; d(1/B) pref {d_pref:.5f}, Nyquist {1/(2*FL_max):.5f}")
print(f"N_B = {N_B}, delivered d(1/B) = {span/(N_B-1):.5f} 1/T   (1/B span {span:.4f}, dF = {1/span:.2f} T)")
print(f"N_n = {N_n}, dn = {(N_MAX-N_MIN)/(N_n-1):.5f}e12 (ray floor {dn_ray/2:.5f} at B_lo={B_LO})")
print(f"total points {N_B*N_n}")

print("\n--- claim-resolution check at the low-n edge (model at TRUE density = "
      f"{SCALE:.3f} x nominal) ---")
for nn in (N_MIN, 2.6, N_MAX):
    nt = nn * SCALE
    _, orb = fc.abab_fs(nt * 1e16)
    f = sorted(x[0] for x in orb)
    FL = float(luttinger_frequency(nt * 1e16))
    _, torb = tri.aba_fs(nt * 1e16)
    tf = sorted(x[0] for x in torb)
    print(f"  n_nom {nn:.2f} (true {nt:.2f}): ABAB {['%.2f'%x for x in f]} sum {sum(f):.2f} = F_L {FL:.2f} | "
          f"partner periods {span*f[0]:.1f} (>=5) | heavy-vs-F_L {FL-f[1]:.2f} T = {(FL-f[1])*span:.1f} dF (>=2) | "
          f"3L-ABA {['%.2f'%x for x in tf]}")
    # B-window split halves
    half = span / 2
    print(f"      B-window split halves: dF = {1/half:.2f} T; heavy-vs-F_L = {(FL-f[1])*half:.1f} half-dF (>=2)")

print("\n--- gate vectors / validator margins ---")
ns = np.linspace(N_MIN, N_MAX, N_n)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  Vtg {Vtgs.min():+.4f} -> {Vtgs.max():+.4f} (limit -0.3/+1.0; margin {1.0-Vtgs.max():+.4f})")
print(f"  Vbg {Vbgs.min():+.4f} -> {Vbgs.max():+.4f} (limit -1.3/+2.0; margin {2.0-Vbgs.max():+.4f})")
print(f"  roundtrip max |D| = {np.abs(calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])[1]).max():.2e} V/nm")
print(f"  last column n = {ns[-1]:.4f} (= run 6 spot 3.2 -> grid-change reproduction check)")

print("\n--- B schedule ---")
B_vec = field_invB(B_LO, B_MAX, N_B)
print(f"  B_vec: {B_vec[0]:.4f} -> {B_vec[-1]:.4f} T, monotonic {bool(np.all(np.diff(B_vec)>0))}")
print(f"  first 5 dB: {np.round(np.diff(B_vec[:6]),4)}   last 5 dB: {np.round(np.diff(B_vec[-6:]),4)}")
print(f"  max single-row dB = {np.diff(B_vec).max():.3f} T ({np.diff(B_vec).max()/0.137:.1f} min ramp)")

print("\n--- cost ---")
t_pt = K * TAU + 0.098          # run-5 calibrated readback overhead at NPLC=1
flyback = (abs(Vtgs[-1]-Vtgs[0])/0.005 + abs(Vbgs[-1]-Vbgs[0])/0.005) * 0.006
slow_delay = 3.0
traverse = (B_MAX - B_LO)/0.137*60
grid = N_B * N_n * t_pt
fixed = N_B * (slow_delay + flyback)
tot = traverse + grid + fixed
print(f"  fast_delay {K*TAU:.1f} s (= {K} tau, tau={TAU} s @ 24 dB/oct), t_pt {t_pt:.3f} s")
print(f"  traverse {traverse/3600:.2f} h | grid {grid/3600:.2f} h | row fixed {fixed/3600:.2f} h (flyback {flyback:.2f} s)")
print(f"  TOTAL {tot/3600:.2f} h  -> headline with 10% {tot*1.10/3600:.2f} h")

print("\n--- checkpoint schedule (cumulative wall clock) ---")
cum = 0.0
marks = {}
for i in range(N_B):
    if i:
        cum += (B_vec[i]-B_vec[i-1])/0.137*60
    cum += slow_delay + flyback + N_n*t_pt
    for tgt in (0.68, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0):
        if tgt not in marks and B_vec[i] >= tgt:
            marks[tgt] = (i+1, cum/3600)
for tgt, (row, h) in marks.items():
    print(f"  B = {tgt:4.2f} T reached at row {row:3d} / {N_B}  ->  t = {h:.2f} h")

print("\n--- dynamic range ---")
print("  worst corner n=2.2e12 x B=10 T: R(B=0) ~ 68 Ohm (run 5) x MR 10.5x (run 6, n=3.2)")
print("  -> ~700 Ohm expected; even a 3x underestimate (2100 Ohm) is 42% of the")
print(f"     50 uV / 10 nA full scale = {50e-6/(1/100e6):.0f} Ohm. Keep 50 uV (inherited from run 6).")
