# Plan step 4: landau-fan; base T, empirical D=0, Si=0; one upward traverse.
# Read-only preconditions precede every hardware write.
import json
from pathlib import Path
from scipy.constants import e, epsilon_0

for _p, _expected in [
    (k_tg.volt, (-0.3, 1.0)), (k_bg.volt, (-1.3, 2.0)),
    (dc205.smart_voltage, (-25.0, 25.0)), (dc205.voltage, (-25.0, 25.0)),
    (magnet.field, (-10.0, 10.0)),
    (heater.sample_setpoint, (0.0, 100.0)),
    (heater.vaporizer_setpoint, (0.0, 100.0))]:
    _actual = (float(_p.vals._min_value), float(_p.vals._max_value))
    print(f'validator {_p.full_name}: expected {_expected}, actual {_actual}')
    assert _actual == _expected, 'SAFETIES differs from card; stop'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Vt, _Vb, _Vsi = k_tg.volt(), k_bg.volt(), k_si()
_ranges = (heater.sample_range(), heater.vaporizer_range())
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'expected base Ts 1.0-1.5 K, Tv <1.6 K / within 0.6 K; actual {_Ts}, {_Tv}')
print(f'expected handoff |B|<0.02 T, gates 0 V; actual B={_B}, TG={_Vt}, BG={_Vb}, Si={_Vsi}')
print(f'expected heater ranges (0,0), PS/output True/True; actual {_ranges}, {_ps}/{_out}')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts) < .6
assert abs(_B) < .02 and abs(_Vt) < .001 and abs(_Vb) < .001 and abs(_Vsi) < .01
assert _ranges == (0,0) and _ps and _out
_rng, _dc_out = dc205.voltage_range(), dc205.output()
print(f'expected DC205 range/output 2/1, ramp_rate .5 V/s; actual {_rng}/{_dc_out}, {dc205.ramp_rate}')
assert _rng == 2 and _dc_out == 1 and dc205.ramp_rate == .5
print(f'expected TG/BG steps .005 V and NPLC 1; actual {k_tg.volt.step}/{k_bg.volt.step}, {k_tg.nplci()}/{k_bg.nplci()}')
assert k_tg.volt.step == .005 and k_bg.volt.step == .005
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
_card_wiring = {'source':'T_0', 'drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('expected hardwired B_1-B_2, actual', WIRING)
assert WIRING == _card_wiring and 'mux' not in globals()
assert meas_config['sr0_gain'] == -1e6 and meas_config.get('sr1_gain',1) == 1
assert meas_config['bias_resistor'] == 100e6 and meas_config['bias_channel'] == 'sr1'
_amp, _freq = sr1.amplitude(), sr1.frequency()
print(f'expected drive 1 V / 13.777 Hz; actual {_amp} / {_freq}')
assert abs(_amp-1.0) < 1e-6 and abs(_freq-13.777) < .01
for _sr in (sr0, sr1):
    _tau, _slope = _sr.time_constant(), _sr.filter_slope()
    print(f'{_sr.name}: expected tau .3 s / slope 24; actual {_tau} / {_slope}')
    assert _tau == .3 and _slope == 24
print('expected sr0 sensitivity .02 V; actual', sr0.sensitivity())
assert sr0.sensitivity() == .02

# Exact run-5 fit; density in 1e12 cm^-2, D in V/nm, SI capacitance.
fan_cal = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137, D_offset=-0.013)
fan_n = np.linspace(-1.2, 3.2, 111)
fan_charge = e * (fan_n - fan_cal['n_offset']) * 1e16
fan_diff = 2 * epsilon_0 * (0.0 - fan_cal['D_offset']) * 1e9
fan_vtg = (fan_charge + fan_diff) / (2*fan_cal['c_tg'])
fan_vbg = (fan_charge - fan_diff) / (2*fan_cal['c_bg'])
fan_B = np.r_[0.0, np.round(np.arange(.5, 1.41, .1), 8), field_invB(1.5, 10., 85)]
assert len(fan_B) == 96 and np.all(np.diff(fan_B)>0)
for _p, _vec in ((k_tg.volt,fan_vtg), (k_bg.volt,fan_vbg), (magnet.field,fan_B)):
    for _v in _vec: _p.validate(float(_v))
