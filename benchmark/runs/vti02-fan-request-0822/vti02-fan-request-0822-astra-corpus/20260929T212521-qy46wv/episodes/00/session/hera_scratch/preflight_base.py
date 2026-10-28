# Read-only preconditions; no validators or operating limits are changed.
for label, candidates in [('T_sample',VTI.temp_logfile_candidates['T_sample']),('T_vaporizer',VTI.temp_logfile_candidates['T_vaporizer'])]:
    assert_thermometry_live(label,candidates,max_age=15,max_period=12)
_ts,_tv,_b=T_sample(),T_vaporizer(),magnet.field()
print(f'Expected base 1.0–1.5 K, vaporizer <1.6 K, Si 0 V; actual {_ts:.3f}, {_tv:.3f} K, Si {k_si():.4f} V; B {_b:.5f} T')
assert 1.0<=_ts<=1.5 and _tv<1.6 and abs(_tv-_ts)<0.6 and abs(k_si())<0.01
print('Expected heaters off, magnet PS/output on:',heater.sample_range(),heater.vaporizer_range(),magnet.persistent_switch_on(),magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for par, expected in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(par.vals._min_value),float(par.vals._max_value))
    print(par.full_name,'validator expected',expected,'actual',actual)
    assert actual==expected
assert B_SESSION_CAP==10. and T_SESSION_CAP==100.
print('Expected drive 1 V / 13.777 Hz, tau 0.3 s / slope 24, NPLC 1:',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope(),k_tg.nplci(),k_bg.nplci())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<0.01
assert sr0.time_constant()==0.3 and sr1.time_constant()==0.3
assert sr0.filter_slope()==24 and sr1.filter_slope()==24
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005
assert dc205.ramp_rate==0.5 and dc205.voltage_range()==2 and dc205.output()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
