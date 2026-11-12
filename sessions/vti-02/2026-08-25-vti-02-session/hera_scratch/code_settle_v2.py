# HERA — corrected settling/noise characterisation. Sets lock-in tau/slope
# (operator-granted) and makes one +50 mV top-gate excursion that returns to 0.
# No field motion, no sweep, no run directory.
import time

import numpy as np

# --- preconditions this cell assumes but does not set ---
_vtg, _vbg, _vsi = k_2400_tg.volt(), k_2400_bg.volt(), dc205.voltage()
_B, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={_vtg:+.4f} V  V_bg={_vbg:+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vtg) < 1e-3 and abs(_vbg) < 1e-3 and abs(_vsi) < 0.01, "gates not parked at 0"
assert abs(_B) < 0.02, "field not at zero"
assert 1.0 <= _Ts <= 1.4, "sample not at base"
assert np.isclose(sr1.sensitivity(), 5e-6), "sr1 not at the ranged sensitivity from cell 37"

_I = sr0.X() / meas_config["sr0_gain"]
print(f"transport current I = {_I:.5e} A   (R_xx = X_sr1 / I)")
_TAU0, _SLOPE0 = sr1.time_constant(), sr1.filter_slope()

# ---------- Part 2 (corrected): scatter sampled AT the dwell interval ----------
print()
print("=== Part 2 (corrected): point-to-point scatter, samples spaced by the dwell ===")
_CONFIGS = [(0.3, 24), (0.1, 24), (0.03, 24), (0.1, 12)]
_N = 24
_results = []
print(f"{'tau (s)':>8} {'slope':>6} {'dwell (s)':>10} {'mean X (V)':>13} {'std X (V)':>12} "
      f"{'dR_xx (ohm)':>12} {'dR/R':>9} {'span (s)':>9}")
for _tau, _slope in _CONFIGS:
    sr1.time_constant(_tau)
    sr1.filter_slope(_slope)
    _k = 7 if _slope == 24 else 5
    _dwell = _k * _tau
    interruptible_sleep(max(10 * _tau, 1.0))
    _t0 = time.time()
    _samples = []
    for _j in range(_N):
        interruptible_sleep(_dwell)          # <- the fix: independent samples
        _samples.append(sr1.X())
    _samples = np.array(_samples)
    _span = time.time() - _t0
    _m, _sd = _samples.mean(), _samples.std(ddof=1)
    _dR = _sd / abs(_I)
    _results.append((_tau, _slope, _dwell, _m, _sd, _dR))
    print(f"{_tau:>8.3g} {_slope:>6d} {_dwell:>10.2f} {_m:>13.5e} {_sd:>12.3e} "
          f"{_dR:>12.4g} {_sd/abs(_m):>9.2%} {_span:>9.1f}")

# ---------- Part 3: in-situ settling after a real gate step ----------
print()
print("=== Part 3: in-situ settling, V_tg 0 -> +0.050 V (tau=0.3 s, 24 dB/oct) ===")
sr1.time_constant(0.3)
sr1.filter_slope(24)
interruptible_sleep(3.0)
_itg0, _ibg0 = k_2400_tg.curr(), k_2400_bg.curr()
_base = np.mean([sr1.X() for _ in range(4)])
print(f"before step: X={_base:.5e} V, I_tg={_itg0:.3e} A, I_bg={_ibg0:.3e} A")

_STEP_V, _DT, _T_END = 0.050, 0.10, 6.0
_t0 = time.time()
k_2400_tg.volt(_STEP_V)
_trace = []
while time.time() - _t0 < _T_END:
    _trace.append((time.time() - _t0, sr1.X()))
    time.sleep(_DT)
_trace = np.array(_trace)
_final = _trace[-8:, 1].mean()
print(f"after step:  X_final={_final:.5e} V  (delta = {_final - _base:+.3e} V, "
      f"dR_xx = {(_final - _base)/_I:+.4g} ohm)")

# settling time: first crossing after which |X - X_final| stays within tolerances
_amp = abs(_final - _base)
print()
print(f"{'tol':>8} {'t_settle (s)':>13}")
for _tol in (0.10, 0.05, 0.02, 0.01):
    if _amp <= 0:
        break
    _bad = np.where(np.abs(_trace[:, 1] - _final) > _tol * _amp)[0]
    _ts = _trace[_bad[-1] + 1, 0] if len(_bad) and _bad[-1] + 1 < len(_trace) else 0.0
    print(f"{_tol:>8.0%} {_ts:>13.2f}")
print()
print("trace (t s, X V, R_xx ohm) every 0.5 s:")
for _t, _x in _trace[::5]:
    print(f"   {_t:5.2f}  {_x:.5e}  {_x/_I:9.2f}")

k_2400_tg.volt(0.0)
interruptible_sleep(3.0)
_itg1, _ibg1 = k_2400_tg.curr(), k_2400_bg.curr()
print()
print(f"returned V_tg -> {k_2400_tg.volt():+.4f} V; X={sr1.X():.5e} V "
      f"(was {_base:.5e}); I_tg={_itg1:.3e} A, I_bg={_ibg1:.3e} A")
assert abs(_itg1) < 1e-9 and abs(_ibg1) < 1e-9, "gate current above 1 nA - stop and investigate"

# restore
sr1.time_constant(_TAU0)
sr1.filter_slope(_SLOPE0)
print(f"restored sr1 tau={sr1.time_constant()} s, slope={sr1.filter_slope()} dB/oct")

# ---------- pricing ----------
print()
print("=== pricing (dwell from Part 3 overrides k*tau where they disagree) ===")
_OVERHEAD = 0.25
print(f"{'tau (s)':>8} {'slope':>6} {'s/pt':>7} {'151pt leg':>10} {'4-leg gateC':>12} "
      f"{'101x101':>9} {'dR_xx (ohm)':>12}")
for _tau, _slope, _dwell, _m, _sd, _dR in _results:
    _spp = _dwell + _OVERHEAD
    print(f"{_tau:>8.3g} {_slope:>6d} {_spp:>7.2f} {_spp*151/60:>9.1f}m "
          f"{_spp*151*4/60:>11.1f}m {_spp*101*101/3600:>8.2f}h {_dR:>12.4g}")
print()
print("SETTLE-V2: done")
