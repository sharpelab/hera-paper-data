# landau-fan-vti: electron-side D=0, calibrated to ridge A of run 5.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preflight: committed safety surfaces must equal the device card.
for _p, _expected in [(k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                       (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                       (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                       (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(f'{_p.full_name}: expected validator {_expected}, actual {_actual}')
    assert _actual == _expected
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B = T_sample(),T_vaporizer(),magnet.field()
_ranges=(heater.sample_range(),heater.vaporizer_range())
_ps=(magnet.persistent_switch_on(),magnet.output_enabled())
_si=(dc205.voltage_range(),dc205.output(),k_si(),dc205.ramp_rate)
print(f'Expected base: Ts 1.0..1.5 K, Tv<1.6 K, |Tv-Ts|<0.6 K, ranges (0,0); actual {_Ts}, {_Tv}, {_ranges}')
print(f'Expected |B|<0.05 T, PS/output on; actual {_B}, {_ps}; Si expected RNGE2/on/0V/0.5V/s; actual {_si}')
assert 1.0<=_Ts<=1.5 and 0<_Tv<1.6 and abs(_Tv-_Ts)<0.6 and _ranges==(0,0)
assert abs(_B)<0.05 and all(_ps)
assert _si[0]==2 and _si[1]==1 and abs(_si[2])<0.01 and _si[3]==0.5
_tau=(sr0.time_constant(),sr1.time_constant())
_slopes=(sr0.filter_slope(),sr1.filter_slope())
_drive=(sr1.amplitude(),sr1.frequency())
_pacing=(k_tg.volt.step,k_bg.volt.step)
_nplc=(k_tg.nplci(),k_bg.nplci())
print(f'Expected tau (.3,.3), slopes (24,24), drive (1 V,13.777 Hz), gate steps (.005,.005), NPLC (1,1); actual {_tau}, {_slopes}, {_drive}, {_pacing}, {_nplc}')
assert _tau==(.3,.3) and _slopes==(24,24)
assert abs(_drive[0]-1)<1e-6 and abs(_drive[1]-13.777)<.01
assert _pacing==(.005,.005) and _nplc==(1,1)
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'} and 'mux' not in globals()
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

CAL_FAN=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
ns_fan=np.linspace(3.2,2.8,11)
Vtgs_fan,Vbgs_fan=calc_gate_voltages(ns_fan,np.zeros(11),**CAL_FAN)
B_fan=field_invB(1.017617880804576,6.5,239)
for _p,_vals in [(k_tg.volt,Vtgs_fan),(k_bg.volt,Vbgs_fan),(magnet.field,B_fan)]:
    for _v in _vals: _p.validate(float(_v))
_ncheck,_Dcheck=calc_nD(Vtgs_fan,Vbgs_fan,**CAL_FAN)
assert np.allclose(_ncheck,ns_fan) and np.max(np.abs(_Dcheck))<1e-10
print(f'Fan: {len(B_fan)} x {len(ns_fan)}; B {B_fan[0]:.6f}->{B_fan[-1]:.3f} T; TG {Vtgs_fan.min():.6f}..{Vtgs_fan.max():.6f}, BG {Vbgs_fan.min():.6f}..{Vbgs_fan.max():.6f} V')
print(f'Bare ramp total from actual {_B:+.4f} T: {(6.5-_B)*7.3:.1f} min; first row positioning {(B_fan[0]-_B)*7.3:.1f} min. No extra field traverse.')
# Acquisition settings only; validators, driver step, ramp_rate, and heaters untouched.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6 and sr0.sensitivity()==.02
mc_fan=dict(meas_config)
mc_fan.update({'Si (V)':_si[2],'sample_temperature:':_Ts,'calibration':CAL_FAN,
               'n_vector_1e12_cm2':ns_fan.tolist(),'D_V_nm':0.,'settling_s':3.,
               'comments':'D0 electron fan; ridge-A run5 calibration; n 3.2->2.8, B 1.017618->6.5 T; 239x11; sr1 50uV, 10nA, tau0.3s/24dB, dwell3s; no contact rerouting'})
s=sweep.AsyncStation(mc_fan)
s.add_comment('landau-fan-vti')
s.add_comment('tetralayer-stacking-fs-count Step4; n_A=3.2->2.8e12 cm^-2 (11), D_A=0 V/nm; B=1.0176178808->6.5 T (239 uniform-1/B); Si=0 V; B1-B2 Rxx; cal run5 ratio=.773, absolute scale geometry prior; first 3 rows and every 30min checkpoints')
s.ramp(k_bg.volt,float(Vbgs_fan[0])); s.ramp(k_tg.volt,float(Vtgs_fan[0]))
interruptible_sleep(3)
# Every recorded channel is also visible in the live monitor.
# Row: time, B_set, TG_set, BG_set, Ts, Tv, Itg, Ibg, sr0X, sr0P, sr1X, sr1P, B_read.
B_read_fan=qcodes.Parameter('B_read_fan',get_cmd=magnet.field,unit='T')
for _param in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,B_read_fan):
    s.fp(_param)
    s.plot('time',_param)
_fan_guard={'last_fresh':0.0,'reason':None}
def fan_guard(station,data):
    _why=[]
    if not np.all(np.isfinite(np.asarray(data,dtype=float))): _why.append('nonfinite reading')
    if not (1.0<=float(data[4])<=1.5 and 0<float(data[5])<1.6 and abs(float(data[5])-float(data[4]))<.6): _why.append('base temperature mismatch')
    if max(abs(float(data[6])),abs(float(data[7])))>1e-9: _why.append('inherited 1nA gate-current trip')
    if abs(float(data[10]))>=.9*50e-6 or abs(float(data[8]))>=.9*.02: _why.append('lock-in near full scale')
    if not 8e-9<float(data[8])/-1e6<12e-9: _why.append('drain-current mismatch')
    if abs(float(data[12])-float(data[1]))>.03: _why.append('measured field mismatch')
    if time.monotonic()-_fan_guard['last_fresh']>30:
        try:
            for _name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        except Exception as _err: _why.append(str(_err))
        _fan_guard['last_fresh']=time.monotonic()
    if _why:
        _fan_guard['reason']='; '.join(_why)
        print('FAN STOP:',_fan_guard['reason'])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
fan_result=s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vtgs_fan,Vbgs_fan],slow_delay=1,fast_delay=3)
print('Fan run',fan_result.id,'interrupted',fan_result.metadata.get('interrupted'),'guard',_fan_guard['reason'])
print('Actual endpoint:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample(),T_vaporizer())
# Hold endpoint for analysis/next move. Any interruption requires state reread and explicit E1 re-grant after a safety drop.
