# === Fixed-D Landau fan (`landau-fan`): B slow 0.3→10 T, (TG,BG) fast n_A −1.15→+3.20e12, D_A=0 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: state inherited from the operator's post-handoff close_out, not set by this cell.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Vtg, _Vbg, _Vsi = k_tg.volt(), k_bg.volt(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_hs, _hv = heater.sample_range(), heater.vaporizer_range()
print(f'precondition T_sample={_T:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (<1.6), B={_B:+.4f} T (|B|<0.03)')
print(f'precondition TG={_Vtg:+.4f}, BG={_Vbg:+.4f}, Si={_Vsi:+.4f} V (all 0); PS={_ps}, output={_out} (both on); heater ranges={_hs},{_hv} (both off)')
assert 1.0 <= _T <= 1.5 and _Tv < 1.6 and abs(_Tv-_T) < 0.6 and abs(_B) < 0.03
assert max(abs(_Vtg), abs(_Vbg), abs(_Vsi)) < 0.01 and _ps and _out and _hs == 0 and _hv == 0
assert dc205.voltage_range() == 2 and dc205.output() == 1 and abs(dc205.ramp_rate-0.5) < 1e-9
assert k_tg.volt.step == k_bg.volt.step == 0.005 and k_tg.nplci() == k_bg.nplci() == 1

# Recheck committed Gate-B fences numerically before any hardware move.
def _limits(p):
    return float(p.vals._min_value), float(p.vals._max_value)
assert _limits(k_tg.volt) == (-0.3, 1.0) and _limits(k_bg.volt) == (-1.3, 2.0)
assert _limits(dc205.smart_voltage) == _limits(dc205.voltage) == (-25.0, 25.0)
assert _limits(magnet.field) == (-10.0, 10.0) and B_SESSION_CAP == 10.0
assert _limits(heater.sample_setpoint) == _limits(heater.vaporizer_setpoint) == (0.0, 100.0) and T_SESSION_CAP == 100.0

_cal8 = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
             n_offset=-0.08937933224099137, D_offset=-0.013)
n8 = np.linspace(-1.15, 3.20, 88)  # 0.05 x10^12 cm^-2 per point, region A
D8 = np.zeros_like(n8)
Vtg8, Vbg8 = calc_gate_voltages(n8, D8, **_cal8)
B8 = np.linspace(0.3, 10.0, 50)  # ~0.198 T/row, increasing from 0 T handoff
assert Vtg8.min() >= TG_MIN and Vtg8.max() <= TG_MAX and Vbg8.min() >= BG_MIN and Vbg8.max() <= BG_MAX
assert 0 <= B8.min() and B8.max() <= B_SESSION_CAP
print(f'grid: {len(B8)} B rows {B8[0]:.3f}..{B8[-1]:.3f} T x {len(n8)} density points {n8[0]:+.2f}..{n8[-1]:+.2f}e12; '
      f'TG {Vtg8.min():+.4f}..{Vtg8.max():+.4f} V, BG {Vbg8.min():+.4f}..{Vbg8.max():+.4f} V')
print('n,D roundtrip endpoints:', calc_nD(Vtg8[[0,-1]], Vbg8[[0,-1]], **_cal8))

# Fixed sensitivity for CNP headroom. At 10 nA, 1 mV is ~100 kOhm full scale.
sr1.sensitivity(1e-3)
_tau0, _tau1 = sr0.time_constant(), sr1.time_constant()
FAST_DELAY = max(2.2, 7.5 * max(_tau0, _tau1))
print(f'drive={sr1.amplitude()} V, sr1 sensitivity={sr1.sensitivity()} V, tau sr0/sr1={_tau0}/{_tau1} s, '
      f'slopes={sr0.filter_slope()}/{sr1.filter_slope()}, fast_delay={FAST_DELAY:.2f} s')
assert sr1.amplitude() > 0 and sr1.amplitude() <= 1.0 and FAST_DELAY <= 3.0, 'lock-in dwell changed materially; reprice before running'
I_TRIP = 1e-9
V_RAIL = 0.95e-3
mc8 = dict(meas_config)
mc8['Si (V)'] = _Vsi
mc8['sample_temperature:'] = _T
mc8['comments'] = ('landau-fan: D_A=0, n_A=-1.15..+3.20e12 (88), B=0.3..10 T (50); '
                   'run-5 cal, Vsi=0, sr1 sens 1 mV, 2.2s fast dwell')
s = sweep.AsyncStation(mc8)
s.add_comment('landau-fan')
s.add_comment('fixed D_A=0 V/nm; n_A=-1.15..+3.20e12 cm^-2 (88 points); '
              'B=0.3..10 T increasing (50 rows); TG/BG co-swept; Vsi=0; run-5 calibration; '
              'sr1 sensitivity=1 mV; fast_delay>=2.2 s')
s.ramp(k_bg.volt, float(Vbg8[0])); s.ramp(k_tg.volt, float(Vtg8[0]))
interruptible_sleep(10)

# Row: [time, B, TG, BG, T, TG I, BG I, sr0 X/P, sr1 X/P].
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    # The two gate-current columns are positions 5 and 6, sr1 X is position 9.
    if abs(float(data[5])) > I_TRIP or abs(float(data[6])) > I_TRIP or abs(float(data[9])) > V_RAIL:
        print(f'FAN TRIP at B={float(data[1]):.3f} T, TG={float(data[2]):+.4f}, BG={float(data[3]):+.4f}: '
              f'I_TG={float(data[5]):+.3e} A, I_BG={float(data[6]):+.3e} A, sr1X={float(data[9]):+.3e} V')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B8], [k_tg.volt, k_bg.volt], [Vtg8, Vbg8],
                 slow_delay=0, fast_delay=FAST_DELAY)
print(f'fan stopped: measured B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V')
