# Plan step 4: both-sign Landau fan, inferred D=0, measured pair B_1-B_2.
# Read-only preflight: stop before any write on mismatch.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Si = k_si()
_hr = (heater.sample_range(), heater.vaporizer_range())
_ps = (magnet.persistent_switch_on(), magnet.output_enabled())
print('Expected base 1.0..1.5 K, vaporizer <1.6 K within 0.6 K; B near 0; Si 0; heaters off; PS/output on')
print('Actual:', dict(T_sample=_Ts, T_vaporizer=_Tv, B=_B, Si=_Si, heater_ranges=_hr, PS_output=_ps))
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts) < 0.6
assert abs(_B) < 0.02 and abs(_Si) < 0.01 and _hr == (0,0) and all(_ps)
for _p, _bounds in ((k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.0,25.0)), (dc205.voltage,(-25.0,25.0)),
                    (magnet.field,(-10.0,10.0)), (heater.sample_setpoint,(0.0,100.0)),
                    (heater.vaporizer_setpoint,(0.0,100.0))):
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name, 'validator expected',_bounds,'actual',_actual)
    assert _actual == _bounds
assert B_SESSION_CAP == 10 and T_SESSION_CAP == 100
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
_drive, _freq = sr1.amplitude(), sr1.frequency()
_taus=(sr0.time_constant(),sr1.time_constant())
_slopes=(sr0.filter_slope(),sr1.filter_slope())
_nplc=(k_tg.nplci(),k_bg.nplci())
_steps=(k_tg.volt.step,k_bg.volt.step)
print('Expected drive 1 V / 13.777 Hz; tau .3/.3, slope 24/24; NPLC 1/1; gate steps .005/.005')
print('Actual:',_drive,_freq,_taus,_slopes,_nplc,_steps,'Si pacing',dc205.ramp_rate)
assert abs(_drive-1.0)<1e-6 and abs(_freq-13.777)<0.01
assert _taus == (0.3,0.3) and _slopes == (24,24) and _nplc == (1.0,1.0) and _steps == (0.005,0.005)
assert dc205.ramp_rate == 0.5 and dc205.voltage_range()==2 and dc205.output()==1
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

from sharpelab_nb.gates import calc_gate_voltages
# Explicit run-5 fit, conventional units: n in 1e12 cm^-2, D in V/nm.
fan_cal = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137, D_offset=-0.013)
fan_n = np.linspace(-1.20,3.20,111)
fan_tg,fan_bg = calc_gate_voltages(fan_n,np.zeros_like(fan_n),**fan_cal)
fan_B = np.r_[0.0,0.5,0.75,1.0,field_invB(1.5,10.0,86)]
assert np.all(np.diff(fan_B)>0) and len(fan_B)==90
for _p,_v in ((k_tg.volt,fan_tg),(k_bg.volt,fan_bg),(magnet.field,fan_B)):
    for _x in _v: _p.validate(float(_x))
print('Fan points',len(fan_B)*len(fan_n),'TG',fan_tg[[0,-1]],'BG',fan_bg[[0,-1]],'B',fan_B[[0,-1]])
# Ordinary acquisition range, not a validator/operating-limit change.
sr1.sensitivity(100e-6)
_sens0,_sens1 = sr0.sensitivity(),sr1.sensitivity()
assert _sens0 == 0.02 and _sens1 == 100e-6
mc=dict(meas_config)
mc.update({'sr1_gain':1.0,'Si (V)':_Si,'sample_temperature:':_Ts,
           'gate_calibration':fan_cal,'density_scale_status':'geometry-anchored absolute scale; run-5 fitted ratio and CNP; inferred D zero',
           'comments':'landau-fan; B_1-B_2; inferred D=0; n_prior=-1.2..3.2e12 cm^-2 (111); B=0,0.5,0.75,1 then 1.5..10 T uniform 1/B (86); Si=0; base T; fast delay 3 s; sr1 100 uV'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(mc['comments'])
s.add_comment('Calibration source data/5; field feasibility data/6 and data/7; plan step 4. No Si move. Gate pacing unchanged.')
s.ramp(k_bg.volt,float(fan_bg[0]));s.ramp(k_tg.volt,float(fan_tg[0]))
interruptible_sleep(10)
fan_followed=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,
              magnet.field,k_tg.volt,k_bg.volt,k_si]
for _p in fan_followed:
    s.fp(_p)
    s.plot('time',_p)
# All raw lock-in values stored unscaled; gains in metadata, analysis uses measured I.
fan_guard={'points':0,'reason':None}
def fan_after(station,data,writer):
    # Duplicate columns: last occurrence is measured readback, first is setpoint.
    values=dict(zip(writer.metadata['columns'],data))
    reasons=[]
    if not np.all(np.isfinite(data)): reasons.append('nonfinite readback')
    for p in (k_tg.curr,k_bg.curr):
        if abs(values[p.full_name])>1e-9: reasons.append(p.full_name+' >1 nA')
    if abs(values[sr0.X.full_name])>0.9*_sens0 or abs(values[sr1.X.full_name])>0.9*_sens1:
        reasons.append('lock-in >=90% full scale')
    cur=values[sr0.X.full_name]/mc['sr0_gain']
    if not 8e-9<cur<12e-9: reasons.append('drain current outside 8..12 nA')
    if not 1.0<=values[T_sample.full_name]<=1.5: reasons.append('sample temperature outside base window')
    if not 0<values[T_vaporizer.full_name]<1.6: reasons.append('vaporizer temperature outside base window')
    if abs(values[magnet.field.full_name]-data[1])>0.03: reasons.append('field readback mismatch >30 mT')
    if abs(values[k_tg.volt.full_name]-data[2])>0.01 or abs(values[k_bg.volt.full_name]-data[3])>0.01:
        reasons.append('gate readback mismatch >10 mV')
    if abs(values[k_si.full_name])>0.01: reasons.append('Si no longer zero')
    fan_guard['points']+=1
    if fan_guard['points'] % len(fan_n)==0:
        try:
            assert_thermometry_live('T_sample',VTI.temp_logfile_candidates['T_sample'],max_age=15,max_period=12)
            assert_thermometry_live('T_vaporizer',VTI.temp_logfile_candidates['T_vaporizer'],max_age=15,max_period=12)
        except Exception as exc: reasons.append('thermometry freshness: '+str(exc))
    if reasons:
        fan_guard['reason']='; '.join(reasons)
        print('FAN STOP:',fan_guard['reason'],'at B',data[1],'TG/BG',data[2:4])
        station.interrupt_requested=True
s.register_run_after(fan_after,())
fan_result=s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],
                          [fan_tg,fan_bg],slow_delay=3.0,fast_delay=3.0)
print('Fan run',fan_result.id,'interrupted',fan_result.metadata.get('interrupted'),'guard',fan_guard)
print('Actual final B, TG, BG, Si, T:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample())
# Hold actual endpoint. A kernel interrupt does NOT stop a VTI supply ramp.
