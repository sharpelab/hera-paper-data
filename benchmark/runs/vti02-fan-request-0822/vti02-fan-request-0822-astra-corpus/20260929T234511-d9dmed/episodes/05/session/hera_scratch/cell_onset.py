# Read-only preflight: inherited state and all committed validators.
import time as _time
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_T0,_Tv,_B0,_Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
print(f'Expected base T 1.0..1.5 K, vaporizer <1.6 K, B near zero, Si=0: actual {_T0:.3f}, {_Tv:.3f}, {_B0:+.4f}, {_Si:+.3f}')
assert 1.0<=_T0<=1.5 and _Tv<1.6 and abs(_Tv-_T0)<0.6 and abs(_B0)<0.05 and abs(_Si)<0.01
for _p,_bounds in ((k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))):
    _actual=(_p.vals._min_value,_p.vals._max_value)
    print(_p.full_name,'expected',_bounds,'actual',_actual)
    assert _actual==_bounds
assert B_SESSION_CAP==10. and T_SESSION_CAP==100.
print('Heater ranges expected 0/0:',heater.sample_range(),heater.vaporizer_range())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Drive expected 1 V / 13.777 Hz:',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
for _li in (sr0,sr1):
    print(_li.name,'expected tau .3 s / 24 dB:',_li.time_constant(),_li.filter_slope())
    assert _li.time_constant()==.3 and _li.filter_slope()==24
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
Vtg_spot,Vbg_spot=calc_gate_voltages(3.2,0.,**CAL)
assert TG_MIN<=Vtg_spot<=TG_MAX and BG_MIN<=Vbg_spot<=BG_MAX
B_vec=field_invB(.3,2.,285)
assert np.max(np.abs(np.diff(1/B_vec)))<=1/(3*33.1)
mc=dict(meas_config)
mc.update({'Si (V)':_Si,'sample_temperature:':_T0,'comments':'Electron onset extension; n=3.2e12 cm^-2, D=0, run-5 calibration; B=.3->2 T, 285 uniform-inverse-B points; sr1 10 uV, tau .3 s; fixed driver settle 3 s'})
sr1.sensitivity(10e-6)
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('onset extension: n=+3.2e12 cm^-2 D=0; B .3->2 T 285 inverse-B points; Vsi=0; run-5 calibration; sr1 10uV; 3s driver settle')
s.ramp(k_bg.volt,Vbg_spot); s.ramp(k_tg.volt,Vtg_spot)
interruptible_sleep(3)
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.plot(magnet.field,_p)
_guard_last=0.
def onset_guard(station,data):
    global _guard_last
    # time, B, Ts, Tv, Itg, Ibg, I0X, I0P, V1X, V1P
    _a=np.asarray(data,dtype=float)
    _bad=(not np.all(np.isfinite(_a))) or not (1.0<=_a[2]<=1.5) or _a[3]>=1.6 or max(abs(_a[4]),abs(_a[5]))>1e-9 or abs(_a[8])>=.9*10e-6 or abs(_a[6])>=.9*sr0.sensitivity()
    if _bad:
        print('ONSET STOP: temperature/leakage/rail/nonfinite',_a)
        station.interrupt_requested=True
    if _time.monotonic()-_guard_last>60:
        for _nm in ('T_sample','T_vaporizer'):
            assert_thermometry_live(_nm,VTI.temp_logfile_candidates[_nm],max_age=15,max_period=12)
        _guard_last=_time.monotonic()
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('ONSET END actual field/gates:',magnet.field(),k_tg.volt(),k_bg.volt())
