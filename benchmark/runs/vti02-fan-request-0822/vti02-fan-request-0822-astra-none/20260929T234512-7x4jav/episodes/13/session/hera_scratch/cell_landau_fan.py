# Plan step 4: Landau fan across both neutrality ridges, at estimated D=0.
# Read-only preflight first; no safety surface or ramp pacing is changed.
import numpy as np
from scipy.constants import e as _e, epsilon_0 as _eps0

for _par, _expected in [
    (k_tg.volt, (-0.3, 1.0)), (k_bg.volt, (-1.3, 2.0)),
    (dc205.smart_voltage, (-25.0, 25.0)), (dc205.voltage, (-25.0, 25.0)),
    (magnet.field, (-10.0, 10.0)),
    (heater.sample_setpoint, (0.0, 100.0)),
    (heater.vaporizer_setpoint, (0.0, 100.0)),
]:
    _actual = (float(_par.vals._min_value), float(_par.vals._max_value))
    print(f'{_par.full_name} validator: expected {_expected}, actual {_actual}')
    assert _actual == _expected, 'SAFETIES mismatch; stop without writes'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_fan_T, _fan_Tv, _fan_B = T_sample(), T_vaporizer(), magnet.field()
_fan_Si = k_si()
_fan_ranges = (heater.sample_range(), heater.vaporizer_range())
_fan_PS, _fan_out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'Expected base T=1.0..1.5 K, vaporizer<1.6 K within 0.6 K; actual {_fan_T:.3f}, {_fan_Tv:.3f}')
print(f'Expected |B|<0.02 T, Si=0 V, heaters off, PS/output on; actual B={_fan_B:.5f}, Si={_fan_Si:.4f}, ranges={_fan_ranges}, PS/output={_fan_PS}/{_fan_out}')
print(f'Gate start readbacks TG={k_tg.volt():.4f}, BG={k_bg.volt():.4f} V; both will be set to fan start')
assert 1.0 <= _fan_T <= 1.5 and 0 < _fan_Tv < 1.6 and abs(_fan_Tv-_fan_T) < 0.6
assert abs(_fan_B) < 0.02 and abs(_fan_Si) < 0.01 and _fan_ranges == (0, 0)
assert _fan_PS and _fan_out
assert dc205.voltage_range() == 2 and dc205.output() == 1 and dc205.ramp_rate == 0.5
_fan_steps = (k_tg.volt.step, k_bg.volt.step)
_fan_nplc = (k_tg.nplci(), k_bg.nplci())
_fan_tau = (sr0.time_constant(), sr1.time_constant())
_fan_slope = (sr0.filter_slope(), sr1.filter_slope())
_fan_amp, _fan_freq = sr1.amplitude(), sr1.frequency()
print(f'Expected steps=(0.005,0.005), NPLC=(1,1), tau=(0.3,0.3), slope=(24,24); actual {_fan_steps}, {_fan_nplc}, {_fan_tau}, {_fan_slope}')
print(f'Expected drive=1 V/13.777 Hz, sr0 sensitivity=0.02 V; actual {_fan_amp}/{_fan_freq}, {sr0.sensitivity()}')
assert _fan_steps == (0.005, 0.005) and _fan_nplc == (1, 1)
assert _fan_tau == (0.3, 0.3) and _fan_slope == (24, 24)
assert abs(_fan_amp-1.0) < 1e-6 and abs(_fan_freq-13.777) < 0.01
assert sr0.sensitivity() == 0.02
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain'] == -1e6 and meas_config['bias_channel'] == 'sr1' and meas_config['bias_resistor'] == 100e6

# Run-5 calibration: SI internally, n labels below in 1e12 cm^-2.
_fan_cal = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
                n_offset_m2=-0.08937933224099137e16, D_offset_Vm=-0.013e9,
                provenance='run 5; relative ratio fitted, absolute c_tg geometry prior, D zero estimated')
_fan_n = np.linspace(-1.2, 3.2, 177)
_fan_D = 0.0
_fan_charge = _e * (_fan_n*1e16 - _fan_cal['n_offset_m2'])
_fan_delta = 2*_eps0*(_fan_D - _fan_cal['D_offset_Vm'])
_fan_tg = (_fan_charge + _fan_delta)/(2*_fan_cal['c_tg'])
_fan_bg = (_fan_charge - _fan_delta)/(2*_fan_cal['c_bg'])
_fan_fields = np.concatenate(([0.0, 0.5, 0.75], np.linspace(1, 3, 17), np.linspace(3.25, 10, 28)))
assert len(_fan_fields) == 48 and len(_fan_tg) == 177
assert np.all(np.diff(_fan_fields) > 0)
for _par, _values in [(k_tg.volt, _fan_tg), (k_bg.volt, _fan_bg), (magnet.field, _fan_fields)]:
    for _v in _values: _par.validate(float(_v))
