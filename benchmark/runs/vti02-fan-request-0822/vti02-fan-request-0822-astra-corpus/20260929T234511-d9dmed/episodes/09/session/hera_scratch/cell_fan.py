# landau-fan-vti: stacking discrimination on sr1 / B_1-B_2.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
import time as _fan_time
from pathlib import Path as _FanPath

# Inherited-state preflight: read and print before any instrument write.
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B = T_sample(),T_vaporizer(),magnet.field()
_ps,_out=magnet.persistent_switch_on(),magnet.output_enabled()
_ranges=(heater.sample_range(),heater.vaporizer_range())
_si,_rng,_sout=dc205.voltage(),dc205.voltage_range(),dc205.output()
print(f'Expected base T 1.0–1.5 K, vaporizer <1.6 K, B~0 (+/-0.02 T), heaters off, PS/output on; actual {_Ts}, {_Tv}, {_B}, {_ranges}, {_ps}/{_out}')
print(f'Expected Si 0 V, RNGE 2, output 1, pacing 0.5 V/s; actual {_si}, {_rng}, {_sout}, {dc205.ramp_rate}')
assert 1.0<=_Ts<=1.5 and 0<_Tv<1.6 and abs(_Ts-_Tv)<0.6
assert abs(_B)<0.02 and _ranges==(0,0) and _ps and _out
assert abs(_si)<0.01 and _rng==2 and _sout==1 and dc205.ramp_rate==0.5
# Gate B: numerical equality with card, including raw Si and both T guards.
for _p,_expected in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),
                     (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                     (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                     (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(_p.vals._min_value,_p.vals._max_value)
    print(f'{_p.full_name}: expected validator {_expected}; actual {_actual}')
    assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print(f'Expected drive 1 V/13.777 Hz; actual {sr1.amplitude()}/{sr1.frequency()}; expected sr0 sens .02 V, actual {sr0.sensitivity()}')
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<.01 and sr0.sensitivity()==.02
for _li in (sr0,sr1):
    _tau,_slope=_li.time_constant(),_li.filter_slope()
    print(f'{_li.name}: expected tau .3 s / slope 24 dB, actual {_tau}/{_slope}')
    assert _tau==.3 and _slope==24
for _k in (k_tg,k_bg):
    print(f'{_k.name}: expected NPLC 1, ramp step .005 V; actual {_k.nplci()}/{_k.volt.step}')
    assert _k.nplci()==1 and _k.volt.step==.005
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
print(f'Actual starting gates: TG {k_tg.volt():+.5f} V, BG {k_bg.volt():+.5f} V; explicitly positioned below')

# Same rounded calibration as spot run 6, so n=3.2 is an exact acquisition comparison.
FAN_CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
ns=np.linspace(3.2,2.8,11)
Vtgs,Vbgs=calc_gate_voltages(ns,np.zeros_like(ns),**FAN_CAL)
B_vec=field_invB(1.017617880804576,6.4689868523317715,101)
assert np.all((Vtgs>=-.3)&(Vtgs<=1)) and np.all((Vbgs>=-1.3)&(Vbgs<=2))
_nn,_dd=calc_nD(Vtgs,Vbgs,**FAN_CAL)
assert np.allclose(_nn,ns) and np.max(np.abs(_dd))<1e-10
assert np.all(np.diff(B_vec)>0) and B_vec[-1]<=10
assert np.max(np.abs(np.diff(1/B_vec)))<=1/120
assert np.max(np.abs(np.diff(ns)))*1.2<=4*1.602176634e-19/6.62607015e-34*B_vec[0]/1e16/2
FAST_DELAY,SLOW_DELAY=3.0,1.0  # 10 tau for each newly set gate point.
# Same sensitivity as spot checks; 5 kOhm FS vs spot max 530 Ohm.
sr1.sensitivity(50e-6)
print(f'Fan: {len(B_vec)} x {len(ns)}; TG {Vtgs.min():.6f}..{Vtgs.max():.6f}, BG {Vbgs.min():.6f}..{Vbgs.max():.6f}; sr1 FS {sr1.sensitivity()/1e-8:.0f} Ohm')
mc=dict(meas_config)
mc.update({'Si (V)':_si,'sample_temperature:':_Ts,'gate_calibration':FAN_CAL,
           'comments':'D=0 nominal ridge A; n=2.8..3.2e12; B=1.017618..6.468987 T uniform inverse B; 101x11; sr1 B_1-B_2; run6 shared n=3.2; onset provisional local-fit 1.018 T; scale geometry prior',
           'fan_design':{'ns_1e12':ns.tolist(),'fast_delay_s':3.0,'sr0_tau_s':.3,'sr1_tau_s':.3,'filter_slope_dB':24,'sr1_sensitivity_V':50e-6}})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(mc['comments'])
# Initial 0->1.0176 T is 7.43 min at .137 T/min; total 0->6.469 is 47.22 min.
s.ramp(k_tg.volt,Vtgs[0]);s.ramp(k_bg.volt,Vbgs[0])
s.ramp(magnet.field,float(B_vec[0]))
interruptible_sleep(3)
# Data: time, B_set, TG_set, BG_set, Ts, Tv, Itg, Ibg, sr0X, sr0P, sr1X, sr1P, B_read.
_fan_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field]
for _p in _fan_follow:
    s.fp(_p);s.plot('time',_p)
# Carry the existing 1 nA leakage stop and check freshness/rail/T during acquisition.
# No validator, operating-limit, driver-step or ramp-rate changes.
_fan_paths={}
for _name in ('T_sample','T_vaporizer'):
    _choices=[_FanPath(p) for p in VTI.temp_logfile_candidates[_name] if _FanPath(p).exists()]
    assert _choices, f'No thermometry log for {_name}'
    _fan_paths[_name]=max(_choices,key=lambda p:p.stat().st_mtime)
fan_stop_reasons=[]
def fan_guard(station,data):
    reasons=[]
    vals=np.asarray(data,dtype=float)
    if not np.all(np.isfinite(vals)): reasons.append('nonfinite data')
    if abs(data[6])>1e-9 or abs(data[7])>1e-9: reasons.append('gate leakage >1 nA')
    if not 1.0<=data[4]<=1.5 or not 0<data[5]<1.6: reasons.append('temperature outside base window')
    if abs(data[8])>=.9*.02 or abs(data[10])>=.9*50e-6: reasons.append('lock-in near full scale')
    if not 8e-9< data[8]/-1e6 <12e-9: reasons.append('drain current outside 8–12 nA')
    if abs(data[12]-data[1])>.03: reasons.append('field readback mismatch >30 mT')
    for name,path in _fan_paths.items():
        if _fan_time.time()-path.stat().st_mtime>15: reasons.append(name+' stale >15 s')
    if reasons:
        fan_stop_reasons.extend(reasons)
        print('FAN STOP',reasons,'B,TG,BG=',data[1:4])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
fan_result=s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=SLOW_DELAY,fast_delay=FAST_DELAY)
print('Fan exit: stop reasons',fan_stop_reasons)
print(f'Actual endpoint B {magnet.field():.5f} T, TG {k_tg.volt():.5f} V, BG {k_bg.volt():.5f} V')
# Hold endpoint for the next decision. No automatic field return or writes after an abort.
