# HERA — sr1 ranging + settling/noise characterisation. Sets lock-in
# sensitivity / time-constant / filter-slope only (operator-granted). No gate
# moves, no field moves, no sweep, no run directory.
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vtg, _vbg, _vsi = k_2400_tg.volt(), k_2400_bg.volt(), dc205.voltage()
_B, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={_vtg:+.4f} V  V_bg={_vbg:+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vtg) < 1e-3 and abs(_vbg) < 1e-3 and abs(_vsi) < 0.01, "gates not parked at 0"
assert abs(_B) < 0.02, "field not at zero"
assert 1.0 <= _Ts <= 1.4, "sample not at base"

_I = sr0.X() / meas_config["sr0_gain"]
print(f"transport current I = {_I:.5e} A")
print()

# ---------------- Part 1: range sr1 off the rail ----------------
SENS_LADDER = [2e-6, 5e-6, 1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2]
print("=== Part 1: sr1 sensitivity ladder (target |X|/sens < 0.5) ===")
print(f"{'sens (V)':>10} {'X (V)':>13} {'|X|/sens':>9} {'R_xx (ohm)':>12}")
_chosen = None
for _s in SENS_LADDER:
    sr1.sensitivity(_s)
    interruptible_sleep(7 * sr1.time_constant())
    _X = sr1.X()
    _frac = abs(_X) / _s
    print(f"{_s:>10.1e} {_X:>13.5e} {_frac:>9.3f} {_X/_I:>12.5e}")
    if _frac < 0.5:
        _chosen = _s
        break

if _chosen is None:
    print("!! sr1 still loaded at the top of the ladder - stopping, this is not a ranging problem")
else:
    interruptible_sleep(7 * sr1.time_constant())
    _Vxx = sr1.X()
    _Rxx0 = _Vxx / _I
    print()
    print(f"sr1 ranged at {_chosen:.1e} V  ->  V_xx = {_Vxx:.5e} V,  "
          f"R_xx(V_tg=0,V_bg=0) = {_Rxx0:.5e} ohm  ({_Rxx0/1e3:.3f} kohm)")
    print(f"theta = {sr1.P():+.2f} deg")

# ---------------- Part 2: settling / noise trade ----------------
print()
print("=== Part 2: output noise vs (tau, slope) at fixed setpoint ===")
print("std is per-point uncertainty at a settled point; the dwell column is the")
print("theory settling floor (7*tau at 24 dB/oct, 5*tau at 12 dB/oct), NOT measured here.")
print()
_TAU0, _SLOPE0 = sr1.time_constant(), sr1.filter_slope()
_CONFIGS = [(0.3, 24), (0.1, 24), (0.03, 24), (0.1, 12)]
_N = 24
_results = []
print(f"{'tau (s)':>8} {'slope':>6} {'dwell (s)':>10} {'mean X (V)':>13} {'std X (V)':>12} "
      f"{'dR_xx (ohm)':>12} {'dR/R':>9}")
for _tau, _slope in _CONFIGS:
    sr1.time_constant(_tau)
    sr1.filter_slope(_slope)
    _k = 7 if _slope == 24 else 5
    _dwell = _k * _tau
    interruptible_sleep(max(10 * _tau, 1.0))
    _samples = np.array([sr1.X() for _ in range(_N)])
    _m, _sd = _samples.mean(), _samples.std(ddof=1)
    _dR = _sd / abs(_I)
    _results.append((_tau, _slope, _dwell, _m, _sd, _dR))
    print(f"{_tau:>8.3g} {_slope:>6d} {_dwell:>10.2f} {_m:>13.5e} {_sd:>12.3e} "
          f"{_dR:>12.4g} {_sd/abs(_m):>9.2%}")

# restore the rack as found (sensitivity stays ranged; tau/slope revert)
sr1.time_constant(_TAU0)
sr1.filter_slope(_SLOPE0)
print()
print(f"restored sr1 tau={sr1.time_constant()} s, slope={sr1.filter_slope()} dB/oct "
      f"(sensitivity left at {sr1.sensitivity():.1e} V)")

# ---------------- pricing helper ----------------
print()
print("=== what each choice prices, per-point and for a 101x101 first gate map ===")
_OVERHEAD = 0.25  # s/pt, rig-card fp readback overhead at NPLC=1
print(f"{'tau (s)':>8} {'slope':>6} {'s/pt':>7} {'101x101':>10} {'dR_xx (ohm)':>12}")
for _tau, _slope, _dwell, _m, _sd, _dR in _results:
    _spp = _dwell + _OVERHEAD
    print(f"{_tau:>8.3g} {_slope:>6d} {_spp:>7.2f} {_spp*101*101/3600:>9.2f} h {_dR:>12.4g}")
print()
print("RANGE-SETTLE: done")