print(f'Fan: {len(_fan_fields)} x {len(_fan_n)} points; TG {_fan_tg[0]:+.6f}..{_fan_tg[-1]:+.6f} V; BG {_fan_bg[0]:+.6f}..{_fan_bg[-1]:+.6f} V; B 0..10 T')

# Only acquisition sensitivity changes; restored handoff value 2 uV would rail.
sr1.sensitivity(100e-6)
assert sr1.sensitivity() == 100e-6
_fan_mc = dict(meas_config)
_fan_mc.update({'Si (V)': _fan_Si, 'sample_temperature:': _fan_T,
                'sr1_gain': 1.0, 'sr0_sensitivity': sr0.sensitivity(),
                'sr1_sensitivity': sr1.sensitivity(), 'bias_voltage': _fan_amp,
                'fan_calibration': _fan_cal, 'nominal_density_1e12_cm2': _fan_n.tolist(),
                'estimated_D_Vnm': 0.0, 'settle_s_per_gate_point': 3.0,
                'comments': 'B_1-B_2, both carrier signs, estimated D=0, run-5 calibration; absolute density provisional'})
s = sweep.AsyncStation(_fan_mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B 0,0.5,0.75,1..3 by 0.125,3.25..10 by 0.25 T; nominal n_A -1.2..3.2e12 cm^-2 by 0.025e12; D_est=0; Si=0 V; TG/BG co-swept; 3 s dwell; sr1 100 uV; tau 0.3 s/24 dB; source T_0, drain B_3, voltage B_1-B_2')
# Ramp at the committed Keithley pacing. No field pre-ramp or return traversal.
s.ramp(k_bg.volt, float(_fan_bg[0])); s.ramp(k_tg.volt, float(_fan_tg[0]))
interruptible_sleep(10)
# Data: time,Bset,TGset,BGset,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P,Bactual.
_fan_follow = [T_sample, T_vaporizer, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P, magnet.field]
for _p in _fan_follow:
    s.fp(_p)
    s.plot('time', _p)
_fan_point_count = 0
_fan_stop_reasons = []

def _fan_guard(station, data):
    global _fan_point_count
    _fan_point_count += 1
    d = np.asarray(data, dtype=float)
    why = []
    if not np.isfinite(d).all(): why.append('nonfinite reading')
    if max(abs(d[6]), abs(d[7])) > 1e-9: why.append('gate current exceeds 1 nA')
    if not 1.0 <= d[4] <= 1.5: why.append('sample T outside base window')
    if not 0 < d[5] < 1.6 or abs(d[5]-d[4]) >= 0.6: why.append('vaporizer departs base')
    if abs(d[12]-d[1]) > 0.02: why.append('field readback differs >20 mT')
    if abs(d[8]) >= 0.9*0.02 or abs(d[10]) >= 0.9*100e-6: why.append('lock-in headroom below 10 percent')
    _idrain = d[8] / _fan_mc['sr0_gain']
    if not 5e-9 < _idrain < 12e-9: why.append('drain current outside 5..12 nA')
    if _fan_point_count % len(_fan_n) == 0:
        try:
            assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
            assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
        except Exception as exc:
            why.append(f'thermometry freshness: {exc}')
        print(f'FAN ROW {_fan_point_count//len(_fan_n)}/48 complete, B={d[12]:.4f} T, T={d[4]:.3f} K', flush=True)
    if why:
        _fan_stop_reasons.extend(why)
        print(f'FAN STOP at point {_fan_point_count}: {why}; data={d.tolist()}', flush=True)
        station.interrupt_requested = True

s.register_run_after(_fan_guard, ())
_fan_result = s.multimegasweep([magnet.field], [_fan_fields],
                              [k_tg.volt, k_bg.volt], [_fan_tg, _fan_bg],
                              slow_delay=3.0, fast_delay=3.0)
print(f'FAN END: run {_fan_result.id}; interrupted={_fan_result.metadata.get("interrupted")}; reasons={_fan_stop_reasons}')
print(f'ACTUAL STATE: B={magnet.field():.5f} T, TG={k_tg.volt():.6f} V, BG={k_bg.volt():.6f} V, Si={k_si():.4f} V, Ts={T_sample():.3f} K, Tv={T_vaporizer():.3f} K')
# Hold final state for review; no automatic extra traverse or close-out.
