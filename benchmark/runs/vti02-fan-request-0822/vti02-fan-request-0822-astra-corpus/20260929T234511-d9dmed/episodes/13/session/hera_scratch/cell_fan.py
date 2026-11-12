# landau-fan-vti: D~0, electrons 2.8..3.2e12 cm^-2, B 1->6 T.
# Read-only preconditions precede every instrument write.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

def fan_vrange(p):
    return float(p.vals._min_value), float(p.vals._max_value)
for p, expected in [(k_tg.volt,(-.3,1.)), (k_bg.volt,(-1.3,2.)),
                    (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    actual=fan_vrange(p)
    print('SAFETIES',p.full_name,'expected',expected,'actual',actual)
    assert actual==expected, 'SAFETIES mismatch; stop before writes'
assert B_SESSION_CAP==10.0 and T_SESSION_CAP==100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
_Ts,_Tv,_B=T_sample(),T_vaporizer(),magnet.field()
_ranges=(heater.sample_range(),heater.vaporizer_range())
_Si=(dc205.voltage(),dc205.voltage_range(),dc205.output())
_PS=(magnet.persistent_switch_on(),magnet.output_enabled())
print('Expected Ts 1.0..1.5 K, Tv<1.6 K within 0.6 K of Ts, B near 0; actual',_Ts,_Tv,_B)
print('Expected heater ranges 0/0, Si 0 V/RNGE2/on, magnet PS/output on; actual',_ranges,_Si,_PS)
assert 1.0<=_Ts<=1.5 and 0<_Tv<1.6 and abs(_Tv-_Ts)<.6 and abs(_B)<.05
assert _ranges==(0,0) and abs(_Si[0])<.01 and _Si[1:]==(2,1) and all(_PS)
print('Gate starting readback (will set):',k_tg.volt(),k_bg.volt())
print('Expected 5mV gate steps, Si 0.5V/s; actual',k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate)
assert k_tg.volt.step==.005 and k_bg.volt.step==.005 and dc205.ramp_rate==.5
print('Expected gate-current NPLC 1/1; actual',k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected 1 V / 13.777 Hz drive; actual',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1.)<.001 and abs(sr1.frequency()-13.777)<.01
for lia in [sr0,sr1]:
    tau,slope=lia.time_constant(),lia.filter_slope()
    print(lia.name,'expected tau .3 s / slope 24 dB, actual',tau,slope)
    assert tau==.3 and slope==24
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
assert abs(magnet.settle_s-3.)<1e-6

FAN_CAL=dict(c_tg=.0027960593093052633,c_bg=.002160696465377614,
             n_offset=-.08937933224099137,D_offset=-.013)
ns=np.linspace(2.8,3.2,11)
Vtgs,Vbgs=calc_gate_voltages(ns,np.zeros(len(ns)),**FAN_CAL)
B_vec=field_invB(1.,6.,221)
_nrt,_Drt=calc_nD(Vtgs,Vbgs,**FAN_CAL)
assert np.allclose(_nrt,ns) and np.max(np.abs(_Drt))<1e-10
assert np.min(Vtgs)>=-.3 and np.max(Vtgs)<=1. and np.min(Vbgs)>=-1.3 and np.max(Vbgs)<=2.
assert B_vec.min()>=0 and B_vec.max()<=B_SESSION_CAP
assert np.max(np.abs(np.diff(1/B_vec)))<=1/(2*132.)+1e-12
print('Grid 221 B x 11 n; gate spans',Vtgs[[0,-1]],Vbgs[[0,-1]],'V')

# Fixed acquisition settings; no validator or gate-pacing writes.
sr1.sensitivity(20e-6) # 2 kohm nominal FS, >10x run-6 |R| through 6 T.
sr0.sensitivity(.02)  # 20 nA full scale, 10 nA measured drain.
assert sr1.sensitivity()==20e-6 and sr0.sensitivity()==.02
mc=dict(meas_config)
mc.update({'Si (V)':0.,'sample_temperature:':_Ts,'calibration':FAN_CAL,
           'calibration_source':'run 5; ratio fitted, absolute scale geometry prior',
           'acquisition':{'sr1_sensitivity':20e-6,'sr0_sensitivity':.02,
                          'tau_s':.3,'slope_dB':24,'point_dwell_s':3.,'NPLC':1},
           'comments':'D=0; n=2.8..3.2e12 cm^-2; B=1..6T ascending uniform 1/B, 221x11; Si=0; sr1=B_1-B_2'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('n=2.8..3.2e12 cm^-2 (11); D=0 V/nm run-5 calibration; B=1->6T uniform 1/B (221); Si=0V; 10nA; sr1 20uV, tau .3s/24dB; 3s dwell; field parked at 6T on success')
s.ramp(k_bg.volt,float(Vbgs[0])); s.ramp(k_tg.volt,float(Vtgs[0]))
interruptible_sleep(3)
# Sweep itself positions from actual ~0 T to 1 T: 1/.137=7.3 min, no return traverse.
# Columns: time,B,Vtg,Vbg,Ts,Tv,Itg,Ibg,X0,P0,X1,P1.
for p in [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]:
    s.fp(p)
    s.plot('time',p)
_fan_count={'points':0,'stop_reason':None}

def fan_before(station):
    if _fan_count['points']%len(ns)==0:
        for name in ['T_sample','T_vaporizer']:
            assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        row=_fan_count['points']//len(ns)
        measured=magnet.field()
        print('Row',row+1,'B expected/actual',float(B_vec[row]),measured)
        assert abs(measured-B_vec[row])<.025, 'Measured B differs from planned row'

def fan_after(station,data):
    _fan_count['points']+=1
    reason=None
    if not all(np.isfinite(float(v)) for v in data): reason='nonfinite read'
    elif abs(float(data[6]))>1e-9 or abs(float(data[7]))>1e-9: reason='gate leakage >1nA'
    elif not (1.0<=float(data[4])<=1.5 and 0<float(data[5])<1.6 and abs(float(data[4])-float(data[5]))<.6): reason='base temperature lost'
    elif abs(float(data[10]))>.9*20e-6: reason='sr1 approaching rail'
    elif not (8e-9<float(data[8])/-1e6<12e-9): reason='drain current outside 8..12nA'
    if reason:
        _fan_count['stop_reason']=reason
        print('FAN STOP:',reason,'B',data[1],'Vtg,Vbg',data[2:4])
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1.,fast_delay=3.)
print('FAN RESULT:',_fan_count)
print('Actual endpoint B,Tg,Bg,Si,Ts,Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
# Hold actual endpoint for review; no hidden return/restore after an interrupt.
