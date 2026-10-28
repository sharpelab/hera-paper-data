# sdh-spot-check: resolve run-6 censored onset before committing the fan.
from sharpelab_nb.gates import calc_gate_voltages
# Preconditions first; all are reads, no safety/pacing edits.
for name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
_T,_Tv,_B,_Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
print(f'Expected base T 1.0..1.5 K, vaporizer within 0.6 K; actual {_T}, {_Tv}; expected B~0, Si=0; actual {_B}, {_Si}')
assert 1.0<=_T<=1.5 and abs(_Tv-_T)<0.6 and abs(_B)<0.05 and abs(_Si)<0.01
print('Expected heaters off / PS on / output on:',heater.sample_range(),heater.vaporizer_range(),magnet.persistent_switch_on(),magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for p,limits in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    actual=(p.vals._min_value,p.vals._max_value);print(p.full_name,'validator expected',limits,'actual',actual);assert actual==limits
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
print('Expected drive 1 V /13.777 Hz, tau 0.3 s /24 dB, NPLC 1:',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope(),k_tg.nplci(),k_bg.nplci())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr0.time_constant()==.3 and sr1.time_constant()==.3 and sr0.filter_slope()==24 and sr1.filter_slope()==24
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert k_tg.volt.step==.005 and k_bg.volt.step==.005 and dc205.ramp_rate==.5
assert dc205.voltage_range()==2 and dc205.output()==1
assert magnet.settle_s>=3
# Identical rounded calibration to run 6, for a strict shared-density comparison.
_onset_cal=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
_vt,_vb=calc_gate_voltages(3.2,0.,**_onset_cal)
assert -.3<=_vt<=1 and -1.3<=_vb<=2
_Bcheck=field_invB(1.8,.2,446)
assert np.max(np.abs(np.diff(1/_Bcheck)))<=.01001
sr1.sensitivity(10e-6) # 1 kOhm FS; run 6 has <60 ohm in this window, ample margin.
_mc=dict(meas_config);_mc['Si (V)']=_Si;_mc['sample_temperature:']=_T
_mc['comments']='onset/grid-change repeat of run 6: n_A=+3.2e12 cm^-2 D_A=0; B=1.8->0.2 T uniform 1/B,446 points; sr1=10uV; tau=.3s slope=24; magnet settle>=3s'
s=sweep.AsyncStation(_mc)
s.add_comment('sdh-spot-check')
s.add_comment(_mc['comments'])
s.ramp(k_bg.volt,float(_vb));s.ramp(k_tg.volt,float(_vt))
interruptible_sleep(10)
# 0->1.8 T: 13.14 min bare ramp at 0.137 T/min. Blocks until reached.
magnet.field(1.8)
for p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(p);s.plot('time',p)
# [time,B,Ts,Tv,Itg,Ibg,I_X,I_P,V_X,V_P]
def onset_guard(station,data):
    vals=np.asarray(data,dtype=float)
    if not np.isfinite(vals).all() or not 1.0<=vals[2]<=1.5 or abs(vals[3]-vals[2])>=.6 or max(abs(vals[4]),abs(vals[5]))>1e-9 or abs(vals[8])>=.9*10e-6:
        print('ONSET CHECK STOP: invalid T/leakage/rail',vals)
        station.interrupt_requested=True
s.register_run_after(onset_guard,())
s.sweep(magnet.field,_Bcheck,delay=0)
print('Post-check measured B/T/gates:',magnet.field(),T_sample(),k_tg.volt(),k_bg.volt())
