# landau-fan-vti — run-5 calibration, run-6 onset and acquisition design.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Preconditions: read before any instrument write. Same-kernel SAFETIES cell 18 [10].
for _p, _bounds in [(k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name, 'validator expected',_bounds,'actual',_actual)
    assert _actual == _bounds
assert B_SESSION_CAP == 10. and T_SESSION_CAP == 100.
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B=T_sample(),T_vaporizer(),magnet.field()
_vsi=dc205.voltage(); _rng=dc205.voltage_range(); _out=dc205.output()
_ps,_enabled=magnet.persistent_switch_on(),magnet.output_enabled()
_hr=(heater.sample_range(),heater.vaporizer_range())
print('Expected base Ts 1.0–1.5 K, Tv <1.6 K tracking within 0.6 K; actual',_Ts,_Tv)
print('Expected handoff B~0 T, Si=0 V/RNGE2/output1, PS/output on, heaters off; actual',_B,_vsi,_rng,_out,_ps,_enabled,_hr)
print('Gate starting readbacks (cell sets both):',k_tg.volt(),k_bg.volt())
assert 1.0<=_Ts<=1.5 and 0<_Tv<1.6 and abs(_Tv-_Ts)<0.6
assert abs(_B)<0.05 and abs(_vsi)<0.01 and _rng==2 and _out==1
assert _ps and _enabled and _hr==(0,0)
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
print('Pacing expected TG/BG step .005 V, Si .5 V/s; actual',k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate)
assert k_tg.volt.step==k_bg.volt.step==0.005 and dc205.ramp_rate==0.5
for _li in (sr0,sr1):
    _tau,_slope=_li.time_constant(),_li.filter_slope()
    print(_li.name,'expected tau .3 s / 24 dB; actual',_tau,_slope)
    assert _tau==0.3 and _slope==24
_drive,_freq=sr1.amplitude(),sr1.frequency()
print('Expected drive 1 V / 13.777 Hz, sr0 sens .02 V; actual',_drive,_freq,sr0.sensitivity())
assert abs(_drive-1.)<1e-6 and abs(_freq-13.777)<.01 and sr0.sensitivity()==.02
assert magnet.settle_s>=3.0
for _k in (k_tg,k_bg):
    print(_k.name,'expected output ON, VOLT mode, NPLC 1; actual',_k.output(),_k.mode(),_k.nplci())
    assert _k.output() and _k.mode()=='VOLT' and _k.nplci()==1.

CAL_FAN=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
ns_fan=np.linspace(3.2,2.8,11)
Vtgs_fan,Vbgs_fan=calc_gate_voltages(ns_fan,np.zeros_like(ns_fan),**CAL_FAN)
B_fan=field_invB(1.017617880804576,6.47,233)
assert np.all((Vtgs_fan>=TG_MIN)&(Vtgs_fan<=TG_MAX))
assert np.all((Vbgs_fan>=BG_MIN)&(Vbgs_fan<=BG_MAX))
assert np.all((B_fan>0)&(B_fan<=B_SESSION_CAP)) and np.all(np.diff(B_fan)>0)
_nr,_dr=calc_nD(Vtgs_fan,Vbgs_fan,**CAL_FAN)
assert np.allclose(_nr,ns_fan) and np.max(np.abs(_dr))<1e-10
assert np.max(np.abs(np.diff(1/B_fan)))<1/(2*140.)
assert 1.2*np.max(np.abs(np.diff(ns_fan)))<=B_fan[0]/10.33916924/2
print('Fan: NB,Nn=',len(B_fan),len(ns_fan),'TG endpoints',Vtgs_fan[[0,-1]],'BG endpoints',Vbgs_fan[[0,-1]])

# Acquisition change only; no validator, operating-limit or ramp-pacing edits.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
mc_fan=dict(meas_config)
mc_fan.update({'Si (V)':_vsi,'sample_temperature:':_Ts,'calibration':CAL_FAN,
    'n_setpoints_1e12_cm2':ns_fan.tolist(),'D_V_nm':0.,
    'comments':'landau-fan-vti: B_1-B_2, n 3.2->2.8e12 D~0; B 1.017618->6.47 T, 233 inverse-B rows x 11 gates; 3s fast delay; sr1 50uV; window-qualified onset from run6'})
s=sweep.AsyncStation(mc_fan)
s.add_comment('landau-fan-vti')
s.add_comment('n=3.2->2.8e12 cm^-2 (11), D=0 V/nm via run5 CAL; B=1.0176178808->6.47 T (233 uniform-1/B); Si=0 V; I_bias=10 nA; sr1 50 uV; fast_delay=3 s; slow_delay=1 s; checkpoints rows 1-3 then every 30 min; ends at 6.47 T')
# Keep raw readback distinct from the slow-axis setpoint column.
B_readback_fan=qcodes.Parameter('B_readback_fan',unit='T',get_cmd=magnet.field)
# Row: time, B_set, Vtg, Vbg, Ts, Tv, Itg, Ibg, sr0X, sr0P, sr1X, sr1P, B_read.
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,B_readback_fan):
    s.fp(_p)
    s.plot('time',_p)

# Point guards retain the session's existing 1 nA leakage trip; they stop acquisition,
# never alter safety limits or attempt a magnet abort. Re-read actual state after a trip.
_fan_trip=[]
_fan_guard_count=0

def fan_guard(station,data):
    global _fan_guard_count
    _fan_guard_count+=1
    vals=np.asarray(data[4:],dtype=float)
    reasons=[]
    if not np.isfinite(vals).all(): reasons.append('nonfinite read')
    if not (1.0<=data[4]<=1.5 and 0<data[5]<1.6 and abs(data[4]-data[5])<.6): reasons.append('base temperature')
    if max(abs(data[6]),abs(data[7]))>1e-9: reasons.append('gate leakage >1nA')
    if abs(data[10])>.9*50e-6: reasons.append('sr1 near full scale')
    if not 5e-9 < data[8]/-1e6 < 15e-9: reasons.append('drain current')
    if abs(data[12]-data[1])>.03: reasons.append('field readback mismatch')
    if (_fan_guard_count-1)%len(ns_fan)==0:
        try:
            for name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        except Exception as exc:
            reasons.append('stale thermometry: '+str(exc))
    if reasons:
        _fan_trip.extend(reasons)
        print('FAN STOP:',reasons,'B set/read',data[1],data[12])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())

# From handoff zero: positioning 1.0176/0.137≈7.43 min; whole 0->6.47 T ≈47.23 min.
# Blocking field set supplies its own settle. No blind return traverse.
s.ramp(k_bg.volt,float(Vbgs_fan[0]));s.ramp(k_tg.volt,float(Vtgs_fan[0]))
interruptible_sleep(3)
s.ramp(magnet.field,float(B_fan[0]))
# Fresh reads after positioning before the first acquired row.
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
assert 1.0<=T_sample()<=1.5 and abs(magnet.field()-B_fan[0])<.03
fan_result=s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vtgs_fan,Vbgs_fan],slow_delay=1.,fast_delay=3.)
print('Fan finished/interrupted:',fan_result.metadata.get('interrupted'),'; guard reasons:',_fan_trip)
print('Actual held state: B, TG, BG, Ts =',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample())
# Hold endpoint for the next measured return or explicit close-out decision.
