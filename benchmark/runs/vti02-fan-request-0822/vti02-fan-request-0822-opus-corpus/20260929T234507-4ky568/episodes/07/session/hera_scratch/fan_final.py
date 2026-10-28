"""Final Landau-fan design numbers (the cost-floor design, one proposal)."""
import numpy as np
import scipy.constants as cst
from hera.analysis import luttinger_frequency, field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TAU, TURN_READ = 0.30, 0.098      # sr1 tau (24 dB/oct); run-5 per-point read overhead
B_LO, B_HI = 1.00, 10.0
N_B = 91
n_hi, n_lo, N_n = 3.20, 0.80, 61
FAST_DELAY = 6 * TAU              # landau-fan step 7: ~6 tau when n carries the extracted signal
SLOW_DELAY = 1.0

F_L_max = float(luttinger_frequency(n_hi * 1e12 * 1e4))
F_L_min = float(luttinger_frequency(n_lo * 1e12 * 1e4))
B_vec = field_invB(B_LO, B_HI, N_B)
d_invB = abs(np.median(np.diff(1 / B_vec)))
ns = np.linspace(n_hi, n_lo, N_n)
Vtgs, Vbgs = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
dn = abs(ns[1] - ns[0])
dn_ray = 4 * cst.e / cst.h / 1e4 / 1e12 * B_LO

print(f"B: {N_B} rows uniform-1/B {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T ; d(1/B) = {d_invB:.5f} 1/T")
print(f"   samples/period at F_L(n_max)={F_L_max:.1f} T : {1/(d_invB*F_L_max):.2f}   (Nyquist floor 2, target 3)")
print(f"   dB at bottom row {B_vec[1]-B_vec[0]:.4f} T ; at top row {B_vec[-1]-B_vec[-2]:.3f} T")
print(f"   dF = 1/(1/B_lo - 1/B_hi) = {1/(1/B_LO - 1/B_HI):.2f} T")
print(f"   half-window dF (B-window split Verify): {1/(1/B_LO - 1/np.sqrt(B_LO*B_HI)):.2f} T (low half)")
print()
print(f"n: {N_n} pts {n_hi} -> {n_lo} e12 cm^-2 at D = 0 ; step {dn:.4f}e12")
print(f"   ray spacing at B_lo: {dn_ray:.4f}e12 -> {dn_ray/dn:.2f} pts/ray (floor 2; 15% scale prior -> {dn_ray/dn/1.15:.2f} worst case)")
print(f"   V_tg {Vtgs.min():+.4f} .. {Vtgs.max():+.4f} V   (limit [-0.3, +1.0])")
print(f"   V_bg {Vbgs.min():+.4f} .. {Vbgs.max():+.4f} V   (limit [-1.3, +2.0])")
print(f"   F_L span over the fan: {F_L_min:.2f} -> {F_L_max:.2f} T")
print(f"   periods in the 1/B record at the low-n edge: {F_L_min*(1/B_LO-1/B_HI):.1f} (F_L), "
      f"{0.22*F_L_max*(1/B_LO-1/B_HI):.1f} (light tone at n_max)")
print()
t_pt = FAST_DELAY + TURN_READ
n_pts = N_B * N_n
retrace = max(np.ptp(Vtgs), np.ptp(Vbgs)) / 0.005 * 0.006
traverse = (B_HI - B_LO) / 0.137 * 60
turn = retrace + SLOW_DELAY + 3.0
tot = n_pts * t_pt + traverse + N_B * turn
print(f"cost: fast_delay {FAST_DELAY:.2f} s (6 tau) + {TURN_READ:.3f} s reads = {t_pt:.3f} s/pt")
print(f"      grid {N_B} x {N_n} = {n_pts} pts -> {n_pts*t_pt/3600:.2f} h")
print(f"      field traverse {B_HI-B_LO:.0f} T / 0.137 T/min = {traverse/60:.0f} min = {traverse/3600:.2f} h")
print(f"      row turnaround {turn:.1f} s x {N_B} = {N_B*turn/60:.0f} min")
print(f"      TOTAL {tot/3600:.2f} h ; +10% margin = {tot*1.1/3600:.2f} h")
print(f"      + positioning 0 -> {B_LO} T = {B_LO/0.137:.0f} min")
print()
print("worst corner (n_lo, B_hi): R ~ 600-1350 Ohm (see fan_range.py) at 5 kOhm FS -> fill 0.12-0.27")
np.save("/tmp/none.npy", np.array([0]))
print("\nfirst 5 / last 5 B rows:", np.round(B_vec[:5], 4), np.round(B_vec[-5:], 3))
print("first 3 (Vtg,Vbg):", [(round(a, 4), round(b, 4)) for a, b in zip(Vtgs[:3], Vbgs[:3])])
print("last 3  (Vtg,Vbg):", [(round(a, 4), round(b, 4)) for a, b in zip(Vtgs[-3:], Vbgs[-3:])])
rt = calc_nD(Vtgs, Vbgs, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print("roundtrip n max |err|:", float(np.max(np.abs(np.asarray(rt[0]) - ns))), " D max |err|:", float(np.max(np.abs(rt[1]))))
