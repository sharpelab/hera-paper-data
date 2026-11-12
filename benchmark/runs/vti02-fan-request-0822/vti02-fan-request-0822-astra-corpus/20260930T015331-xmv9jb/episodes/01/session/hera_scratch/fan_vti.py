# landau-fan-vti: compact electron D=0 frequency-trajectory fan, runs 5/6 calibration.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preflight; compare committed SAFETIES numerically, never modify them.
for _p, _limits in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(_p.vals.min_value,_p.vals.max_value)
    print(f'SAFETIES {_p.full_name}: expected {_limits}, actual {_actual}')
    assert _actual == _limits
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
for _name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B0,_Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
_ranges=(heater.sample_range(),heater.vaporizer_range())
_PS,_out=magnet.persistent_switch_on(),magnet.output_enabled()
print(f'Expected base T 1.0-1.5 K, vaporizer within 0.5 K, B~0, Si=0, heaters off, PS/output on; actual {_Ts}, {_Tv}, {_B0}, {_Si}, {_ranges}, {_PS}/{_out}')
assert 1.0<=_Ts<=1.5 and abs(_Tv-_Ts)<0.5 and abs(_B0)<0.05 and abs(_Si)<0.01
assert _ranges==(0,0) and _PS and _out
print('Expected DC205 RNGE=2/output=1/rate=0.5; actual',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
print('Expected gate step=0.005, NPLC=1; actual',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005 and k_tg.nplci()==1 and k_bg.nplci()==1
print('Expected sr1 drive 1 V/13.777 Hz, sr0/sr1 tau .3 s, slopes 24, sr0 sens .02 V; actual',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope(),sr0.sensitivity())
assert abs(sr1.amplitude()-1.)<1e-6 and abs(sr1.frequency()-13.777)<0.001
assert sr0.time_constant()==sr1.time_constant()==0.3 and sr0.filter_slope()==sr1.filter_slope()==24
assert sr0.sensitivity()==0.02
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}

# Same rounded run-6 calibration keeps the +3.2e12 column exactly comparable.
FAN_CAL=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-0.0894,D_offset=-0.013)
ns=np.linspace(2.8,3.2,11); Ds=np.zeros_like(ns)
Vtgs,Vbgs=calc_gate_voltages(ns,Ds,**FAN_CAL)
B_vec=field_invB(1.017617880804576,6.5,101)
assert np.all(np.diff(B_vec)>0)
for _p,_vec in [(k_tg.volt,Vtgs),(k_bg.volt,Vbgs),(magnet.field,B_vec)]:
    for _v in _vec: _p.validate(float(_v))
_ncheck,_Dcheck=calc_nD(Vtgs,Vbgs,**FAN_CAL)
assert np.allclose(_ncheck,ns) and np.allclose(_Dcheck,0,atol=1e-12)
assert np.max(np.abs(np.diff(1/B_vec))) <= 1/(2*60)
assert np.max(np.diff(ns))*1.2 <= (4*cst.e/cst.h)*B_vec[0]/1e16/2
print('Fan: 101 B x 11 n, gate endpoints',Vtgs[[0,-1]],Vbgs[[0,-1]],'B',B_vec[[0,-1]])

# 50 uV -> 5 kohm FS, identical to spot check; 3 s gate dwell = 10 tau.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
mc=dict(meas_config)
mc.update({'Si (V)':_Si,'sample_temperature:':_Ts,'gate_calibration':FAN_CAL,
           'comments':'landau-fan-vti; n=2.8..3.2e12 (11), D=0 ridge A; B=1.01761788..6.5 T (101 uniform inverse B); fast_delay=3s; sr1=50uV; run6 shared density; base T'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('n=+2.8..+3.2e12 cm^-2 (11); D=0 V/nm ridge-A run5 calibration; B=1.017617880804576 -> 6.5 T (101 uniform 1/B); Si=0; I_bias=10nA; B1-B2; fast_delay=3s; slow_delay=1s; gates parked at 0 after normal completion, field retained 6.5T')
s.ramp(k_bg.volt,float(Vbgs[0]));s.ramp(k_tg.volt,float(Vtgs[0]))
interruptible_sleep(3)
# [time,Bset,Vtg,Vbg,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P,Bactual]
_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)
_fan_guard={'last_fresh':0.,'reason':None}
def fan_guard(station,data):
    _reason=None
    if not np.all(np.isfinite(data)): _reason='nonfinite data'
    elif not 1.0<=data[4]<=1.5 or abs(data[5]-data[4])>=0.5: _reason='temperature outside base precondition'
    elif abs(data[6])>1e-9 or abs(data[7])>1e-9: _reason='existing 1 nA gate-current trip'
    elif abs(data[8])>=0.9*0.02 or abs(data[10])>=0.9*50e-6: _reason='lock-in headroom <10 percent'
    elif not 8e-9 < data[8]/-1e6 < 12e-9: _reason='drain current outside 8-12 nA'
    elif abs(data[12]-data[1])>0.03: _reason='field readback not at row setpoint'
    if time.time()-_fan_guard['last_fresh']>30:
        try:
            for _name in ['T_sample','T_vaporizer']:
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        except Exception as _err: _reason=f'thermometry freshness: {_err}'
        _fan_guard['last_fresh']=time.time()
    if _reason:
        _fan_guard['reason']=_reason
        print('FAN STOP:',_reason,'Bset/actual',data[1],data[12],flush=True)
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
# First slow set includes the 0 -> 1.018 T positioning (~7.4 min); no second traverse.
_fan_result=s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1,fast_delay=3)
if _fan_guard['reason'] or s.interrupt_requested:
    print('FAN INTERRUPTED: hold all state; read actual field/gates before any next move.',_fan_guard['reason'])
else:
    s.ramp(k_tg.volt,0.);s.ramp(k_bg.volt,0.)
print('FAN end actual B/TG/BG/Si/Tsample:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample())
