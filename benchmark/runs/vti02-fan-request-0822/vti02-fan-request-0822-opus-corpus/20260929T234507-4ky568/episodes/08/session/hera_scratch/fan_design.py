"""Fan design arithmetic: grid, Nyquist both axes, dF, cost. Electron side, D=0."""
import numpy as np, sys
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import luttinger_frequency, field_invB

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX, BG_MIN, BG_MAX = -0.3, 1.0, -1.3, 2.0
e_over_h = 1.602176634e-19 / 6.62607015e-34      # m^-2 T^-1

N_LO, N_HI = 2.10, 3.22          # 1e12 cm^-2
B_LO, B_MAX = 0.70, 7.50
N_N, N_B = 47, 132
TAU, FAST_DELAY, SLOW_DELAY = 0.3, 1.8, 1.0
T_OVERHEAD = 0.098               # measured, run 5 (gatemap, same fp set, fast_delay 1.0 -> 1.098 s/pt)

print("== gate window ==")
for n in (N_LO, N_HI):
    vtg, vbg = calc_gate_voltages(n, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    ok = TG_MIN <= vtg <= TG_MAX and BG_MIN <= vbg <= BG_MAX
    print(f"  n={n:+.2f}e12 D=0 -> Vtg={vtg:+.4f} Vbg={vbg:+.4f}  in-limits={ok} "
          f"(TG headroom {TG_MAX - vtg:+.4f} V)")
ns = np.linspace(N_LO, N_HI, N_N)
Vtgs, Vbgs = calc_gate_voltages(ns, 0.0 * ns, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"  Vtg span {Vtgs.min():+.4f}..{Vtgs.max():+.4f} ({np.ptp(Vtgs)*1e3:.0f} mV), "
      f"Vbg span {Vbgs.min():+.4f}..{Vbgs.max():+.4f} ({np.ptp(Vbgs)*1e3:.0f} mV)")

print("\n== B grid (uniform in 1/B) ==")
B_vec = field_invB(B_LO, B_MAX, N_B)
inv = 1 / B_vec
dinv = abs(np.median(np.diff(inv)))
F_L_max = float(luttinger_frequency(N_HI * 1e16))
print(f"  N_B={N_B}  d(1/B)={dinv:.5f} 1/T  -> Nyquist F = {1/(2*dinv):.1f} T")
print(f"  F_L(n_max={N_HI}e12) = {F_L_max:.2f} T  -> need d(1/B) <= {1/(2*F_L_max):.5f} (Nyq) / "
      f"{1/(3*F_L_max):.5f} (pref 1/3)  --> {'OK, 1/3 met' if dinv <= 1/(3*F_L_max) else 'CHECK'}")
print(f"  dB steps: {np.diff(np.sort(B_vec)).min()*1e3:.1f} mT at {B_LO} T ... "
      f"{np.diff(np.sort(B_vec)).max()*1e3:.0f} mT at {B_MAX} T")
span_inv = 1 / B_LO - 1 / B_MAX
dF = 1 / span_inv
print(f"  1/B record span = {span_inv:.4f} 1/T  -> dF = {dF:.3f} T  (trust a split past 2dF = {2*dF:.2f} T)")

print("\n== n grid / ray Nyquist ==")
dn = (N_HI - N_LO) / (N_N - 1)
dn_ray = 4 * e_over_h * B_LO / 1e16          # LL ray spacing in 1e12 cm^-2, at B_LO
print(f"  N_n={N_N}  dn={dn*1e12:.3e} cm^-2 ({dn:.4f}e12);  LL ray spacing at {B_LO} T = {dn_ray:.4f}e12")
print(f"  -> {dn_ray/dn:.2f} pts per ray at B_lo (floor 2, prefer 3); "
      f"3 pts/ray above B = {3*dn/(4*e_over_h/1e16):.2f} T")

print("\n== model templates over the fan window ==")
print(f"{'n':>6} {'F_L':>7} {'ABAB f1':>8} {'ABAB f2':>8} {'f2/f1':>6} {'3xf1':>7} "
      f"{'f2-3f1':>7} {'ABCA':>7} {'per(f1)':>8} {'per(f2)':>8}")
for n in np.linspace(N_LO, N_HI, 6):
    F_L = float(luttinger_frequency(n * 1e16))
    _, orbs = M.abab_fs(n * 1e16)
    fs = sorted(f for f, k in orbs)
    f1, f2 = fs[0], fs[-1]
    _, _, _, _, Fa = M.abca_fs(n * 1e16)
    print(f"{n:6.2f} {F_L:7.2f} {f1:8.2f} {f2:8.2f} {f2/f1:6.2f} {3*f1:7.2f} {f2-3*f1:7.2f} "
          f"{Fa:7.2f} {f1*span_inv:8.1f} {f2*span_inv:8.1f}")

print("\n== cost ==")
npts = N_B * N_N
t_pt = FAST_DELAY + T_OVERHEAD
meas = npts * t_pt
traverse = (B_MAX - B_LO) / 0.137 * 60
flyback = np.ptp(Vbgs) / 5e-3 * 6e-3          # bg is the wider span; 5 mV step, 6 ms/write
row_oh = 3.0 + SLOW_DELAY + flyback           # magnet settle_s + slow_delay + flyback
rows = N_B * row_oh
tot = meas + traverse + rows
print(f"  points {npts} x {t_pt:.2f} s = {meas/3600:.2f} h")
print(f"  traverse {B_LO}->{B_MAX} T bare = {traverse/60:.1f} min")
print(f"  row overhead {row_oh:.1f} s x {N_B} = {rows/60:.1f} min (flyback {flyback:.2f} s)")
print(f"  TOTAL = {tot/3600:.2f} h  (+10% margin -> {tot*1.10/3600:.2f} h)")
print(f"  dwell = {FAST_DELAY/TAU:.0f} tau (tau={TAU} s, 24 dB/oct)")
