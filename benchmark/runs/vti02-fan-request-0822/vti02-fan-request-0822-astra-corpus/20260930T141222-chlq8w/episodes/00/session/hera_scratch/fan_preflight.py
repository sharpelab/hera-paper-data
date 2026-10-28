# Read-only preconditions; compare live state and validators before any write.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
for _p, _bounds in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
 (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
 (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
 _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
 print(_p.full_name,'validator expected',_bounds,'actual',_actual)
 assert _actual==_bounds
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for _name in ('T_sample','T_vaporizer'):
 assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B0=T_sample(),T_vaporizer(),magnet.field()
_Si=k_si(); _ranges=(heater.sample_range(),heater.vaporizer_range())
print('Expected base T 1.0-1.5 K, vaporizer <1.6 K, Si=0, heaters off; actual',_Ts,_Tv,_Si,_ranges)
print('Actual B, TG, BG',_B0,k_tg.volt(),k_bg.volt())
assert 1.0<=_Ts<=1.5 and 0<_Tv<1.6 and abs(_Ts-_Tv)<0.6 and abs(_Si)<0.01 and _ranges==(0,0)
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected drive 1 V / 13.777 Hz, tau 0.3 s / 24 dB; actual',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<0.01
assert sr0.time_constant()==sr1.time_constant()==0.3 and sr0.filter_slope()==sr1.filter_slope()==24
assert k_tg.nplci()==k_bg.nplci()==1
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-0.0894,D_offset=-0.013)
