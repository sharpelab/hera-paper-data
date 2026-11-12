# landau-fan-vti: hole-side frequency trajectories, B1-B2, D~0 (run-5 calibration)
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preconditions BEFORE any write. SAFETIES remain operator-owned.
for _p, _bounds in [(k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                     (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                     (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                     (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(f'{_p.full_name}: validator expected {_bounds}, actual {_actual}')
    assert _actual == _bounds
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ['T_sample','T_vaporizer']:
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_T,_Tv,_B,_Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
print(f'Expected base T 1.0-1.5 K, vaporizer <1.6 K and within 0.6 K, |B|<0.02 T, Si=0 V; actual {_T}, {_Tv}, {_B}, {_Si}')
assert 1.0<=_T<=1.5 and 0<_Tv<1.6 and abs(_Tv-_T)<0.6 and abs(_B)<0.02 and abs(_Si)<0.01
print('Expected heaters off, PS and magnet output on:',heater.sample_range(),heater.vaporizer_range(),magnet.persistent_switch_on(),magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
print('Expected DC205 RNGE 2, output 1, ramp_rate 0.5:',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print('Expected drive 1 V / 13.777 Hz:',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1.)<0.001 and abs(sr1.frequency()-13.777)<0.001
for _sr in [sr0,sr1]:
    print(_sr.name,'expected tau=0.3 s, slope=24:',_sr.time_constant(),_sr.filter_slope())
    assert _sr.time_constant()==0.3 and _sr.filter_slope()==24
print('Expected gate step 0.005 V / NPLC 1:',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005 and k_tg.nplci()==1 and k_bg.nplci()==1
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

CAL_FAN=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,n_offset=-0.08937933224099137,D_offset=-0.013)
ns_fan=np.linspace(-1.2,-0.95,10)
B_fan=field_invB(0.7138767261704282,6.0,75)
Vt_fan,Vb_fan=calc_gate_voltages(ns_fan,np.zeros(10),**CAL_FAN)
for _p,_vs in [(k_tg.volt,Vt_fan),(k_bg.volt,Vb_fan),(magnet.field,B_fan)]:
    for _v in _vs: _p.validate(float(_v))
_ncheck,_dcheck=calc_nD(Vt_fan,Vb_fan,**CAL_FAN)
assert np.allclose(_ncheck,ns_fan) and np.max(np.abs(_dcheck))<1e-10
assert np.max(np.abs(np.diff(1/B_fan)))<=1/(2*2*1.2*1.2*10.33916924)
assert np.max(np.diff(ns_fan))*1.2<=B_fan[0]/10.33916924/2
print('Plan: 75 B rows x 10 densities; voltage endpoints:',Vt_fan[[0,-1]],Vb_fan[[0,-1]])
print('Bare field traverse from readback to 6 T:',abs(6-_B)/0.137,'min; holds at 6 T on completion')

# Fixed sensitivities: 2 kohm voltage range, 20 nA current range. No auto-ranging.
sr1.sensitivity(20e-6)
sr0.sensitivity(20e-3)
mc=dict(meas_config)
mc.update({'Si (V)':_Si,'sample_temperature:':_T,'calibration':CAL_FAN,
           'n_vector_1e12_cm2':ns_fan.tolist(),'D_Vnm':0.0,'settle_s_per_point':3.0,
           'sr1_tau_s':0.3,'sr1_slope_dB':24,'sr1_gain':1,
           'comments':'landau-fan-vti; B1-B2; holes n -1.20:-0.95e12, D~0 ridge A; B 0.7138767:6 T uniform inverse-B 75 x 10; Si 0; 10 nA; 3 s dwell; sr1 20 uV; run-5 calibration'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(mc['comments'])
# Gates retain their committed pacing; Si never moved. First B row performs positioning.
s.ramp(k_bg.volt,float(Vb_fan[0]));s.ramp(k_tg.volt,float(Vt_fan[0]))
interruptible_sleep(3)
# columns: time, B_set, Vtg_set, Vbg_set, Ts, Tv, Itg, Ibg, I_X, I_P, V_X, V_P
_channels=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]
for _p in _channels:
    s.fp(_p)
    s.plot('time',_p)
_guard={'points':0,'trips':[]}

def fan_before(station):
    # Use interruptible settling after the paired gate set (10 tau); no bare 3-s sleep.
    interruptible_sleep(3.0)
    if _guard['points']%10==0:
        for _name in ['T_sample','T_vaporizer']:
            assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)

def fan_after(station,data):
    _a=np.asarray(data,dtype=float)
    _problems=[]
    if not np.all(np.isfinite(_a)): _problems.append('nonfinite readback')
    if not (1.0<=_a[4]<=1.5 and 0<_a[5]<1.6 and abs(_a[4]-_a[5])<0.6): _problems.append('base temperature')
    if max(abs(_a[6]),abs(_a[7]))>1e-9: _problems.append('gate leakage >1 nA')
    if abs(_a[8])>=0.9*20e-3 or abs(_a[10])>=0.9*20e-6: _problems.append('90% full-scale headroom')
    if not 8e-9<=_a[8]/(-1e6)<=12e-9: _problems.append('drain current outside 8-12 nA')
    if _guard['points']%10==0:
        _bread=magnet.field()
        print(f'Row {_guard["points"]//10+1}/75: B expected {_a[1]:.5f}, measured {_bread:.5f} T')
        if abs(_bread-_a[1])>0.02: _problems.append('field readback mismatch')
    _guard['points']+=1
    if _problems:
        _guard['trips'].extend(_problems)
        print('FAN STOP:',_problems,'at B',_a[1])
        station.interrupt_requested=True

s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vt_fan,Vb_fan],slow_delay=0,fast_delay=0)
print('Post-run actual B,T,Tv,gates,Si:',magnet.field(),T_sample(),T_vaporizer(),k_tg.volt(),k_bg.volt(),k_si())
assert not _guard['trips'] and _guard['points']==750, f'Incomplete fan: {_guard}; re-read state before any move'
print('FAN COMPLETE: 750 points; hold B=6 T and final density for analysis-directed next step')
