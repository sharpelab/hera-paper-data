# sdh-spot-check: resolve censored electron onset before sizing the fan.
from sharpelab_nb.gates import calc_gate_voltages
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
print(f'Expected base T 1.0–1.5 K, vaporizer <1.6 K, B≈0, Si=0: actual {_Ts}, {_Tv}, {_B}, {k_si()}')
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_B) < 0.05 and abs(k_si()) < 0.01
print('Expected heaters off and magnet PS/output on:', heater.sample_range(), heater.vaporizer_range(), magnet.persistent_switch_on(), magnet.output_enabled())
assert heater.sample_range() == 0 and heater.vaporizer_range() == 0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for _p, _bounds in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    _actual = (float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name, 'expected',_bounds,'actual',_actual)
    assert _actual == _bounds
assert B_SESSION_CAP == 10. and T_SESSION_CAP == 100.
print('Expected drive 1V/13.777Hz, tau .3s/24dB, NPLC 1:',sr1.amplitude(),sr1.frequency(),sr1.time_constant(),sr1.filter_slope(),k_tg.nplci(),k_bg.nplci())
assert abs(sr1.amplitude()-1.) < 1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr0.time_constant()==.3 and sr1.time_constant()==.3
assert sr0.filter_slope()==24 and sr1.filter_slope()==24
assert magnet.settle_s >= 3.0
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
CAL = dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
_vt,_vb = calc_gate_voltages(3.2,0.,**CAL)
k_tg.volt.validate(_vt); k_bg.volt.validate(_vb)
B_vec = field_invB(.2,1.5,363)
assert np.max(np.abs(np.diff(1/B_vec))) < 1/(2*40.)
sr1.sensitivity(50e-6)
mc=dict(meas_config);mc.update({'Si (V)':k_si(),'sample_temperature:':_Ts,'comments':'Electron onset extension n=+3.2e12 D=0; 0.2→1.5T uniform 1/B 363pts; run-5 calibration; 3s magnet settle, 50uV sr1'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,_vb);s.ramp(k_tg.volt,_vt)
interruptible_sleep(10)
# [time,B,T_sample,T_vaporizer,Itg,Ibg,sr0X,sr0P,sr1X,sr1P]
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(_p);s.plot('time',_p)
_onset_trip=[]
def onset_guard(station,data):
    if not np.all(np.isfinite(data)) or not 1.0<=data[2]<=1.5 or data[3]>=1.6 or max(abs(data[4]),abs(data[5]))>1e-9 or abs(data[8])>.9*50e-6:
        _onset_trip.append(list(data)); print('STOP: onset quality/thermal/leakage guard',data);station.interrupt_requested=True
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('Actual endpoint:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample())
assert not _onset_trip, 'Onset sweep stopped; inspect actual state before another move'
