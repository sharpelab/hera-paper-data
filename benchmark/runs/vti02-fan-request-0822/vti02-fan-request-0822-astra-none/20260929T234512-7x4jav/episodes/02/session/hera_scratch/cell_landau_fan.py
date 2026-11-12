# Plan step 4: constant-working-D Landau fan, B_1 - B_2 only.
# Inherited-state reads and safety validation precede every instrument write.
import numpy as np
from scipy.constants import e as _e, epsilon_0 as _eps0
from hera.analysis import field_invB

for _label in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_label, VTI.temp_logfile_candidates[_label], max_age=15, max_period=12)
_Ts, _Tv, _Bstart = T_sample(), T_vaporizer(), magnet.field()
_Si = k_si(); _ranges = (heater.sample_range(), heater.vaporizer_range())
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'EXPECTED base Ts=1.0..1.5 K, Tv<1.6 K, |B|<0.02 T, Si=0 V, heaters=(0,0), PS/output on; ACTUAL Ts={_Ts}, Tv={_Tv}, B={_Bstart}, Si={_Si}, ranges={_ranges}, PS/output={_ps}/{_out}')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts) < .6
assert abs(_Bstart) < .02 and abs(_Si) < .01 and _ranges == (0, 0) and _ps and _out
for _p, _expected in ((k_tg.volt,(-.3,1.)), (k_bg.volt,(-1.3,2.)),
                      (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                      (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                      (heater.vaporizer_setpoint,(0.,100.))):
    _actual = (float(_p.vals._min_value),float(_p.vals._max_value))
    print(f'SAFETIES {_p.full_name}: expected {_expected}, actual {_actual}')
    assert _actual == _expected
assert B_SESSION_CAP == 10. and T_SESSION_CAP == 100.
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
_expected_wiring = {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                    'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('EXPECTED hardwired B_1-B_2; ACTUAL', WIRING)
assert WIRING == _expected_wiring
_drive, _freq = sr1.amplitude(), sr1.frequency()
_tau0, _tau1 = sr0.time_constant(), sr1.time_constant()
_slope0, _slope1 = sr0.filter_slope(), sr1.filter_slope()
_nplc = (k_tg.nplci(),k_bg.nplci())
_steps = (k_tg.volt.step,k_bg.volt.step)
_rng, _dc_on = dc205.voltage_range(),dc205.output()
print(f'EXPECTED drive 1 V/13.777 Hz, tau .3/.3 s, slope 24/24, NPLC 1/1, gate step .005/.005 V; ACTUAL {_drive}/{_freq}, tau {_tau0}/{_tau1}, slope {_slope0}/{_slope1}, NPLC {_nplc}, steps {_steps}')
print(f'EXPECTED Si RNGE=2, output=1, pacing=.5 V/s; ACTUAL {_rng}, {_dc_on}, {dc205.ramp_rate}')
assert abs(_drive-1.) < 1e-6 and abs(_freq-13.777) < .01
assert (_tau0,_tau1) == (.3,.3) and (_slope0,_slope1) == (24,24)
assert _nplc == (1.,1.) and _steps == (.005,.005)
assert _rng == 2 and _dc_on == 1 and abs(dc205.ramp_rate-.5) < 1e-9
assert sr0.sensitivity() == .02
assert meas_config['sr0_gain'] == -1e6 and meas_config['bias_resistor'] == 100e6 and meas_config['bias_channel'] == 'sr1'

# Run 5 ratio/offsets; absolute scale is geometry-anchored, D zero is a working symmetry convention.
FAN_CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137, D_offset=-0.013)
n_nom = np.linspace(-1.2,3.2,111)  # display units: 1e12 cm^-2
_q = _e*(n_nom-FAN_CAL['n_offset'])*1e16
_d = 2*_eps0*(0.-FAN_CAL['D_offset'])*1e9
Vt_fan = (_q+_d)/(2*FAN_CAL['c_tg'])
Vb_fan = (_q-_d)/(2*FAN_CAL['c_bg'])
B_fan = np.r_[0., .75, field_invB(1.5,10.,81)]
for _p,_vec in ((k_tg.volt,Vt_fan),(k_bg.volt,Vb_fan),(magnet.field,B_fan)):
    for _v in _vec: _p.validate(float(_v))
print(f'GRID {len(B_fan)} B rows x {len(n_nom)} gate pairs; TG {Vt_fan[0]:+.6f}..{Vt_fan[-1]:+.6f} V, BG {Vb_fan[0]:+.6f}..{Vb_fan[-1]:+.6f} V')
print('RAMP: 0->10 T at 1/7.3 T/min = 73 min bare; estimated total 11 h incl dwell, flybacks, reads, contingency')

sr1.sensitivity(100e-6)
assert sr1.sensitivity() == 100e-6
mc_fan = dict(meas_config)
mc_fan.update({'sr1_gain':1., 'Si (V)':_Si, 'sample_temperature:':_Ts,
               'fan_calibration':FAN_CAL, 'n_nominal_1e12_cm2':n_nom.tolist(),
               'D_working_V_nm':0., 'absolute_density_scale':'geometry prior; pending LL check',
               'D_zero':'run-5 CNP resistance symmetry; provisional',
               'lockin_tau_s':[_tau0,_tau1], 'lockin_slope_dB':[_slope0,_slope1],
               'gate_nplci':list(_nplc), 'comments':'landau-fan: B_1-B_2, B 0/.75/1.5..10 T, 83x111, nominal n -1.2..3.2e12 at working D=0, base T, Si=0, 3 s dwell, sr1 100 uV'})
s = sweep.AsyncStation(mc_fan)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B=[0,0.75]+81 uniform-in-1/B points 1.5->10 T; n_nominal=-1.20..+3.20e12 cm^-2 (111, .04 step), D_working=0 V/nm; TG=-.277033..+.983594 V, BG=-.465040..+1.166281 V; Si=0; 10 nA; base T; fast_delay=3 s; calibration run 5, absolute scale provisional')
# Raw X values stored (gain=1); metadata gains used by hera-watch/analysis.
_fan_follow = [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field,k_tg.volt,k_bg.volt]
for _p in _fan_follow:
    s.fp(_p)
    s.plot('time',_p)
s.plot(k_tg.volt,magnet.field,sr1.X)

_guard = {'points':0, 'reason':None}
def fan_guard(station, data):
    # multimegasweep layout: time, B set, TG set, BG set, followed values.
    _v = dict(zip([p.full_name for p in _fan_follow],map(float,data[4:])))
    _reason=[]
    if not np.all(np.isfinite(data)): _reason.append('nonfinite data')
    if max(abs(_v[k_tg.curr.full_name]),abs(_v[k_bg.curr.full_name])) > 1e-9:
        _reason.append('gate current >1 nA')
    if abs(_v[sr0.X.full_name]) >= .9*.02 or abs(_v[sr1.X.full_name]) >= .9*100e-6:
        _reason.append('lock-in >=90% full scale')
    _Id = _v[sr0.X.full_name]/mc_fan['sr0_gain']
    if not 5e-9 < _Id < 12e-9: _reason.append('drain current outside 5..12 nA')
    if not 1.0 <= _v[T_sample.full_name] <= 1.5: _reason.append('sample T outside base window')
    if not 0 < _v[T_vaporizer.full_name] < 1.6: _reason.append('vaporizer outside base window')
    if abs(_v[magnet.field.full_name]-float(data[1])) > .03: _reason.append('field readback mismatch >30 mT')
    if abs(_v[k_tg.volt.full_name]-float(data[2])) > .003 or abs(_v[k_bg.volt.full_name]-float(data[3])) > .003:
        _reason.append('gate readback mismatch >3 mV')
    if _guard['points'] % len(n_nom) == 0:
        try:
            for _label in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_label,VTI.temp_logfile_candidates[_label],max_age=15,max_period=12)
        except Exception as _exc: _reason.append('thermometry freshness: '+str(_exc))
    _guard['points'] += 1
    if _reason:
        _guard['reason']='; '.join(_reason)
        print('FAN STOP:',_guard['reason'], 'B/TG/BG setpoints',data[1:4])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
# Existing driver pacing handles initial positioning and every row flyback.
s.ramp(k_tg.volt,float(Vt_fan[0])); s.ramp(k_bg.volt,float(Vb_fan[0]))
interruptible_sleep(10)
fan_result = s.multimegasweep([magnet.field],[B_fan], [k_tg.volt,k_bg.volt],[Vt_fan,Vb_fan],
                            slow_delay=3.,fast_delay=3.)
print('FAN END:',fan_result.id,'interrupted=',fan_result.metadata.get('interrupted'),'guard=',_guard)
print('ACTUAL B/TG/BG/Si/Ts/Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
# Hold end state; no automatic return after completion or abort.
