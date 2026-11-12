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
assert abs(_b)<0.02, 'handoff field expected 0 T'
from sharpelab_nb.gates import calc_gate_voltages
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-0.0894,D_offset=-0.013)
vt,vb=calc_gate_voltages(3.2,0.,**CAL)
assert -0.3<=vt<=1. and -1.3<=vb<=2.
B_vec=field_invB(0.2,1.5,435)
assert np.max(np.abs(np.diff(1/B_vec)))<=0.01
# Fixed 50 uV inherited from run 6, 5 kohm full scale; 3 s driver dwell = 10 tau.
sr1.sensitivity(50e-6)
assert magnet.settle_s>=3. and sr0.sensitivity()==0.02
mc=dict(meas_config)
mc.update({'Si (V)':k_si(),'sample_temperature:':_ts,'comments':'sdh-spot-check onset extension: n=+3.2e12 cm^-2 D=0, B 0.2->1.5 T inverse-B 435 points; run-5 CAL; sr1 50uV, 10nA; no Si move'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,vb); s.ramp(k_tg.volt,vt)
interruptible_sleep(10)
for p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(p); s.plot('time',p)
# [time,B,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P]
def onset_guard(station,data):
    d=np.asarray(data,dtype=float)
    if not np.all(np.isfinite(d)) or abs(d[4])>1e-9 or abs(d[5])>1e-9 or not 1.0<=d[2]<=1.5 or d[3]>=1.6 or abs(d[8])>=0.9*50e-6 or not 8e-9<d[6]/-1e6<12e-9:
        print('ONSET EXTENSION STOP: data guard',d)
        station.interrupt_requested=True
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('Extension endpoint:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample())
