# Step 5: electron D=0 Landau fan, plan in hera_scratch/plan.md.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: state inherited from the handoff, not set by this sweep.
def _limits(p):
    return float(p.vals._min_value), float(p.vals._max_value)

assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_vtg0, _vbg0, _vsi0 = k_tg.volt(), k_bg.volt(), k_si()
print(f'precondition T_sample={_Ts:.3f} K (1.0–1.5), T_vaporizer={_Tv:.3f} K (<1.6), '
      f'B={_B:+.4f} T (zero ±0.05), TG={_vtg0:+.4f}, BG={_vbg0:+.4f}, Si={_vsi0:+.4f} V (zero)')
print(f'PS={magnet.persistent_switch_on()}, output={magnet.output_enabled()}, '
      f'ramping={magnet.is_ramping()}, heaters={heater.sample_range()}/{heater.vaporizer_range()}, '
      f'DC205 range/output={dc205.voltage_range()}/{dc205.output()}')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_Tv - _Ts) < 0.6
assert abs(_B) < 0.05 and not magnet.is_ramping()
assert abs(_vtg0) < 0.005 and abs(_vbg0) < 0.005 and abs(_vsi0) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert dc205.voltage_range() == 2 and dc205.output() == 1 and abs(dc205.ramp_rate - 0.5) < 1e-9
assert _limits(k_tg.volt) == (-0.3, 1.0) and _limits(k_bg.volt) == (-1.3, 2.0)
assert _limits(dc205.smart_voltage) == (-25.0, 25.0) and _limits(dc205.voltage) == (-25.0, 25.0)
assert _limits(magnet.field) == (-10.0, 10.0) and B_SESSION_CAP == 10.0
assert _limits(heater.sample_setpoint) == (0.0, 100.0) and _limits(heater.vaporizer_setpoint) == (0.0, 100.0)
assert k_tg.volt.step == 0.005 and k_bg.volt.step == 0.005
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
_amp, _freq, _tau, _slope = sr1.amplitude(), sr1.frequency(), sr1.time_constant(), sr1.filter_slope()
print(f'drive={_amp:.3f} V / 100 MΩ = {_amp/100e6*1e9:.3f} nA, f={_freq:.3f} Hz, '
      f'sr1 τ={_tau:.3f} s / slope={_slope} dB/oct; sr0 sens={sr0.sensitivity()} V')
assert abs(_amp - 1.0) < 0.01 and abs(_freq - 13.777) < 0.02
assert _tau == 0.3 and _slope == 24 and sr0.sensitivity() == 0.02
assert WIRING == {'source': 'T_0', 'drain': 'B_3', 'sr1+': 'B_1', 'sr1-': 'B_2',
                  'sr2+': 'n.c.', 'sr2-': 'n.c.', 'sr3+': 'n.c.', 'sr3-': 'n.c.'}

# Calibration: run 5 ridge slope and D vertex; absolute c_tg is the geometry prior.
_cal = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
            n_offset=-0.08937933224099137, D_offset=-0.013)
_n = np.round(np.arange(0.5, 3.2001, 0.05), 4)  # 1e12 cm^-2, region A
_D = np.zeros_like(_n)
_Vtg, _Vbg = calc_gate_voltages(_n, _D, **_cal)
_n_rt, _D_rt = calc_nD(_Vtg, _Vbg, **_cal)
_Bvec = np.round(np.arange(2.0, 10.0001, 0.2), 4)
assert len(_n) == 55 and len(_Bvec) == 41
assert np.allclose(_n_rt, _n, atol=1e-5) and np.allclose(_D_rt, 0, atol=1e-5)
assert _Vtg.min() >= -0.3 and _Vtg.max() <= 1.0 and _Vbg.min() >= -1.3 and _Vbg.max() <= 2.0
assert _Bvec.min() >= 0 and _Bvec.max() <= B_SESSION_CAP
_fast_delay = 3.0  # 10τ at 24 dB/oct; 3 s magnet settle is additional per B row
_I_trip, _fs_trip = 1e-9, 0.9e-3

sr1.sensitivity(1e-3)  # 100 kΩ nominal full scale at 10 nA
print(f'fan grid: B {_Bvec[0]:.1f}→{_Bvec[-1]:.1f} T ({len(_Bvec)} rows), '
      f'n {_n[0]:.2f}→{_n[-1]:.2f}e12 ({len(_n)} points), D=0; '
      f'TG {_Vtg[0]:+.4f}→{_Vtg[-1]:+.4f}, BG {_Vbg[0]:+.4f}→{_Vbg[-1]:+.4f} V')

_mc = dict(meas_config)
_mc['Si (V)'] = _vsi0
_mc['sample_temperature:'] = _Ts
_mc['comments'] = ('landau-fan electron D=0; run-5 ratio 0.773 and offsets; '
                   'n_A 0.50..3.20e12 step 0.05e12, B 2..10 T step 0.2 T; sr1 sens 1 mV')
s = sweep.AsyncStation(_mc)
s.add_comment('landau-fan')
s.add_comment('region A D=0; n_A +0.50..+3.20e12 cm^-2 step 0.05e12; '
              'B +2.0..+10.0 T step 0.2; TG/BG co-swept from run-5 calibration; '
              'Si=0; sr1 sens 1 mV; fast delay 3.0 s; hardwired B_1-B_2')

# Data row: time, B(set), Vtg(set), Vbg(set), T, I_tg, I_bg, sr0.X, sr1.X.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr1.X)
s.plot(magnet.field, T_sample)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_tg.volt, k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.X)

def fan_guard(station, data):
    _it, _ib, _v = abs(float(data[5])), abs(float(data[6])), abs(float(data[8]))
    if _it > _I_trip or _ib > _I_trip or _v > _fs_trip:
        print(f'FAN TRIP B={float(data[1]):+.3f} T, Vtg={float(data[2]):+.4f} V: '
              f'|I_tg|={_it:.3e}, |I_bg|={_ib:.3e} A, |sr1.X|={_v:.3e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.ramp(k_bg.volt, float(_Vbg[0])); s.ramp(k_tg.volt, float(_Vtg[0]))
    interruptible_sleep(10)
    _it0, _ib0 = k_tg.curr(), k_bg.curr()
    print(f'pre-ramp gate currents: TG={_it0*1e12:+.0f} pA, BG={_ib0*1e12:+.0f} pA; require <1 nA')
    assert abs(_it0) < _I_trip and abs(_ib0) < _I_trip
    print('field pre-ramp 0→2 T: ≈15 min at 0.137 T/min; magnet.field blocks')
    magnet.field(float(_Bvec[0]))
    _b2 = magnet.field()
    print(f'field at fan start: {_b2:+.4f} T (expect 2 ±0.02)')
    assert abs(_b2 - _Bvec[0]) < 0.02 and not magnet.is_ramping()
    s.multimegasweep([magnet.field], [_Bvec], [k_tg.volt, k_bg.volt],
                     [_Vtg, _Vbg], slow_delay=0.0, fast_delay=_fast_delay,
                     init_delay=False)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'fan exit readback: B={magnet.field():+.4f} T, '
          f'TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V, '
          f'T_sample={T_sample():.3f} K; verify ramp status before any next move')
