# landau-fan-vti: D=0, n=2.8..3.2e12 cm^-2, B=1.031..7.1 T
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preconditions before any hardware write.
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B0, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
print(f'Expected base Ts 1.0..1.5 K/Tv<1.6 K, B=0±0.05 T, Si=0±0.01 V; actual {_Ts}, {_Tv}, {_B0}, {_Si}')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts)<0.6
assert abs(_B0)<0.05 and abs(_Si)<0.01
print('Expected heater ranges 0/0, PS/output on:', heater.sample_range(), heater.vaporizer_range(), magnet.persistent_switch_on(), magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for _p, _bounds in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name, 'expected',_bounds,'actual',_actual)
    assert _actual==_bounds
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
print('Expected DC205 range/output/rate 2/1/0.5:',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
print('Expected drive 1 V/13.777 Hz; actual',sr1.amplitude(),sr1.frequency())
assert abs(sr1.amplitude()-1)<1e-6 and abs(sr1.frequency()-13.777)<0.01
for _li in (sr0,sr1):
    print(_li.name,'expected tau/slope 0.3/24; actual',_li.time_constant(),_li.filter_slope())
    assert _li.time_constant()==0.3 and _li.filter_slope()==24
for _gate in (k_tg,k_bg):
    print(_gate.name,'expected step/NPLC .005/1; actual',_gate.volt.step,_gate.nplci())
    assert _gate.volt.step==0.005 and _gate.nplci()==1
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6
assert WIRING['sr1+']=='B_1' and WIRING['sr1-']=='B_2'

# Run-5 calibration, exact persisted numbers; no changes to safety surfaces.
fan_cal=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,
             n_offset=-0.08937933224099137,D_offset=-0.013)
ns=np.linspace(2.8,3.2,11); Ds=np.zeros_like(ns)
Vtgs,Vbgs=calc_gate_voltages(ns,Ds,**fan_cal)
B_vec=field_invB(1.031,7.1,76)
for _p,_vec in [(k_tg.volt,Vtgs),(k_bg.volt,Vbgs),(magnet.field,B_vec)]:
    for _v in _vec: _p.validate(float(_v))
_ncheck,_dcheck=calc_nD(Vtgs,Vbgs,**fan_cal)
assert np.allclose(_ncheck,ns) and np.allclose(_dcheck,0)
print('Fan:',len(B_vec),'B rows x',len(ns),'densities; gates',Vtgs[[0,-1]],Vbgs[[0,-1]])
print('Positioning+fan bare ramp minutes:',(B_vec[-1]-_B0)/0.137)
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
assert sr0.sensitivity()==0.02
mc=dict(meas_config)
mc.update({'Si (V)':_Si,'sample_temperature:':_Ts,'gate_calibration':fan_cal,
           'fan_n_1e12':ns.tolist(),'fan_D_Vnm':0.,'sr1_gain':1.,
           'comments':'landau-fan-vti; B_1-B_2; n 2.8..3.2e12 D=0 run5 calibration; B 1.031..7.1 T uniform 1/B 76x11; fast_delay=3 s; 50 uV; Si=0'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,float(Vbgs[0]));s.ramp(k_tg.volt,float(Vtgs[0]))
interruptible_sleep(3)
# The sweep itself positions from the measured field to the first B row.
# Layout: time,B,Vtg,Vbg,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P.
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(_p)
    s.plot('time',_p)
fan_guard={'row':None,'reason':None}
def fan_before(station):
    # Freshness each point: logfile-only; no LS335 polling.
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        for name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
def fan_after(station,data):
    vals=np.asarray(data,dtype=float)
    reasons=[]
    if not np.all(np.isfinite(vals)): reasons.append('nonfinite data')
    if max(abs(vals[6]),abs(vals[7]))>1e-9: reasons.append('gate leakage >1 nA')
    if not (1.0<=vals[4]<=1.5 and 0<vals[5]<1.6): reasons.append('temperature outside base window')
    if not 8e-9<=vals[8]/-1e6<=11e-9: reasons.append('drain current outside 8..11 nA')
    if abs(vals[10])>0.9*50e-6 or abs(vals[8])>0.9*0.02: reasons.append('lock-in rail headroom')
    if fan_guard['row']!=vals[1]:
        fan_guard['row']=vals[1]
        actual_B=magnet.field()
        print(f'ROW field expected {vals[1]:.5f} T, measured {actual_B:.5f} T')
        if abs(actual_B-vals[1])>0.05: reasons.append('field readback mismatch')
    if reasons:
        fan_guard['reason']='; '.join(reasons)
        print('FAN STOP:',fan_guard['reason'])
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
fan_result=s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1.,fast_delay=3.)
print('Final actual B/Tg/Bg/Ts/Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample(),T_vaporizer())
print('FAN RESULT:',fan_result,'guard:',fan_guard)
