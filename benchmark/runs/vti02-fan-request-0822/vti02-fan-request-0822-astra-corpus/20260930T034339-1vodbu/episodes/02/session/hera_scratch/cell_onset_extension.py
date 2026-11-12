# Read-only preconditions first. No safety or pacing changes.
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages
from hera.analysis import field_invB
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_ts,_tv,_b=T_sample(),T_vaporizer(),magnet.field()
_si=k_si();_ranges=(heater.sample_range(),heater.vaporizer_range())
print(f'Expected base 1.0-1.5 K, vaporizer <1.6 K, B near 0, Si=0, heaters off; actual {_ts}, {_tv}, {_b}, {_si}, {_ranges}')
assert 1<=_ts<=1.5 and 0<_tv<1.6 and abs(_tv-_ts)<0.6
assert abs(_b)<0.02 and abs(_si)<0.01 and _ranges==(0,0)
assert magnet.persistent_switch_on() and magnet.output_enabled()
for _p,_expected in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name,'expected validator',_expected,'actual',_actual);assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
print('Expected drive 1 V/13.777 Hz, tau .3 s/24 dB, NPLC 1; actual',sr1.amplitude(),sr1.frequency(),sr1.time_constant(),sr1.filter_slope(),k_tg.nplci(),k_bg.nplci())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr1.time_constant()==.3 and sr1.filter_slope()==24 and sr0.time_constant()==.3
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
assert WIRING['sr1+']=='B_1' and WIRING['sr1-']=='B_2' and WIRING['drain']=='B_3'
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6
CAL=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
vt,vb=calc_gate_voltages(3.2,0.,**CAL)
for p,v in [(k_tg.volt,vt),(k_bg.volt,vb)]:p.validate(float(v))
B_vec=field_invB(.3,1.5,321)
assert np.max(np.abs(np.diff(1/B_vec)))<=1/(3*40)
sr1.sensitivity(5e-6)  # 500 ohm FS; run 6 <100 ohm in this restricted window.
mc=dict(meas_config);mc['Si (V)']=_si;mc['sample_temperature:']=_ts
mc['comments']='Electron onset extension; n=+3.2e12 D=0, run-5 calibration; B=.3 to 1.5 T uniform 1/B 321 points; sr1 5uV, 10nA, 3s driver settle, gates held at endpoint'
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check');s.add_comment(mc['comments'])
s.ramp(k_bg.volt,float(vb));s.ramp(k_tg.volt,float(vt));interruptible_sleep(3)
# [time,B,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P]
_params=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]
for p in _params:s.fp(p);s.plot(magnet.field,p)
def extension_guard(station,data):
    if abs(data[4])>1e-9 or abs(data[5])>1e-9 or not 1<=data[2]<=1.5 or abs(data[8])>=.9*5e-6:
        print('STOP: extension leakage/temperature/rail guard',data);station.interrupt_requested=True
s.register_run_after(extension_guard,())
assert magnet.settle_s>=3
s.sweep(magnet.field,B_vec,delay=0)
print('Extension end actual B/TG/BG:',magnet.field(),k_tg.volt(),k_bg.volt())
