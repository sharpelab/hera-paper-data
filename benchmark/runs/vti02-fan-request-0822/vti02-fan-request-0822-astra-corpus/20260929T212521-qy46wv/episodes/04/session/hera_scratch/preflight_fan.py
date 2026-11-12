# Read-only preconditions before any instrument set.
for label, p, expected in [
    ('TG',k_tg.volt,(-0.3,1.0)),('BG',k_bg.volt,(-1.3,2.0)),
    ('Si',dc205.smart_voltage,(-25.,25.)),('Si raw',dc205.voltage,(-25.,25.)),
    ('B',magnet.field,(-10.,10.)),('T sample',heater.sample_setpoint,(0.,100.)),
    ('T vaporizer',heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(p.vals._min_value),float(p.vals._max_value))
    print(label,'validator expected',expected,'actual',actual)
    assert actual==expected
assert B_SESSION_CAP==10. and T_SESSION_CAP==100.
assert (k_tg is k_2400_tg) and (k_bg is k_2400_bg) and (k_si is dc205.smart_voltage)
for name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
_ts,_tv,_b=T_sample(),T_vaporizer(),magnet.field()
print('Expected base Ts 1.0-1.5 K, Tv <1.6 K, B near 0 T; actual',_ts,_tv,_b)
assert 1.0<=_ts<=1.5 and 0.5<_tv<1.6 and abs(_ts-_tv)<0.6
assert abs(_b)<0.05
_hr=(heater.sample_range(),heater.vaporizer_range())
_ps=(magnet.persistent_switch_on(),magnet.output_enabled())
print('Expected heaters (0,0), PS/output (True,True); actual',_hr,_ps)
assert _hr==(0,0) and all(_ps)
_si=(dc205.voltage_range(),dc205.output(),k_si(),dc205.ramp_rate)
print('Expected Si range2/on/0V/0.5V/s; actual',_si)
assert _si[:2]==(2,1) and abs(_si[2])<.01 and _si[3]==.5
_drive=(sr1.amplitude(),sr1.frequency())
print('Expected drive 1 V,13.777 Hz; actual',_drive)
assert abs(_drive[0]-1)<1e-6 and abs(_drive[1]-13.777)<.01
for li in [sr0,sr1]:
    settings=(li.time_constant(),li.filter_slope())
    print(li.name,'expected tau0.3/slope24; actual',settings)
    assert settings==(.3,24)
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
print('NPLC expected 1,1; actual',k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci()==1 and k_bg.nplci()==1
print('Expected hardwired B1-B2 / T0-B3; actual',WIRING)
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
