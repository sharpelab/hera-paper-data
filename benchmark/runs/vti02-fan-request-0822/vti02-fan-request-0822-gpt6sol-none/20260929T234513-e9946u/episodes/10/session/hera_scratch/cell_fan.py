# === Step 4: calibrated D_A=0 Landau fan on hardwired B_1-B_2 Rxx ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Gate B: live committed validators must still match the device card exactly.
def _bounds(p):
    return (float(p.vals._min_value), float(p.vals._max_value))
_expected = [(-0.3, 1.0), (-1.3, 2.0), (-25.0, 25.0), (-25.0, 25.0),
             (-10.0, 10.0), (0.0, 100.0), (0.0, 100.0)]
_params = [k_tg.volt, k_bg.volt, dc205.smart_voltage, dc205.voltage,
           magnet.field, heater.sample_setpoint, heater.vaporizer_setpoint]
_actual = [_bounds(p) for p in _params]
print('SAFETIES validators: actual', _actual, 'expected', _expected)
assert _actual == _expected and B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0

# Preconditions the fan assumes: base thermometry, zero field/Si, heater off,
# energized magnet output, and the provided hardwired contact configuration.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B0, _Vsi = T_sample(), T_vaporizer(), magnet.field(), k_si()
_sr, _vr = heater.sample_range(), heater.vaporizer_range()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_amp, _freq = sr1.amplitude(), sr1.frequency()
print(f'preconditions: T_sample={_Ts:.3f} K [1.0,1.5], T_vap={_Tv:.3f} K [<1.6]; '
      f'B={_B0:+.4f} T [|B|<.02], Si={_Vsi:+.4f} V [0]; heaters={_sr}/{_vr} [0/0]; '
      f'PS/output={_ps}/{_out} [True/True]; drive={_amp:.3f} V at {_freq:.3f} Hz [1 V,13.777 Hz]')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_Tv - _Ts) < 0.6
assert abs(_B0) < 0.02 and abs(_Vsi) < 0.01 and _sr == _vr == 0
assert _ps and _out and abs(_amp - 1.0) < 0.01 and abs(_freq - 13.777) < 0.01
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert k_tg.volt.step == 0.005 and k_bg.volt.step == 0.005
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

# data/5 ridge-A ratio + offset; top-gate absolute capacitance from geometry.
FAN_CAL = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
n_vec = np.linspace(-1.2, 3.2, 111)  # units: 1e12 cm^-2
Vtg_vec, Vbg_vec = calc_gate_voltages(n_vec, np.zeros_like(n_vec), **FAN_CAL)
B_vec = np.r_[0.0, 0.5, 1.0, np.round(np.arange(1.1, 10.0001, 0.1), 3)]
assert len(B_vec) == 93 and len(Vtg_vec) == len(Vbg_vec) == 111
assert np.all((TG_MIN <= Vtg_vec) & (Vtg_vec <= TG_MAX))
assert np.all((BG_MIN <= Vbg_vec) & (Vbg_vec <= BG_MAX))
assert np.all((0 <= B_vec) & (B_vec <= B_SESSION_CAP))
_n_back, _D_back = calc_nD(Vtg_vec, Vbg_vec, **FAN_CAL)
assert np.max(np.abs(_n_back - n_vec)) < 1e-8 and np.max(np.abs(_D_back)) < 1e-8
print(f'fan vectors: B {B_vec[0]:.1f}..{B_vec[-1]:.1f} T x {len(B_vec)} rows; '
      f'n_A {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 x {len(n_vec)} pts, D_A=0; '
      f'TG {Vtg_vec.min():+.4f}..{Vtg_vec.max():+.4f} V, BG {Vbg_vec.min():+.4f}..{Vbg_vec.max():+.4f} V')

# Fixed acquisition settings: 1 s = 10 tau at 24 dB. The current channel has
# enough headroom at 20 mV; the voltage channel has 50 kOhm nominal headroom.
sr0.time_constant(0.1); sr1.time_constant(0.1)
sr1.sensitivity(500e-6)
_s1fs = sr1.sensitivity()
print(f'acquisition: sr0/sr1 tau {sr0.time_constant()}/{sr1.time_constant()} s, '
      f'slopes {sr0.filter_slope()}/{sr1.filter_slope()} dB/oct, sr1 FS {_s1fs*1e6:.0f} uV')
assert sr0.filter_slope() == sr1.filter_slope() == 24

mc = dict(meas_config)
mc['Si (V)'] = _Vsi; mc['sample_temperature:'] = _Ts
mc['comments'] = ('landau-fan: run-5 calibrated D_A=0; n_A -1.2..+3.2e12/0.04e12; '
                  'B 0,0.5,1.0,1.1..10.0/0.1 T; 1 s fast dwell; sr1 500 uV; Si 0')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('B slow 0,0.5,1.0,1.1..10.0 T (93 rows); n_A fast -1.2..+3.2e12 cm^-2 '
              '(111 pts, D_A=0, co-swept TG/BG); Si=0; T=base; region-A cal data/5: '
              'c_tg=2.796mF/m2, c_bg=2.161mF/m2, n_offset=-0.0894e12, D_offset=-0.013V/nm; '
              'sr1=500uV, tau=0.1s, fast_delay=1s; contacts T_0->B_3, Rxx B_1-B_2')

# Park the fast pair at the first density endpoint before the run starts.
s.ramp(k_bg.volt, float(Vbg_vec[0])); s.ramp(k_tg.volt, float(Vtg_vec[0]))
interruptible_sleep(10)

# Row: time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _y in [T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]:
    s.plot(k_tg.volt, _y)

def fan_guard(station, data):
    _it, _ib = abs(float(data[5])), abs(float(data[6]))
    _ix, _vx, _t = abs(float(data[7])), abs(float(data[9])), float(data[4])
    if _it > 1e-9 or _ib > 1e-9 or _ix < 1e-3 or _vx > 0.9*_s1fs or _t > 1.5:
        print(f'FAN GUARD TRIP B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f}, '
              f'Vbg={float(data[3]):+.4f}: I_tg={_it:.3e}, I_bg={_ib:.3e} A, '
              f'sr0.X={_ix:.3e} V, sr1.X/FS={_vx/_s1fs:.2f}, T={_t:.3f} K')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt],
                     [Vtg_vec, Vbg_vec], slow_delay=1.0, fast_delay=1.0)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'fan exit readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, '
          f'BG={k_bg.volt():+.4f} V, Si={k_si():+.4f} V, T={T_sample():.3f} K')
