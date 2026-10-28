# Plan step 4: Landau fan. Preconditions are read-only; no limit/pacing edits.
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Si, _ranges = k_si(), (heater.sample_range(), heater.vaporizer_range())
print(f'Expected base Ts 1.0..1.5 K, Tv<1.6 K, B=0 +/-0.02 T, Si=0 +/-0.01 V, heaters off; actual {_Ts}, {_Tv}, {_B}, {_Si}, {_ranges}')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts)<0.6
assert abs(_B)<0.02 and abs(_Si)<0.01 and _ranges==(0,0)
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print('Expected PS/output on:', _ps, _out)
assert _ps and _out
_expected = [(k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
             (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
             (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
             (heater.vaporizer_setpoint,(0.,100.))]
for _p, _limits in _expected:
    _actual = (float(_p.vals._min_value), float(_p.vals._max_value))
    print(_p.full_name, 'expected validator', _limits, 'actual', _actual)
    assert _actual == _limits
assert B_SESSION_CAP==10.0 and T_SESSION_CAP==100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
_pace = (k_tg.volt.step, k_bg.volt.step, dc205.ramp_rate)
_nplc = (k_tg.nplci(), k_bg.nplci())
_drive = (sr1.amplitude(), sr1.frequency())
_filters = (sr0.time_constant(), sr0.filter_slope(), sr1.time_constant(), sr1.filter_slope())
print('Expected pacing (0.005,0.005,0.5), NPLC (1,1), drive (1 V,13.777 Hz), filters (0.3s,24dB,0.3s,24dB):',_pace,_nplc,_drive,_filters)
assert _pace==(0.005,0.005,0.5) and _nplc==(1,1)
assert abs(_drive[0]-1.0)<1e-6 and abs(_drive[1]-13.777)<0.01
assert _filters==(0.3,24,0.3,24)
assert dc205.voltage_range()==2 and dc205.output()==1
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

# Exact run-5 calibration, SI units. Absolute scale is geometry anchored.
_ct, _cb = 0.0027960593093052633, 0.002160696465377614
_n0, _D0 = -0.08937933224099137e16, -0.013e9
fan_n = np.linspace(-1.2e16, 3.2e16, 111)
_q, _d = cst.e*(fan_n-_n0), 2*cst.epsilon_0*(0.0-_D0)
fan_tg, fan_bg = (_q+_d)/(2*_ct), (_q-_d)/(2*_cb)
fan_B = np.r_[0.,0.5,0.75,1.,1.25,1.5,1.75,field_invB(2.,10.,81)]
assert np.all(np.diff(fan_B)>0) and fan_B[-1]<=B_SESSION_CAP
assert fan_tg.min()>=TG_MIN and fan_tg.max()<=TG_MAX
assert fan_bg.min()>=BG_MIN and fan_bg.max()<=BG_MAX
for _v in fan_tg: k_tg.volt.validate(float(_v))
for _v in fan_bg: k_bg.volt.validate(float(_v))
for _v in fan_B: magnet.field.validate(float(_v))
print(f'Grid {len(fan_B)} x {len(fan_n)} = {len(fan_B)*len(fan_n)}; TG {fan_tg[0]:+.6f}..{fan_tg[-1]:+.6f} V; BG {fan_bg[0]:+.6f}..{fan_bg[-1]:+.6f} V')

# Acquisition range change only; safety validators and all ramp pacing unchanged.
sr1.sensitivity(100e-6)
_sens0, _sens1 = sr0.sensitivity(), sr1.sensitivity()
assert _sens0==0.02 and _sens1==100e-6
_mc = dict(meas_config)
_mc.update({'Si (V)':_Si,'sample_temperature:':_Ts,
    'sr1_gain':1.0,'comments':'landau-fan: B_1-B_2, nominal A D=0; n=-1.2..3.2e12 cm^-2; B=0..10 T ascending; Si=0 V; base T',
    'gate_calibration':{'source_run':5,'c_tg_F_m2':_ct,'c_bg_F_m2':_cb,'n_offset_m2':_n0,'D_offset_V_m':_D0,'absolute_scale':'geometry prior','D_zero':'CNP resistance-minimum proxy'},
    'fan_nominal_n_m2':fan_n.tolist(),'fan_nominal_D_V_m':0.0,
    'lockin_filters':{'sr0_tau_s':_filters[0],'sr0_slope_dB':_filters[1],'sr1_tau_s':_filters[2],'sr1_slope_dB':_filters[3]},
    'sr0_sensitivity':_sens0,'sr1_sensitivity':_sens1})
s = sweep.AsyncStation(_mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B_1-B_2; nominal D=0 V/nm (run5 proxy); n=-1.2..+3.2e12 cm^-2, 111 pts; B sparse 0..1.75 then uniform 1/B 2..10 T,81 rows; TG/BG co-sweep; Si=0 V; dwell=3 s; sr1=100 uV')
# Separate names distinguish actual readbacks from the planned sweep columns.
fan_B_read = qcodes.Parameter('fan_B_read',unit='T',get_cmd=magnet.field)
fan_TG_read = qcodes.Parameter('fan_TG_read',unit='V',get_cmd=k_tg.volt)
fan_BG_read = qcodes.Parameter('fan_BG_read',unit='V',get_cmd=k_bg.volt)
_follow = [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.Y,sr0.P,
           sr1.X,sr1.Y,sr1.P,fan_B_read,fan_TG_read,fan_BG_read,k_si]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)

# Column layout: time,B,TG,BG,Ts,Tv,Itg,Ibg,X0,Y0,P0,X1,Y1,P1,Bactual,TGactual,BGactual,Si.
_fan_count = 0
def fan_before(station, writer):
    if _fan_count % len(fan_n)==0:
        try:
            for _name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        except Exception as exc:
            print('FAN STOP: thermometry freshness',repr(exc))
            station.interrupt_requested=True

def fan_after(station, data):
    global _fan_count
    _fan_count += 1
    a=np.asarray(data,dtype=float)
    problems=[]
    if not np.all(np.isfinite(a)): problems.append('nonfinite readback')
    if max(abs(a[6]),abs(a[7]))>1e-9: problems.append('gate leakage >1 nA')
    if not (1.0<=a[4]<=1.5 and 0<a[5]<1.6 and abs(a[4]-a[5])<0.6): problems.append('temperature outside base window')
    if abs(a[14]-a[1])>0.02: problems.append('field readback mismatch >20 mT')
    if abs(a[15]-a[2])>0.003 or abs(a[16]-a[3])>0.003 or abs(a[17])>0.01: problems.append('gate readback mismatch')
    if np.hypot(a[8],a[9])>=0.9*_sens0 or np.hypot(a[11],a[12])>=0.9*_sens1: problems.append('lock-in magnitude >=90% full scale')
    if not 5e-9 < a[8]/_mc['sr0_gain'] < 15e-9: problems.append('drain current outside 5..15 nA')
    if _fan_count in (1,20) or _fan_count%len(fan_n)==0:
        print(f'FAN CHECK point {_fan_count}: B={a[14]:.4f} T, Ts={a[4]:.3f} K, I={a[8]/_mc["sr0_gain"]*1e9:.3f} nA, TG/BG={a[15]:.4f}/{a[16]:.4f} V')
    if problems:
        print('FAN STOP:', '; '.join(problems),'point',_fan_count)
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
s.ramp(k_bg.volt,float(fan_bg[0])); s.ramp(k_tg.volt,float(fan_tg[0]))
interruptible_sleep(10)
fan_result=s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],
                          [fan_tg,fan_bg],slow_delay=3.0,fast_delay=3.0)
print('FAN COMPLETE run',fan_result.id,'interrupted',fan_result.metadata.get('interrupted'))
print('Endpoint B,TG,BG,Si,Ts,Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
