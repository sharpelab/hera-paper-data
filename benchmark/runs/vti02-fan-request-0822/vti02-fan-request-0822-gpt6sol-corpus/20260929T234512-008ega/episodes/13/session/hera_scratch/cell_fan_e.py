# Electron-side FS-count fan; VTI variant of landau-fan, run-5 calibration.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
import numpy as np

# Preconditions: states this cell inherits rather than sets.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Vsi, _Vtg0, _Vbg0 = k_si(), k_tg.volt(), k_bg.volt()
print(f'precondition T_sample={_Ts:.3f} K (1.0-1.5), T_vaporizer={_Tv:.3f} K (<1.6); '
      f'B={_B:+.4f} T (near 0), Si={_Vsi:+.4f} V (0), TG={_Vtg0:+.4f} V (0), BG={_Vbg0:+.4f} V (0)')
print(f'precondition heater ranges={heater.sample_range()},{heater.vaporizer_range()} (0,0); '
      f'PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, '
      f'drive={sr1.amplitude():.4f} V at {sr1.frequency():.3f} Hz, '
      f'tau={sr1.time_constant()} s, slope={sr1.filter_slope()}, field settle={magnet.settle_s} s')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_Tv - _Ts) < .6
assert abs(_B) < .05 and abs(_Vsi) < .01 and abs(_Vtg0) < .01 and abs(_Vbg0) < .01
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert .95 <= sr1.amplitude() <= 1.05 and abs(sr1.frequency()-13.777) < .01
assert sr1.time_constant() <= .3 and magnet.settle_s >= 3
assert (k_2400_tg.volt.vals._min_value, k_2400_tg.volt.vals._max_value) == (-.3, 1.0)
assert (k_2400_bg.volt.vals._min_value, k_2400_bg.volt.vals._max_value) == (-1.3, 2.0)
assert (magnet.field.vals._min_value, magnet.field.vals._max_value) == (-10.0, 10.0)
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert WIRING['sr1+'] == 'B_1' and WIRING['sr1-'] == 'B_2'

# Run-5 ridge-A (n,D) calibration: ratio data-calibrated; absolute scale geometry prior.
CAL_FAN = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-.0894, D_offset=-.013)
ns = np.linspace(3.20, 2.50, 23)  # 1e12 cm^-2, high -> low; last point is next-step-friendly
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL_FAN['c_tg'], CAL_FAN['c_bg'], CAL_FAN['n_offset'], CAL_FAN['D_offset'])
Vtgs, Vbgs = np.asarray(Vtgs), np.asarray(Vbgs)
assert len(ns) == len(Vtgs) == len(Vbgs) == 23
assert np.all((Vtgs >= TG_MIN) & (Vtgs <= TG_MAX)) and np.all((Vbgs >= BG_MIN) & (Vbgs <= BG_MAX))
n_check, D_check = calc_nD(Vtgs, Vbgs, CAL_FAN['c_tg'], CAL_FAN['c_bg'], CAL_FAN['n_offset'], CAL_FAN['D_offset'])
assert np.max(np.abs(np.asarray(n_check)-ns)) < 1e-9 and np.max(np.abs(D_check)) < 1e-9
B_vec = 1.0 / np.linspace(1/.75, 1/10.0, 140)
assert B_vec[0] >= 0 and B_vec[-1] <= B_SESSION_CAP and np.all(np.diff(B_vec) > 0)
assert np.max(np.abs(np.diff(1/B_vec))) <= 1/(3*37.5)
print(f'fan: {len(B_vec)} B rows {B_vec[0]:.3f}->{B_vec[-1]:.3f} T, {len(ns)} n points {ns[0]:.3f}->{ns[-1]:.3f}e12; '
      f'Δ(1/B)={abs(np.diff(1/B_vec)[0]):.5f} T^-1, Δn={abs(np.diff(ns)[0]):.4f}e12')
print(f'gate endpoints: high n ({Vtgs[0]:+.4f},{Vbgs[0]:+.4f}) V, low n ({Vtgs[-1]:+.4f},{Vbgs[-1]:+.4f}) V')

# Fixed sensitivity across all columns; no autoranging during the fan.
sr1.sensitivity(50e-6)
assert abs(sr1.sensitivity()-50e-6) < 1e-9
I_TRIP = 1e-9
R_FS = sr1.sensitivity() / (sr1.amplitude()/100e6)
print(f'sr1 sensitivity={sr1.sensitivity()*1e6:.1f} µV; full-scale R≈{R_FS:.0f} Ω')

# Set the fast-axis starting point, check leakage there, then position the blocking magnet.
s = sweep.AsyncStation(dict(meas_config, **{'Si (V)': _Vsi, 'sample_temperature:': _Ts,
    'comments': 'landau-fan-vti electron D=0, n=+3.20 to +2.50e12, B=0.75 to 10 T, run-5 cal, 140x23'}))
s.add_comment('landau-fan-vti')
s.add_comment('electron B_1-B_2: D=0 V/nm; n=+3.20 to +2.50e12 cm^-2; B=0.75 to 10 T, uniform 1/B 140 rows x 23 n; '
              'TG/BG paired, Si=0 V; run-5 ridge-A cal c_bg/c_tg=0.773, n_offset=-0.0894e12, D_offset=-0.013 V/nm; sr1 50uV, fast_delay=2.4s')
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)
_I_tg0, _I_bg0 = k_tg.curr(), k_bg.curr()
print(f'initial gate currents TG={_I_tg0*1e12:+.1f} pA, BG={_I_bg0*1e12:+.1f} pA (<1000 pA)')
assert abs(_I_tg0) < I_TRIP and abs(_I_bg0) < I_TRIP
s.ramp(magnet.field, float(B_vec[0]))  # blocking ramp: 0 -> 0.75 T (~5.5 min), includes driver settle
print(f'field positioned: measured {magnet.field():+.4f} T vs start {B_vec[0]:.4f} T')
assert abs(magnet.field()-B_vec[0]) < .02

# Data row: [time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P].
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_trip(station, data):
    itg, ibg, x1 = abs(float(data[5])), abs(float(data[6])), abs(float(data[9]))
    if itg > I_TRIP or ibg > I_TRIP or x1 >= .90*50e-6:
        print(f'FAN TRIP B={data[1]:.3f} T, Vtg={data[2]:+.4f} V: |I_tg|={itg*1e12:.0f} pA, '
              f'|I_bg|={ibg*1e12:.0f} pA, |sr1X|={x1*1e6:.1f} µV')
        station.interrupt_requested = True
s.register_run_after(fan_trip, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=1, fast_delay=2.4)
print(f'fan end: measured B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V; '
      f'T_sample={T_sample():.3f} K; interrupted={s.interrupt_requested}')