print(f'planned {len(fan_B)} x {len(fan_n)} points; TG {fan_vtg.min():+.6f}..{fan_vtg.max():+.6f} V; BG {fan_vbg.min():+.6f}..{fan_vbg.max():+.6f} V')

# Only acquisition-range change: no gate/field/T validators or pacing edits.
sr1.sensitivity(100e-6)
assert sr1.sensitivity() == 100e-6
mc = dict(meas_config)
mc.update({'sr1_gain':1.0, 'Si (V)':_Vsi, 'sample_temperature:':_Ts,
           'gate_calibration':fan_cal, 'density_units':'1e12 cm^-2; absolute scale provisional',
           'D_target_V_per_nm':0.0, 'effective_point_dwell_s':3.0,
           'sr0_tau_s':.3, 'sr1_tau_s':.3, 'filter_slope_dB_oct':24,
           'comments':'landau-fan; B_1-B_2; empirical D=0; Si=0; n_nominal -1.2..3.2 step .04; B 0, .5..1.4, inverse-B 1.5..10; run-5 calibration'})
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B_1-B_2, base T, Si=0 V, empirical D=0 V/nm; n=-1.2..3.2e12 cm^-2 (111), c_tg geometry anchored; B=0 reference + 10 coarse low-B rows + 85 inverse-B rows 1.5..10 T; 3 s interruptible dwell; sr1=100 uV')
s.ramp(k_tg.volt, float(fan_vtg[0]))
s.ramp(k_bg.volt, float(fan_vbg[0]))
interruptible_sleep(10)
# Independent named measured field avoids ambiguous duplicate setpoint/readback columns.
B_measured_fan = qcodes.Parameter('B_measured_fan', unit='T', get_cmd=magnet.field)
fan_follow = [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,B_measured_fan]
for _p in fan_follow:
    s.fp(_p)
    s.plot('time', _p)
s.plot(k_tg.volt, sr1.X)
fan_counter = {'n':0}

def fan_before(station, writer):
    if fan_counter['n'] % len(fan_n) == 0:
        for name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(name, VTI.temp_logfile_candidates[name], max_age=15, max_period=12)
    interruptible_sleep(3.0)

def fan_after(station, data, writer):
    # [time,B_set,Vtg_set,Vbg_set,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P,B_measured]
    a = np.asarray(data,dtype=float)
    fan_counter['n'] += 1
    reasons=[]
    if not np.all(np.isfinite(a)): reasons.append('nonfinite readback')
    if max(abs(a[6]),abs(a[7])) > 1e-9: reasons.append('gate current >1 nA')
    if not (1.0 <= a[4] <= 1.5 and 0 < a[5] < 1.6 and abs(a[5]-a[4])<.6): reasons.append('temperature outside base window')
    if not (2e-9 < a[8]/mc['sr0_gain'] < 15e-9): reasons.append('drain current outside 2..15 nA')
    if abs(a[8]) >= .9*.02 or abs(a[10]) >= .9*100e-6: reasons.append('lock-in near full scale')
    if abs(a[12]-a[1]) > .03: reasons.append('field readback differs >30 mT')
    if reasons:
        writer.metadata['health_stop'] = '; '.join(reasons)
        print('FAN HEALTH STOP', writer.metadata['health_stop'], 'B=',a[12], 'TG/BG=',a[2:4])
        station.interrupt_requested = True
    if fan_counter['n'] == 1 or fan_counter['n'] % len(fan_n) == 0:
        print(f'FAN CHECKPOINT points={fan_counter["n"]}, B={a[12]:.4f}, Ts={a[4]:.3f}, I={a[8]/mc["sr0_gain"]*1e9:.3f} nA')

s.register_run_before(fan_before, ())
s.register_run_after(fan_after, ())
# Effective dwell is in the interruptible hook; fast_delay=0 avoids a blocking dwell.
s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_vtg,fan_vbg],
                 slow_delay=3.0,fast_delay=0.0)
print('FAN END actual field/gates/T:', magnet.field(), k_tg.volt(), k_bg.volt(), k_si(), T_sample(), T_vaporizer())
# Hold endpoint (10 T after successful completion); no unrequested retraverse.
