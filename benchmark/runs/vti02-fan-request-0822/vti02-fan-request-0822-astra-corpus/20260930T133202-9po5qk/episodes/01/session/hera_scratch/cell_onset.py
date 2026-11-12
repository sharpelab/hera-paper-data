# Read-only preconditions, then the in-envelope onset / grid reproduction check.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
for name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(name, VTI.temp_logfile_candidates[name], max_age=15, max_period=12)
Ts, Tv, B0, Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
print('Expected base 1.0..1.5 K, vaporizer <1.6 K and within 0.6 K, B~0, Si~0; actual', Ts, Tv, B0, Si)
assert 1.0 <= Ts <= 1.5 and 0 < Tv < 1.6 and abs(Ts-Tv)<0.6
assert abs(B0)<0.02 and abs(Si)<0.01
print('Expected heater ranges 0/0, magnet PS/output on:', heater.sample_range(), heater.vaporizer_range(), magnet.persistent_switch_on(), magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for p, bounds in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),(dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),(magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),(heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(p.vals._min_value),float(p.vals._max_value))
    print(p.full_name, 'expected',bounds,'actual',actual)
    assert actual==bounds
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected 1 V/13.777 Hz, tau .3/.3 s, slopes24/24, NPLC1/1:',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope(),k_tg.nplci(),k_bg.nplci())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01
assert sr0.time_constant()==.3 and sr1.time_constant()==.3 and sr0.filter_slope()==24 and sr1.filter_slope()==24
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert magnet.settle_s>=3 and dc205.ramp_rate==.5 and dc205.voltage_range()==2 and dc205.output()==1
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
assert sr0.sensitivity()==.02
CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
vt,vb=calc_gate_voltages(3.2,0,**CAL)
k_tg.volt.validate(float(vt)); k_bg.volt.validate(float(vb))
B_vec=1/np.linspace(1/.20,1/4.,635)
assert np.max(np.abs(np.diff(1/B_vec))) < 1/(2*66)
for b in B_vec: magnet.field.validate(float(b))
print('Designed gates and n,D roundtrip:',vt,vb,calc_nD(vt,vb,**CAL))
sr1.sensitivity(10e-6)
mc=dict(meas_config); mc.update({'Si (V)':Si,'sample_temperature:':Ts,'comments':'electron onset repair n=3.2e12 D=0 B=.2->4T uniform 1/B 635 pts; sr1 10uV tau.3 slope24; run6 calibration'})
s=sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('onset and grid reproduction: n=+3.2e12 cm^-2 D=0; B .20->4.0T 635 uniform-inverse-B points; Vsi=0; sr1 10uV, 10nA; run5 calibration rounded identically to run6')
s.ramp(k_bg.volt,float(vb)); s.ramp(k_tg.volt,float(vt)); interruptible_sleep(10)
# time, B_set, T_sample, T_vaporizer, Itg, Ibg, sr0X, sr0P, sr1X, sr1P
channels=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]
for p in channels:
    s.fp(p); s.plot(magnet.field,p)
_onset_counter=0
def onset_guard(station,data):
    global _onset_counter
    _onset_counter+=1
    bad=[]
    if not (1.0<=float(data[2])<=1.5 and 0<float(data[3])<1.6): bad.append('temperature')
    if max(abs(float(data[4])),abs(float(data[5])))>1e-9: bad.append('leakage')
    if not 8e-9 < float(data[6])/-1e6 < 12e-9: bad.append('drain current')
    if abs(float(data[8]))>.9*10e-6 or abs(float(data[6]))>.9*.02: bad.append('rail approach')
    if _onset_counter%20==0:
        actual_B=magnet.field()
        print('CHECKPOINT B set/read',data[1],actual_B)
        if abs(actual_B-float(data[1]))>.02: bad.append('field mismatch')
        for name in ('T_sample','T_vaporizer'):
            try: assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
            except Exception as exc: bad.append(str(exc))
    if bad:
        print('STOP:',bad); station.interrupt_requested=True
s.register_run_after(onset_guard,())
s.sweep(magnet.field,B_vec,delay=0)
print('END actual B,Tg,Bg,Ts,Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample(),T_vaporizer())
