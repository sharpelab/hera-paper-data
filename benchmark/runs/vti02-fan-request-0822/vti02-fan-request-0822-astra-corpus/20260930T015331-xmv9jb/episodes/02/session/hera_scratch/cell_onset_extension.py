# sdh-spot-check: resolve the censored/undersampled low-field onset before the fan.
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_ts, _tv, _b, _si = T_sample(), T_vaporizer(), magnet.field(), k_si()
print('Expected base T 1.0-1.5 K, vaporizer within 0.6 K, B=0 +/-0.05 T, Si=0; actual:', _ts, _tv, _b, _si)
assert 1 <= _ts <= 1.5 and 0 < _tv < 1.6 and abs(_tv-_ts)<0.6
assert abs(_b)<0.05 and abs(_si)<0.01
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for _p,_limits in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),(dc205.smart_voltage,(-25,25)),(dc205.voltage,(-25,25)),(magnet.field,(-10,10)),(heater.sample_setpoint,(0,100)),(heater.vaporizer_setpoint,(0,100))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name,'expected validator',_limits,'actual',_actual)
    assert _actual==_limits
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
print('Expected drive 1 V/13.777 Hz, lock-in tau 0.3 s/24 dB; actual:',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<0.01
assert sr0.time_constant()==sr1.time_constant()==0.3 and sr0.filter_slope()==sr1.filter_slope()==24
assert magnet.settle_s>=3 and k_tg.volt.step==k_bg.volt.step==0.005
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
CAL = dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-0.0894,D_offset=-0.013)
_vt,_vb=calc_gate_voltages(3.2,0,**CAL)
B_vec=field_invB(0.25,1.5,279)
assert np.all(np.diff(B_vec)>0) and np.max(np.abs(np.diff(1/B_vec)))<=0.012
k_tg.volt.validate(float(_vt)); k_bg.volt.validate(float(_vb))
sr1.sensitivity(50e-6)
mc=dict(meas_config); mc.update({'Si (V)':_si,'sample_temperature:':_ts,'calibration':CAL,'comments':'sdh-spot-check onset extension; n=+3.2e12 D=0; B 0.25->1.5 T, 279 uniform-1/B points; sr1 50uV; 3s driver settle'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('Onset extension for landau-fan-vti; n=+3.2e12 D=0 run-5 calibration; B 0.25->1.5T, 279 points uniform 1/B, delta<=0.012/T; Si=0; sr1 50uV; base T; read-only safety verification')
s.ramp(k_bg.volt,float(_vb)); s.ramp(k_tg.volt,float(_vt)); interruptible_sleep(10)
# time,B,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(_p); s.plot(magnet.field,_p)
def _onset_guard(station,data):
    if not np.all(np.isfinite(data)) or not 1<=data[2]<=1.5 or not 0<data[3]<1.6 or abs(data[4])>1e-9 or abs(data[5])>1e-9 or abs(data[8])>0.9*50e-6:
        print('ONSET STOP: temperature/leakage/rail/nonfinite',data)
        station.interrupt_requested=True
s.register_run_after(_onset_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('Actual endpoint B, TG, BG:',magnet.field(),k_tg.volt(),k_bg.volt())
