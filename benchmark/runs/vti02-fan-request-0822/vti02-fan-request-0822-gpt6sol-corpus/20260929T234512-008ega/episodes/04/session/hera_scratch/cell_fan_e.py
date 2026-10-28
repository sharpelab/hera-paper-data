# Electron-side D=0 SdH fan, landau-fan-vti, run-5 calibration and run-6 timing.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
import numpy as np

CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
ns = np.linspace(3.2, 2.4, 25)             # 1e12 cm^-2; high to low each row
Ds = np.zeros_like(ns)                      # V/nm
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
B_vec = 1.0 / np.linspace(1.0, 0.1, 91)  # uniform 1/B, 1 -> 10 T
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX)) and np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert max(B_vec) <= B_SESSION_CAP and min(B_vec) > 0
_ncheck, _Dcheck = calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
assert np.max(np.abs(_ncheck-ns)) < 1e-9 and np.max(np.abs(_Dcheck)) < 1e-9
print(f'fan grid: {len(B_vec)} B x {len(ns)} n = {len(B_vec)*len(ns)} pts; B {B_vec[0]:.3f}->{B_vec[-1]:.3f} T, n {ns[0]:.3f}->{ns[-1]:.3f}e12; '
      f'TG {min(Vtgs):.4f}..{max(Vtgs):.4f} V, BG {min(Vbgs):.4f}..{max(Vbgs):.4f} V')

# Silent-state preconditions: no gate or field motion before all pass.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T0, _Tv0, _B0, _Si0 = T_sample(), T_vaporizer(), magnet.field(), k_si()
_sample_range, _vaporizer_range = heater.sample_range(), heater.vaporizer_range()
_ps, _output = magnet.persistent_switch_on(), magnet.output_enabled()
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f'precondition: T_sample {_T0:.3f} K [1.0,1.5], T_vaporizer {_Tv0:.3f} K [0.7,1.5], '
      f'B {_B0:+.4f} T [|B|<0.05], Si {_Si0:+.3f} V [0], heaters {_sample_range}/{_vaporizer_range} [0/0], '
      f'PS/output {_ps}/{_output} [True/True], sr1 tau/slope {_tau}s/{_slope}dB [0.3/24]')
print(f'validators: TG {k_tg.volt.vals}, BG {k_bg.volt.vals}, Si {dc205.smart_voltage.vals}, '
      f'B {magnet.field.vals}, T {heater.sample_setpoint.vals}/{heater.vaporizer_setpoint.vals}')
assert 1.0 <= _T0 <= 1.5 and 0.7 <= _Tv0 <= 1.5 and abs(_B0) < 0.05 and abs(_Si0) < 0.01
assert _sample_range == 0 and _vaporizer_range == 0 and _ps and _output
assert abs(_tau-0.3) < 1e-9 and _slope == 24
assert (k_tg.volt.vals.min_value, k_tg.volt.vals.max_value) == (-0.3, 1.0)
assert (k_bg.volt.vals.min_value, k_bg.volt.vals.max_value) == (-1.3, 2.0)
assert (dc205.smart_voltage.vals.min_value, dc205.smart_voltage.vals.max_value) == (-25.0, 25.0)
assert (magnet.field.vals.min_value, magnet.field.vals.max_value) == (-10.0, 10.0)
assert heater.sample_setpoint.vals.max_value == 100.0 and heater.vaporizer_setpoint.vals.max_value == 100.0

sr1.sensitivity(50e-6)                   # 5 kOhm full-scale at 10 nA, inherited from spot checks
print(f'sr1 sensitivity = {sr1.sensitivity():.1e} V; drive = {sr1.amplitude():.3f} V')
assert abs(sr1.amplitude()-1.0) < 0.01
mc = dict(meas_config)
mc['Si (V)'] = _Si0
mc['sample_temperature:'] = _T0
mc['comments'] = ('landau-fan-vti electron: D=0 V/nm, n=+3.2..+2.4e12 cm^-2, '
                  'B=1..10 T uniform 1/B (91 rows), 25 n points, 3s fast delay, sr1 50uV; run-5 calibration')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('electron side; D=0 V/nm; n=+3.2 to +2.4e12 cm^-2 (25 pts); '
              'B=1 to 10 T (91 rows uniform 1/B); run-5 cal c_bg/c_tg=0.773, '
              'n_offset=-0.0894e12, D_offset=-0.013 V/nm; sr1=50uV, fast_delay=3s')
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr0.X); s.plot('time', sr0.P)
s.plot('time', sr1.X); s.plot('time', sr1.P)

def fan_leak_guard(station, data):
    # Columns: time, B, Vtg, Vbg, T, Itg, Ibg, sr0X/P, sr1X/P.
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > 1e-9 or i_bg > 1e-9:
        print(f'LEAK TRIP B={float(data[1]):.3f} T, n-axis Vtg={float(data[2]):.4f} V: '
              f'|Itg|={i_tg:.3e} A, |Ibg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

# FastBi field(target) blocks through its ramp and 3 s settle; do not interrupt mid-ramp to stop the supply.
magnet.field(float(B_vec[0]))
print(f'positioned at B={magnet.field():.4f} T; starting fan')
s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=0, fast_delay=3.0)
print(f'fan complete: measured B={magnet.field():.4f} T, TG={k_tg.volt():.4f} V, BG={k_bg.volt():.4f} V')
