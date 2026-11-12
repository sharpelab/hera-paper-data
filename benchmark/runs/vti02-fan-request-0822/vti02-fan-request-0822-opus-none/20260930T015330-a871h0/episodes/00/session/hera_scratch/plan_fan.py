"""Landau-fan design arithmetic: gate vectors along D=0, B grid, price."""
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, GateCalibration, luttinger_frequency

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN, TG_MAX = -0.3, 1.0
BG_MIN, BG_MAX = -1.3, 2.0

# --- accessible n along D = 0 within the TG limit (TG is the binding one)
for n in (-1.30, -1.27, -1.25, -1.20, 3.20, 3.25, 3.27, 3.30):
    vtg, vbg = calc_gate_voltages(n, 0.0, **CAL)
    ok = TG_MIN <= vtg <= TG_MAX and BG_MIN <= vbg <= BG_MAX
    print(f"n={n:+.2f}e12 -> Vtg={vtg:+.4f} Vbg={vbg:+.4f}  {'ok' if ok else 'OUT'}")

N_FAST = 85
n_vec = np.linspace(-1.25, 3.25, N_FAST)
Vtg = np.array([calc_gate_voltages(n, 0.0, **CAL)[0] for n in n_vec])
Vbg = np.array([calc_gate_voltages(n, 0.0, **CAL)[1] for n in n_vec])
print(f"\nn: {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f} e12, step {n_vec[1]-n_vec[0]:.4f}e12, {N_FAST} pts")
print(f"Vtg: {Vtg.min():+.4f} .. {Vtg.max():+.4f} (span {np.ptp(Vtg):.4f} V); step {abs(Vtg[1]-Vtg[0])*1e3:.2f} mV")
print(f"Vbg: {Vbg.min():+.4f} .. {Vbg.max():+.4f} (span {np.ptp(Vbg):.4f} V); step {abs(Vbg[1]-Vbg[0])*1e3:.2f} mV")
print("within limits:", (Vtg.min() >= TG_MIN and Vtg.max() <= TG_MAX and Vbg.min() >= BG_MIN and Vbg.max() <= BG_MAX))

# --- B grid uniform in 1/B
for N in (100, 110, 120, 130):
    B = field_invB(1.0, 10.0, N)
    d = np.diff(1/B)
    print(f"N={N}: d(1/B)={abs(d).max():.5f} -> F_Nyq={1/(2*abs(d).max()):.1f} T; dF_res={1/(1/B.min()-1/B.max()):.2f} T; "
          f"dB max={abs(np.diff(B)).max():.3f} T")

N_B = 120
B_vec = field_invB(1.0, 10.0, N_B)
print(f"\nB: {B_vec[0]:.3f} .. {B_vec[-1]:.3f} T, {N_B} rows; dB: {abs(np.diff(B_vec)).min():.4f} .. {abs(np.diff(B_vec)).max():.3f} T")

# --- price (calibrated on run 5: 4158 pts / 4873 s = 1.172 s/pt at fast_delay=1.0)
SPT = 4873/4158
pts = N_B * N_FAST
t_pts = pts * SPT
t_ramp = (B_vec[-1]-B_vec[0]) / 0.137 * 60           # bare magnet ramp, s
flyback = (np.ptp(Vtg)/0.005)*6e-3                      # TG steps home at volt.step
SLOW_DELAY = 2.0
t_turn = N_B * (flyback + SLOW_DELAY + 3.0)           # + magnet settle_s 3 s
pre = 1.0/0.137*60
tot = t_pts + t_ramp + t_turn
print(f"\npoints {pts} x {SPT:.3f} s = {t_pts/3600:.2f} h")
print(f"magnet ramp (9 T @0.137 T/min) = {t_ramp/3600:.2f} h")
print(f"row turnaround {N_B} x ({flyback:.1f} flyback + {SLOW_DELAY} slow_delay + 3 settle) = {t_turn/3600:.2f} h")
print(f"pre-ramp 0->1 T = {pre/60:.1f} min")
print(f"TOTAL = {(tot+pre)/3600:.2f} h  (+8% realism -> {(tot+pre)*1.08/3600:.2f} h)")

# --- expected frequencies
cal = GateCalibration(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894e16, D_offset=-0.013e9)
for n in (-1.25, -0.6, 0.6, 1.5, 3.25):
    F = luttinger_frequency(n*1e16)
    print(f"n={n:+.2f}e12: F_L={F:5.1f} T; nu(10T)={n*1e16*6.626e-34/(1.602e-19*10):5.1f}; "
          f"lowest minimum (nu=4) at B={F/1:5.2f} T; periods over 1..10 T = {F*(1-0.1):.1f}")

# --- n-resolution vs LL spacing
for B in (1.0, 2.0, 5.0, 10.0):
    dn = 4*1.602e-19*B/6.626e-34*1e-16
    print(f"B={B:4.1f} T: LL(nu-4) spacing dn={dn:.3f}e12 ({dn/(n_vec[1]-n_vec[0]):.1f} fast pts); "
          f"nu-1 spacing {dn/4:.3f}e12 ({dn/4/(n_vec[1]-n_vec[0]):.1f} pts)")
