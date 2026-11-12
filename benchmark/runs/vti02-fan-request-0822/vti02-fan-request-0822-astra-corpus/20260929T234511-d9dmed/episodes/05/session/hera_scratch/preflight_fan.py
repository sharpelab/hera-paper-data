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
