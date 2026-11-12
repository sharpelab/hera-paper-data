# === landau-fan: region-A D=0 density line, B slow 1.5 -> 10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.2, 3.2, 111)  # units: 1e12 cm^-2
D_vec = np.zeros_like(n_vec)
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, D_vec, **CAL)
B_vec = np.r_[np.round(np.arange(1.5, 10.0, 0.2), 4), 10.0]
assert len(B_vec) == 44 and len(n_vec) == 111
assert np.all(np.diff(B_vec) > 0) and np.all(np.diff(n_vec) > 0)
assert np.min(Vtg_vec) >= TG_MIN and np.max(Vtg_vec) <= TG_MAX
assert np.min(Vbg_vec) >= BG_MIN and np.max(Vbg_vec) <= BG_MAX
assert np.max(np.abs(B_vec)) <= B_SESSION_CAP == 10.0
assert np.allclose(calc_nD(Vtg_vec, Vbg_vec, **CAL)[0], n_vec, atol=1e-3)
assert np.max(np.abs(calc_nD(Vtg_vec, Vbg_vec, **CAL)[1])) < 1e-3
print(f'grid: B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T ({len(B_vec)} rows); '
      f'n_A {n_vec[0]:+.2f}->{n_vec[-1]:+.2f}e12 ({len(n_vec)} points); '
      f'TG {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V; BG {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V')

# Load-bearing preconditions: these are inherited state, not set by the fan.
def _bounds(v): return (float(v._min_value), float(v._max_value))
assert _bounds(k_2400_tg.volt.vals) == (-0.3, 1.0)
assert _bounds(k_2400_bg.volt.vals) == (-1.3, 2.0)
assert _bounds(dc205.smart_voltage.vals) == _bounds(dc205.voltage.vals) == (-25.0, 25.0)
assert _bounds(magnet.field.vals) == (-10.0, 10.0)
assert _bounds(heater.sample_setpoint.vals) == _bounds(heater.vaporizer_setpoint.vals) == (0.0, 100.0)
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_hs, _hv = heater.sample_range(), heater.vaporizer_range()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
_drive, _freq = sr1.amplitude(), sr1.frequency()
print(f'precondition T_sample {_T:.3f} K [1.0,1.5], T_vaporizer {_Tv:.3f} K [<1.6]; '
      f'B {_B:+.4f} T [0±0.05], Si {_Si:+.4f} V [0±0.01]; '
      f'PS {_ps}, output {_out}, heater ranges {_hs}/{_hv} [0/0]')
print(f'lock-in drive {_drive:.3f} V at {_freq:.3f} Hz, tau {_tau:.3f} s, slope {_slope} dB/oct; '
      f'gate steps {k_tg.volt.step}/{k_bg.volt.step} V; Si rate {dc205.ramp_rate} V/s')
assert 1.0 <= _T <= 1.5 and _Tv < 1.6 and abs(_B) < 0.05 and abs(_Si) < 0.01
assert _ps and _out and _hs == _hv == 0
assert abs(_tau-0.3)<1e-6 and _slope == 24 and abs(_drive-1.0)<0.02 and abs(_freq-13.777)<0.01
assert k_tg.volt.step == k_bg.volt.step == 0.005 and abs(dc205.ramp_rate-0.5)<1e-9

sr1.sensitivity(200e-6)  # ~20 kOhm full scale at the 10 nA bias
print(f'sr1 sensitivity {sr1.sensitivity():.3g} V; I_bias {_drive/100e6*1e9:.2f} nA')
mc = dict(meas_config)
mc['Si (V)'] = _Si; mc['sample_temperature:'] = _T
mc['comments'] = (f'landau-fan: run-5 D_A=0 calibration, n_A -1.2..+3.2e12 x111, '
                  f'B 1.5..10 T x44, sr1 200uV, 2.1s fast delay')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('B slow 1.5..10 T, 0.2 T + terminal 10 T; n_A fast -1.2..+3.2e12 cm^-2, 0.04e12 spacing; '
              'D_A=0 V/nm, Si=0 V; run-5 calibration c_tg=2.796e-3 F/m2, c_bg=2.161e-3 F/m2, '
              'n_offset=-0.0894e12 cm^-2, D_offset=-0.013 V/nm; sr1 200uV, 2.1s fast dwell')
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# [time, B, Vtg, Vbg, T, Itg, Ibg, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot('time', T_sample)

def fan_guard(station, data):
    itg, ibg, vx = abs(float(data[5])), abs(float(data[6])), abs(float(data[9]))
    if itg > 1e-9 or ibg > 1e-9 or vx > 0.9*200e-6:
        print(f'FAN STOP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f} V: '
              f'|Itg|={itg:.3e} A, |Ibg|={ibg:.3e} A, |sr1.X|={vx:.3e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                     [Vtg_vec, Vbg_vec], slow_delay=0, fast_delay=2.1)
finally:
    # Zero the gates at committed 5 mV steps. The field is left at its actual
    # last point for the next data-guided step; read it rather than assume 10 T.
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'fan exit readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, '
          f'BG={k_bg.volt():+.4f} V, T_sample={T_sample():.3f} K')
