# Plan step 4 — D≈0 density-field Landau fan across both CNP ridges.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Card bounds are immutable this session; VERIFY cell 32 printed ALL GREEN in this kernel.
_bounds = lambda p: (float(p.vals._min_value), float(p.vals._max_value))
assert _bounds(k_tg.volt) == (-0.3, 1.0) and _bounds(k_bg.volt) == (-1.3, 2.0)
assert _bounds(dc205.smart_voltage) == (-25.0, 25.0) and _bounds(dc205.voltage) == (-25.0, 25.0)
assert _bounds(magnet.field) == (-10.0, 10.0) and B_SESSION_CAP == 10.0
assert _bounds(heater.sample_setpoint) == (0.0, 100.0) and _bounds(heater.vaporizer_setpoint) == (0.0, 100.0)

# Silent preconditions: these are inherited, not changed by this cell.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Vsi, _sirange, _siout = k_si(), dc205.voltage_range(), dc205.output()
_hout = (heater.sample_range(), heater.vaporizer_range())
_drive, _freq = sr1.amplitude(), sr1.frequency()
print(f'preflight: T_sample={_T:.3f} K, T_vaporizer={_Tv:.3f} K, B={_B:+.4f} T; '
      f'Si={_Vsi:+.3f} V/range={_sirange}/out={_siout}; heater ranges={_hout}; '
      f'PS={magnet.persistent_switch_on()}, magnet output={magnet.output_enabled()}; '
      f'drive={_drive:.3f} V at {_freq:.3f} Hz; gates={k_tg.volt():+.4f}/{k_bg.volt():+.4f} V')
assert 1.0 <= _T <= 1.5 and _Tv < 1.6 and abs(_Tv - _T) < 0.6
assert abs(_B) < 0.02 and abs(_Vsi) < 0.01 and _sirange == 2 and _siout == 1
assert _hout == (0, 0) and magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(_drive - 1.0) < 0.01 and abs(_freq - 13.777) < 0.01
assert sr0.filter_slope() == 24 and sr1.filter_slope() == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

CAL_FAN = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137, D_offset=-0.013)
n_fast = np.linspace(-1.2, 3.2, 111)  # 1e12 cm^-2, region A; includes region-B CNP at n_A=-0.426
D_fast = np.zeros_like(n_fast)          # V/nm, data/5 D-offset convention
Vtg_fast, Vbg_fast = calc_gate_voltages(n_fast, D_fast, **CAL_FAN)
B_slow = np.round(np.linspace(0.0, 9.9, 100), 4)
assert len(B_slow) * len(n_fast) == 11100 and B_slow.max() < B_SESSION_CAP
assert np.min(Vtg_fast) >= TG_MIN and np.max(Vtg_fast) <= TG_MAX
assert np.min(Vbg_fast) >= BG_MIN and np.max(Vbg_fast) <= BG_MAX
_ncheck, _Dcheck = calc_nD(Vtg_fast, Vbg_fast, **CAL_FAN)
assert np.allclose(_ncheck, n_fast) and np.max(np.abs(_Dcheck)) < 1e-9
print(f'grid: B {B_slow[0]:.1f}→{B_slow[-1]:.1f} T x n_A {n_fast[0]:+.2f}→{n_fast[-1]:+.2f}e12 '
      f'({len(B_slow)}x{len(n_fast)}); Vtg {Vtg_fast[0]:+.4f}→{Vtg_fast[-1]:+.4f} V; '
      f'Vbg {Vbg_fast[0]:+.4f}→{Vbg_fast[-1]:+.4f} V; D=0')

# Fixed sensitivity and settled fast-axis cadence; no safety or gate-pacing change.
sr0.time_constant(0.1); sr1.time_constant(0.1)
sr1.sensitivity(1e-3)  # 100 kOhm nominal full-scale at 10 nA; abort above 90%.
print(f'lock-in: sr0/sr1 tau={sr0.time_constant()}/{sr1.time_constant()} s, '
      f'sr1 sens={sr1.sensitivity():g} V, sr0 sens={sr0.sensitivity():g} V')

mc = dict(meas_config)
mc['Si (V)'] = _Vsi
mc['sample_temperature:'] = _T
mc['comments'] = ('landau-fan: D=0 from data/5; n_A -1.2..+3.2e12 cm^-2 x111; '
                  'B 0..+9.9 T x100; Vtg/Vbg co-swept; sr1 1mV, tau 0.1s, fast_delay 1s')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('B slow 0..+9.9 T (100 x 0.1 T); n_A fast -1.2..+3.2e12 cm^-2 '
              '(111 x 0.04e12), D=0 via data/5 calibration; Si=0; sr1 sensitivity 1mV; '
              'sr0/sr1 tau 0.1s; 1s fast dwell; hardwired B_1-B_2; two CNP origins n_A=0,-0.426e12')
s.ramp(k_bg.volt, Vbg_fast[0]); s.ramp(k_tg.volt, Vtg_fast[0])
interruptible_sleep(10)

# multimegasweep rows: time, B, Vtg, Vbg, T, I_tg, I_bg, sr0_X, sr0_P, sr1_X, sr1_P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _channel in (T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P):
    s.plot('time', _channel)

def fan_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    x1, t = abs(float(data[9])), float(data[4])
    if i_tg > 1e-9 or i_bg > 1e-9 or x1 > 0.9e-3 or not (1.0 <= t <= 1.6):
        print(f'FAN STOP B={float(data[1]):.2f} T, Vtg={float(data[2]):+.3f} V: '
              f'|I_tg/bg|={i_tg:.2e}/{i_bg:.2e} A, |sr1_X|={x1*1e6:.1f} uV, T={t:.3f} K')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_slow], [k_tg.volt, k_bg.volt],
                 [Vtg_fast, Vbg_fast], slow_delay=0, fast_delay=1.0)
print(f'fan ended: measured B={magnet.field():+.4f} T; gates '
      f'Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f}, Si={k_si():+.4f} V; '
      f'T_sample={T_sample():.3f} K')
