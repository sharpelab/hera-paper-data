# Read-only preconditions: no changes to validators, limits, ramp pacing or heaters.
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
for _param,_expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_param.vals._min_value),float(_param.vals._max_value))
    print(_param.full_name,'validator expected',_expected,'actual',_actual)
    assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv=T_sample(),T_vaporizer()
_B=magnet.field(); _Si=k_si()
_ranges=(heater.sample_range(),heater.vaporizer_range())
print('Expected base sample 1.0-1.5 K, vaporizer <1.6 K within 0.6 K; actual',_Ts,_Tv)
print('Expected heaters (0,0), Si 0 V; actual',_ranges,_Si)
assert 1.0<=_Ts<=1.5 and _Tv<1.6 and abs(_Tv-_Ts)<0.6
assert _ranges==(0,0) and abs(_Si)<.01
_ps,_out=magnet.persistent_switch_on(),magnet.output_enabled()
print('Expected PS/output True/True; actual',_ps,_out); assert _ps and _out
print('Expected drive 1 V/13.777 Hz; actual',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1)<.001 and abs(sr1.frequency()-13.777)<.001
for _sr in (sr0,sr1):
    _tau,_slope=_sr.time_constant(),_sr.filter_slope()
    print(_sr.name,'expected tau 0.3 s slope 24 dB; actual',_tau,_slope)
    assert abs(_tau-.3)<1e-9 and _slope==24
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
print('Gate pacing expected 0.005 V steps, Si 0.5 V/s; actual',k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate)
assert k_tg.volt.step==.005 and k_bg.volt.step==.005 and dc205.ramp_rate==.5
print('Expected DC205 RNGE 2/output 1; actual',dc205.voltage_range(),dc205.output())
assert dc205.voltage_range()==2 and dc205.output()==1
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
