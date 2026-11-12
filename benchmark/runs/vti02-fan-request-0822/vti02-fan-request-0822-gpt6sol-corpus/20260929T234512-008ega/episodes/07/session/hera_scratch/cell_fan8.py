# Step 4 — tetralayer FS-count electron fan, D=0; follows runs 5–7.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

# Gate B, machine/brief caps, and state assumed by this auto cell.
def _lims(p):
    return (float(p.vals._min_value), float(p.vals._max_value))
_card = {'tg': (-0.3, 1.0), 'bg': (-1.3, 2.0), 'si': (-25.0, 25.0),
         'B': (-10.0, 10.0), 'T': (0.0, 100.0)}
_actual = {'tg': _lims(k_tg.volt), 'bg': _lims(k_bg.volt),
           'si': _lims(dc205.smart_voltage), 'si_raw': _lims(dc205.voltage),
           'B': _lims(magnet.field), 'T': _lims(heater.sample_setpoint),
           'T_vap': _lims(heater.vaporizer_setpoint)}
print('validators expected:', _card, 'actual:', _actual)
assert all(_actual[k] == _card['si' if k == 'si_raw' else 'T' if k == 'T_vap' else k]
           for k in _actual)
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_sr, _vr = heater.sample_range(), heater.vaporizer_range()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_amp, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f'preconditions expected: T_sample 1.0–1.4 K, vaporizer <1.6 K and within 0.6 K, '
      f'B≈0 T, Si≈0 V, both heaters off, PS heater/output on, drive 1 V, tau 0.3 s/24 dB')
print(f'preconditions actual: T_sample={_Ts:.3f} K, T_vaporizer={_Tv:.3f} K, '
      f'B={_B:+.4f} T, Si={_Si:+.4f} V, heater ranges={_sr}/{_vr}, '
      f'PS/output={_ps}/{_out}, drive={_amp} V, tau/slope={_tau} s/{_slope} dB')
assert 1.0 <= _Ts <= 1.4 and _Tv < 1.6 and abs(_Tv - _Ts) < 0.6
assert abs(_B) < 0.05 and abs(_Si) < 0.01 and _sr == 0 and _vr == 0 and _ps and _out
assert abs(_amp - 1.0) < 0.01 and _tau == 0.3 and _slope == 24

# Calibration from run 5; scale is the geometry prior, ratio/offsets are session data.
CAL_FAN = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
               n_offset=-0.08937933224099137, D_offset=-0.013)
ns = np.linspace(3.2, 2.3, 33)  # n in 1e12 cm^-2; high-to-low fast axis.
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, **CAL_FAN)
assert np.all((Vtgs >= TG_MIN) & (Vtgs <= TG_MAX) & (Vbgs >= BG_MIN) & (Vbgs <= BG_MAX))
_ncheck, _Dcheck = calc_nD(Vtgs, Vbgs, **CAL_FAN)
assert np.max(np.abs(_ncheck - ns)) < 1e-9 and np.max(np.abs(_Dcheck)) < 1e-9
B_vec = field_invB(0.6, 10.0, 157)
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
print(f'grid: {len(B_vec)} B rows {B_vec[0]:.3f}→{B_vec[-1]:.3f} T; '
      f'{len(ns)} n points {ns[0]:.3f}→{ns[-1]:.3f}e12; '
      f'Vtg {Vtgs.min():+.4f}→{Vtgs.max():+.4f} V, Vbg {Vbgs.min():+.4f}→{Vbgs.max():+.4f} V')

# Fixed sensitivity clears the unmeasured low-n/high-B corner with headroom.
sr1.sensitivity(200e-6)
print(f'SR1 sensitivity={sr1.sensitivity()} V; full scale≈{sr1.sensitivity()/(_amp/100e6):.0f} Ohm')

mc = dict(meas_config)
mc['Si (V)'], mc['sample_temperature:'] = _Si, _Ts
mc['comments'] = ('landau-fan-vti electron: D=0 V/nm, n=+2.3..+3.2e12 cm^-2; '
                  'B=0.6..10 T rising, uniform 1/B, 157x33; run-5 cal; '
                  'sr1 200 uV, fast_delay 1.8 s, slow_delay 0 s')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('FS-count electron fan; run-5 calibration; D=0 V/nm; n=+2.3..+3.2e12 cm^-2; '
              'B=0.6..10 T rising uniform-1/B 157 rows x 33 n; '
              'Vtg=+0.7257..+0.9836 V, Vbg=+0.8326..+1.1663 V; '
              'SR1 200 uV, tau 0.3 s/24 dB, fast_delay 1.8 s; Si=0 V')

# Start at the present field. The blocking set includes the 0.6 T ramp and settle.
magnet.field(float(B_vec[0]))
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# 2D row layout: [time, B, Vtg, Vbg, T, Itg, Ibg, sr0.X, sr0.P, sr1.X, sr1.P].
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    if abs(float(data[5])) > 1e-9 or abs(float(data[6])) > 1e-9 or not 1.0 <= float(data[4]) <= 1.5:
        print(f'FAN TRIP B={float(data[1]):.3f} T: T={float(data[4]):.3f} K, '
              f'Itg={float(data[5]):+.3e} A, Ibg={float(data[6]):+.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=0, fast_delay=1.8)
print(f'fan done: B={magnet.field():+.4f} T, Vtg={k_tg.volt():+.4f} V, Vbg={k_bg.volt():+.4f} V')
