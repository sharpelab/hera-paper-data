# landau-fan-vti: electron D_A=0 fan, design from runs 5-7.
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preflight: no hardware writes until every inherited-state check passes.
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_ts, _tv, _b = T_sample(), T_vaporizer(), magnet.field()
_si = k_si()
print(f'Expected base 1.0-1.5 K, vaporizer <1.6 K, B=0 +/-0.02 T, Si=0 +/-0.01 V; actual {_ts=}, {_tv=}, {_b=}, {_si=}')
assert 1.0 <= _ts <= 1.5 and 0 < _tv < 1.6 and abs(_tv-_ts)<0.6
assert abs(_b)<0.02 and abs(_si)<0.01
print('Expected heaters off, PS and magnet output on:', heater.sample_range(), heater.vaporizer_range(), magnet.persistent_switch_on(), magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for _p, _limits in ((k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))):
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name,'validator expected',_limits,'actual',_actual)
    assert _actual==_limits
assert B_SESSION_CAP==10.0 and T_SESSION_CAP==100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected drive 1 V / 100 MOhm at 13.777 Hz; actual',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1.0)<1e-6 and abs(sr1.frequency()-13.777)<0.01
assert meas_config['bias_resistor']==100e6 and meas_config['sr0_gain']==-1e6
print('Expected DC205 range 2, output on, pacing 0.5 V/s:',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
for _k in (k_tg,k_bg):
    print(_k.name,'expected step 0.005 V, NPLC 1:',_k.volt.step,_k.nplci())
    assert _k.volt.step==0.005 and _k.nplci()==1
for _sr in (sr0,sr1):
    print(_sr.name,'expected tau 0.3 s, slope 24 dB:',_sr.time_constant(),_sr.filter_slope())
    assert _sr.time_constant()==0.3 and _sr.filter_slope()==24
assert sr0.sensitivity()==0.02

# Run-5 calibration; ratio data-calibrated, absolute scale geometry-prior.
FAN_CAL=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,
             n_offset=-0.08937933224099137,D_offset=-0.013)
ns=np.linspace(3.2,2.8,11)
Vtgs,Vbgs=calc_gate_voltages(ns,np.zeros_like(ns),**FAN_CAL)
B_vec=field_invB(1.0309096913954,7.05,218)
assert np.all((Vtgs>=TG_MIN)&(Vtgs<=TG_MAX)) and np.all((Vbgs>=BG_MIN)&(Vbgs<=BG_MAX))
assert np.all((B_vec>0)&(B_vec<=B_SESSION_CAP))
_nr,_dr=calc_nD(Vtgs,Vbgs,**FAN_CAL)
assert np.allclose(_nr,ns) and np.max(np.abs(_dr))<1e-12
assert np.max(np.abs(np.diff(1/B_vec))) <= 1/(2*131)
print('Fan: 218 B rows x 11 densities; gates',Vtgs[[0,-1]],Vbgs[[0,-1]],'B',B_vec[[0,-1]])

# Restore the empirically validated spot-check sensitivity; fixed through the fan.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
mc=dict(meas_config)
mc.update({'Si (V)':_si,'sample_temperature:':_ts,'calibration':FAN_CAL,
           'n_units':'1e12 cm^-2','n_setpoints':ns.tolist(),'D_V_per_nm':0.0,
           'sr0_tau_s':0.3,'sr1_tau_s':0.3,'filter_slope_dB':24,
           'comments':'landau-fan-vti: B 1.0309096914 -> 7.05 T, 218 uniform-in-1/B rows; n_A +3.2 -> +2.8e12, 11 paired points; D_A=0; Si=0; base; 10 nA; 3 s fast dwell; run-5 calibration'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,float(Vbgs[0])); s.ramp(k_tg.volt,float(Vtgs[0]))
interruptible_sleep(3)
# First field move occurs inside multimegasweep, after the run directory opens.
# 0 -> 1.031 T positioning: 7.53 min; total 0 -> 7.05 T: 51.47 min bare ramp.
# Columns: time, Bset, TGset, BGset, Ts, Tv, Itg, Ibg, I.X, I.P, V.X, V.P, Bactual.
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(magnet.field)
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field):
    s.plot('time',_p)

_fan_state={'points':0,'trip':None}
def _fan_before(station):
    if _fan_state['points'] % len(ns)==0:
        for _name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)

def _fan_after(station,data):
    a=np.asarray(data,dtype=float)
    _fan_state['points']+=1
    why=[]
    if not np.all(np.isfinite(a)): why.append('nonfinite read')
    if not 1.0<=a[4]<=1.5 or not 0<a[5]<1.6: why.append('temperature off base')
    if max(abs(a[6]),abs(a[7]))>1e-9: why.append('gate current >1 nA')
    if abs(a[10])>=0.8*50e-6 or abs(a[8])>=0.8*0.02: why.append('lock-in headroom <20%')
    if not 8e-9<=a[8]/(-1e6)<=12e-9: why.append('drain current outside 8-12 nA')
    if abs(a[12]-a[1])>0.03: why.append('field readback mismatch >30 mT')
    if why:
        _fan_state['trip']='; '.join(why)
        print('FAN STOP',_fan_state['trip'],'at',a[:4])
        station.interrupt_requested=True
s.register_run_before(_fan_before,())
s.register_run_after(_fan_after,())
try:
    fan_result=s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],
                               [Vtgs,Vbgs],slow_delay=1,fast_delay=3.0)
finally:
    print('Actual final B,T,TG,BG,Si:',magnet.field(),T_sample(),k_tg.volt(),k_bg.volt(),k_si())
print('FAN STOP: '+_fan_state['trip'] if _fan_state['trip'] else 'FAN cell returned; consult run metadata for completeness')
# Hold endpoints for the next decision. No blind field return, no safety edits.
