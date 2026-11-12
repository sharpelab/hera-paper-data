# landau-fan-vti: first electron D~0 frequency-trajectory fan.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preconditions before every instrument write; SAFETIES are compared,
# never assigned. Same-kernel grant and handoff: measure cells 18, 32, 44, 46.
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_gate_start = (k_tg.volt(), k_bg.volt(), k_si())
print('Expected base sample 1.0–1.5 K, vaporizer <1.6 K and within 0.6 K; field 0±0.05 T; Si 0±0.01 V.')
print('Actual:', _Ts, _Tv, _B, 'gates TG/BG/Si:', _gate_start)
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts)<.6
assert abs(_B)<.05 and abs(_gate_start[2])<.01
print('Heater ranges expected 0/0:', heater.sample_range(), heater.vaporizer_range())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
print('Magnet switch/output expected True/True:', magnet.persistent_switch_on(),magnet.output_enabled())
assert magnet.persistent_switch_on() and magnet.output_enabled()
for _p,_limits in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),
                   (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                   (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                   (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name,'validator expected',_limits,'actual',_actual)
    assert _actual==_limits
assert B_SESSION_CAP==10. and T_SESSION_CAP==100.
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert 'mux' not in globals()
print('Expected step 0.005 V both; NPLC 1 both:',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step==.005 and k_bg.volt.step==.005 and k_tg.nplci()==1 and k_bg.nplci()==1
print('DC205 expected RNGE 2, output 1, rate 0.5 V/s:',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
for _li in (sr0,sr1):
    print(_li.name,'expected tau 0.3 s / slope 24:',_li.time_constant(),_li.filter_slope())
    assert _li.time_constant()==.3 and _li.filter_slope()==24
print('Expected drive 1 V / 13.777 Hz, sr0 sens 0.02 V:',sr1.amplitude(),sr1.frequency(),sr0.sensitivity())
assert abs(sr1.amplitude()-1.)<1e-6 and abs(sr1.frequency()-13.777)<.01 and sr0.sensitivity()==.02
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
print('Magnet settle expected >=3 s:',magnet.settle_s)
assert magnet.settle_s>=3

# Same rounded calibration as spot run 6: exact shared-density comparison.
CAL_FAN=dict(c_tg=2.796e-3,c_bg=2.161e-3,n_offset=-.0894,D_offset=-.013)
ns_fan=np.linspace(3.2,2.8,13)
Vtgs_fan,Vbgs_fan=calc_gate_voltages(ns_fan,np.zeros(len(ns_fan)),**CAL_FAN)
B_fan=field_invB(.90,5.20,167)
for _p,_values in [(k_tg.volt,Vtgs_fan),(k_bg.volt,Vbgs_fan),(magnet.field,B_fan)]:
    for _v in _values: _p.validate(float(_v))
_nr,_dr=calc_nD(Vtgs_fan,Vbgs_fan,**CAL_FAN)
assert np.allclose(_nr,ns_fan) and np.allclose(_dr,0,atol=1e-10)
print('Fan:',len(B_fan),'B rows x',len(ns_fan),'n; gates:',Vtgs_fan[[0,-1]],Vbgs_fan[[0,-1]])
print('Field from actual',_B,'to 5.2 T: bare ramp floor',abs(5.2-_B)/.137,'min; no return ramp.')

sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
mc=dict(meas_config)
mc.update({'Si (V)':_gate_start[2], 'sample_temperature:':_Ts,
           'gate_calibration':CAL_FAN,'density_units':'1e12 cm^-2',
           'n_setpoints':ns_fan.tolist(),'D_setpoint_V_per_nm':0.,
           'sr0_tau_s':.3,'sr1_tau_s':.3,'filter_slope_dB':24,
           'comments':'landau-fan-vti; B1-B2; n_A 3.2->2.8e12 at D_A=0; B 0.90->5.20 T, 167 uniform-1/B rows x 13 n; 3 s gate dwell; sr1 50 uV; run-5 calibration, run-6 shared density'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('n_A=3.2..2.8e12 cm^-2 (13 paired TG/BG points), D_A=0 V/nm; B=0.90..5.20 T (167 uniform-1/B rows); base T; Si=0 V; 10 nA drive; sr1=50 uV; fast dwell=3 s; slow delay=1 s; calibrated from run 5, compared to run 6; region B unresolved')
# Field axis in sweep metadata is commanded; separately record actual field.
B_fan_read=qcodes.Parameter('B_fan_read',unit='T',get_cmd=magnet.field)
_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,B_fan_read]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)
# Columns: time, commanded B, TG, BG, followed channels in this order.
_fan_col={p.full_name:4+i for i,p in enumerate(_follow)}
_fan_guard_state={'last_fresh':0.}

def fan_before(station):
    # Timestamp/period freshness check during acquisition, not just at launch.
    if time.time()-_fan_guard_state['last_fresh']>=30:
        for name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        _fan_guard_state['last_fresh']=time.time()

def fan_after(station,data):
    vals={p.full_name:float(data[_fan_col[p.full_name]]) for p in _follow}
    reasons=[]
    if not all(np.isfinite(v) for v in vals.values()): reasons.append('nonfinite read')
    if max(abs(vals[k_tg.curr.full_name]),abs(vals[k_bg.curr.full_name]))>1e-9: reasons.append('gate leakage >1 nA')
    if not 1.0<=vals[T_sample.full_name]<=1.5: reasons.append('sample outside base window')
    if not 0<vals[T_vaporizer.full_name]<1.6: reasons.append('vaporizer outside base window')
    if abs(vals[sr1.X.full_name])>.85*50e-6: reasons.append('Rxx nearing full scale')
    if abs(vals[sr0.X.full_name])>.85*.02: reasons.append('current channel nearing full scale')
    if not 8e-9<vals[sr0.X.full_name]/(-1e6)<12e-9: reasons.append('drain current outside 8–12 nA')
    if abs(vals[B_fan_read.full_name]-float(data[1]))>.03: reasons.append('field readback mismatch')
    if reasons:
        print('FAN STOP:',', '.join(reasons),'B/TG/BG',data[1:4])
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())

# No Si or heater writes. Gate pacing remains operator-owned and unchanged.
s.ramp(k_bg.volt,float(Vbgs_fan[0])); s.ramp(k_tg.volt,float(Vtgs_fan[0]))
interruptible_sleep(10)
# First blocking field set is inside the data-writing sweep: watcher sees the
# run before the ~6.6 min initial positioning ramp. End at 5.2 T for next step.
fan_result=s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],
                           [Vtgs_fan,Vbgs_fan],slow_delay=1,fast_delay=3)
print('Fan returned; actual field/gates/T:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample())
print('Read metadata interrupted status before continuing. Instruments hold; no automatic park.')
