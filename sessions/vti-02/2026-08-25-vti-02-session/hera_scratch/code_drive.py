# HERA — drive-current linearity scan, then commit the acquisition config.
# Sets lock-in oscillator amplitude / sensitivity / tau / slope only.
# No gate motion, no field motion, no sweep, no run directory.
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vtg, _vbg, _vsi = k_2400_tg.volt(), k_2400_bg.volt(), dc205.voltage()
_B, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={_vtg:+.4f} V  V_bg={_vbg:+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vtg) < 1e-3 and abs(_vbg) < 1e-3 and abs(_vsi) < 0.01, "gates not parked at 0"
assert abs(_B) < 0.02, "field not at zero"
assert 1.0 <= _Ts <= 1.4, "sample not at base"

_RB = meas_config["bias_resistor"]
_G0 = meas_config["sr0_gain"]
_SENS = [2e-9, 5e-9, 1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6, 1e-5, 2e-5,
         5e-5, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1.0]


def _pick_sens(expected_V):
    """smallest ladder sensitivity that puts |X| below ~45% of full scale"""
    for _s in _SENS:
        if expected_V / _s < 0.45:
            return _s
    return _SENS[-1]


sr1.time_constant(0.3)
sr1.filter_slope(24)
sr0.time_constant(0.3)
sr0.filter_slope(24)

print()
print("=== Part 1: drive linearity (constant R_xx across 5x current = no heating) ===")
print(f"{'drive (V)':>10} {'I (A)':>12} {'V_xx (V)':>12} {'R_xx (ohm)':>11} "
      f"{'sr0 load':>9} {'sr1 load':>9} {'theta':>7}")
_AMPS = [1.0, 2.0, 5.0]
_lin = []
for _a in _AMPS:
    sr1.amplitude(_a)
    sr0.sensitivity(_pick_sens(_a / _RB * abs(_G0)))
    sr1.sensitivity(_pick_sens(_a / _RB * 210.0))
    interruptible_sleep(4.0)                      # re-range + drive change settle
    _x0 = np.mean([sr0.X() for _ in range(3)])
    _x1s = []
    for _j in range(6):
        interruptible_sleep(2.1)
        _x1s.append(sr1.X())
    _x1 = float(np.mean(_x1s))
    _I = _x0 / _G0
    _R = _x1 / _I
    _lin.append((_a, _I, _x1, _R))
    print(f"{_a:>10.2f} {_I:>12.4e} {_x1:>12.4e} {_R:>11.3f} "
          f"{abs(_x0)/sr0.sensitivity():>9.3f} {abs(_x1)/sr1.sensitivity():>9.3f} {sr1.P():>7.2f}")

_R_ref = _lin[0][3]
print()
print(f"reference R_xx at {_AMPS[0]:.1f} V drive = {_R_ref:.3f} ohm; tolerance 2%")
_ok = [row for row in _lin if abs(row[3] - _R_ref) / _R_ref <= 0.02]
for _a, _I, _x1, _R in _lin:
    _d = (_R - _R_ref) / _R_ref
    print(f"   drive {_a:.1f} V: R_xx = {_R:8.3f} ohm  ({_d:+.2%})  "
          f"{'OK' if abs(_d) <= 0.02 else 'REJECT (heating / non-linear)'}")
_A_SEL = max(row[0] for row in _ok)
print(f"-> selected drive = {_A_SEL:.1f} V  (I_bias = {_A_SEL/_RB:.3e} A nominal)")

# ---------- Part 2: scatter at the selected drive ----------
sr1.amplitude(_A_SEL)
sr0.sensitivity(_pick_sens(_A_SEL / _RB * abs(_G0)))
sr1.sensitivity(_pick_sens(_A_SEL / _RB * 210.0))
interruptible_sleep(4.0)
_I_sel = np.mean([sr0.X() for _ in range(3)]) / _G0

print()
print(f"=== Part 2: scatter at {_A_SEL:.1f} V drive (I = {_I_sel:.4e} A), 24 dB/oct ===")
print(f"{'tau (s)':>8} {'dwell (s)':>10} {'mean X (V)':>13} {'std X (V)':>12} "
      f"{'dR_xx (ohm)':>12} {'dR/R':>9}")
_scat = {}
for _tau in (0.3, 0.1):
    sr1.time_constant(_tau)
    _dw = 7 * _tau
    interruptible_sleep(max(10 * _tau, 1.0))
    _s = []
    for _j in range(24):
        interruptible_sleep(_dw)
        _s.append(sr1.X())
    _s = np.array(_s)
    _m, _sd = _s.mean(), _s.std(ddof=1)
    _dR = _sd / abs(_I_sel)
    _scat[_tau] = (_dw, _dR, _sd / abs(_m))
    print(f"{_tau:>8.2f} {_dw:>10.2f} {_m:>13.5e} {_sd:>12.3e} {_dR:>12.4g} {_sd/abs(_m):>9.2%}")

# ---------- commit ----------
_TAU_SEL = 0.1 if _scat[0.1][2] < 0.005 else 0.3
sr1.time_constant(_TAU_SEL)
sr1.filter_slope(24)
sr0.time_constant(_TAU_SEL)
sr0.filter_slope(24)
_DWELL = 7 * _TAU_SEL
interruptible_sleep(3.0)

print()
print("=== COMMITTED ACQUISITION CONFIG ===")
print(f"  drive        : {sr1.amplitude()} V @ {sr1.frequency()} Hz -> I_bias = {_I_sel:.4e} A")
print(f"  sr0          : sens={sr0.sensitivity():.3e}, tau={sr0.time_constant()} s, "
      f"slope={sr0.filter_slope()} dB/oct")
print(f"  sr1          : sens={sr1.sensitivity():.3e}, tau={sr1.time_constant()} s, "
      f"slope={sr1.filter_slope()} dB/oct")
print(f"  dwell        : {_DWELL:.2f} s   (7*tau, 24 dB/oct settling floor)")
print(f"  scatter      : dR_xx = {_scat[_TAU_SEL][1]:.3g} ohm ({_scat[_TAU_SEL][2]:.2%} of R_xx)")
print(f"  rule         : tau=0.1 if its dR/R < 0.50%, else tau=0.3 "
      f"(measured {_scat[0.1][2]:.2%} at tau=0.1)")
print(f"  R_xx(0,0)    : {_R_ref:.2f} ohm")

DWELL = _DWELL          # session-wide per-point dwell, used by later cells
I_BIAS = _I_sel
print()
print(f"pricing at {_DWELL + 0.25:.2f} s/pt incl. 0.25 s fp overhead:")
print(f"  4-leg gate-C @151 pt : {(_DWELL+0.25)*151*4/60:.1f} min")
print(f"  101 x 101 gate map   : {(_DWELL+0.25)*101*101/3600:.2f} h")
print(f"  81 x 51 gate map     : {(_DWELL+0.25)*81*51/3600:.2f} h")
print()
print("DRIVE-CONFIG: done")
