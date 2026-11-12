# Plan step 4: Landau fan, raw gates authoritative; n/D labels provisional.
# Preconditions are read-only and run before any hardware write.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
for _label in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_label, VTI.temp_logfile_candidates[_label], max_age=15, max_period=12)
_Ts, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_ranges = (heater.sample_range(), heater.vaporizer_range())
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'Expected base 1.0..1.5 K, vaporizer <1.6 K, B~0, Si=0, ranges=(0,0), PS/output on; actual {_Ts}, {_Tv}, {_B}, {_Si}, {_ranges}, {_ps}/{_out}')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Ts-_Tv)<0.6
assert abs(_B)<0.02 and abs(_Si)<0.01 and _ranges==(0,0) and _ps and _out
for _p, _limits in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                     (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                     (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                     (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name, 'expected', _limits, 'actual', _actual)
    assert _actual==_limits
assert B_SESSION_CAP==10.0 and T_SESSION_CAP==100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
_pacing=(k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate)
_nplc=(k_tg.nplci(),k_bg.nplci())
_drive,_freq=sr1.amplitude(),sr1.frequency()
_tau=(sr0.time_constant(),sr1.time_constant()); _slope=(sr0.filter_slope(),sr1.filter_slope())
print('Expected pacing .005/.005/.5, NPLC 1/1, drive 1 V at 13.777 Hz, tau .3/.3, slope24/24; actual', _pacing,_nplc,_drive,_freq,_tau,_slope)
assert _pacing==(.005,.005,.5) and _nplc==(1.,1.)
assert abs(_drive-1)<1e-6 and abs(_freq-13.777)<.01 and _tau==(.3,.3) and _slope==(24,24)
assert dc205.voltage_range()==2 and dc205.output()==1
assert sr0.sensitivity()==.02
CAL_FAN=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,n_offset=-0.08937933224099137,D_offset=-0.013)
n_fan=np.linspace(-1.2,3.2,111)
Vtg_fan,Vbg_fan=calc_gate_voltages(n_fan,np.zeros_like(n_fan),**CAL_FAN)
B_fan=np.r_[0.,field_invB(2.,10.,65)]
for _p,_vec in [(k_tg.volt,Vtg_fan),(k_bg.volt,Vbg_fan),(magnet.field,B_fan)]:
    for _v in _vec: _p.validate(float(_v))
    print(_p.full_name, 'planned range', float(min(_vec)),float(max(_vec)))
_nn,_dd=calc_nD(Vtg_fan,Vbg_fan,**CAL_FAN)
assert np.allclose(_nn,n_fan) and np.max(abs(_dd))<1e-10
print('Fan:',len(B_fan),'rows x',len(n_fan),'points; 3 s dwell; raw gate axes authoritative')

sr1.sensitivity(100e-6)
_sens1=sr1.sensitivity(); _sens0=sr0.sensitivity()
assert _sens1==100e-6
mc=dict(meas_config)
mc.update({'sr1_gain':1.0,'Si (V)':_Si,'sample_temperature:':_Ts,
           'comments':'landau-fan: B1-B2; B=0 then 2..10 T uniform inverse-B; nominal D=0; provisional n=-1.2..3.2e12 cm^-2; Si=0',
           'gate_calibration':dict(CAL_FAN,source_run=5,absolute_scale='geometry prior',D_zero='resistance minimum proxy'),
           'sr1_sensitivity_V':_sens1,'sr0_sensitivity_V':_sens0,
           'time_constants_s':list(_tau),'filter_slopes_dB_oct':list(_slope),'gate_nplci':list(_nplc)})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('B_1-B_2; source T_0/drain B_3; B=0 baseline +65 inverse-B points 2..10 T; TG/BG co-swept 111 points along run-5 nominal D=0; provisional n=-1.2..3.2e12 cm^-2 step .04; Si=0; base T; dwell3s; sr1=100uV; no gate-pacing changes')
# Distinct readback name avoids duplicate planned/measured field columns.
fan_B_readback=qcodes.Parameter('fan_B_readback',unit='T',get_cmd=magnet.field)
_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,fan_B_readback]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)
# data: time, B_set, TG_set, BG_set, Ts, Tv, Itg, Ibg, sr0X,P, sr1X,P, B_read
_fan_count=0

def fan_before(station):
    if _fan_count % len(n_fan)==0:
        for _label in ('T_sample','T_vaporizer'):
            assert_thermometry_live(_label,VTI.temp_logfile_candidates[_label],max_age=15,max_period=12)

def fan_after(station,data):
    global _fan_count
    _fan_count+=1
    _a=np.asarray(data,dtype=float)
    _why=[]
    if not np.all(np.isfinite(_a)): _why.append('nonfinite-read')
    if max(abs(_a[6]),abs(_a[7]))>1e-9: _why.append('gate-current-over-1nA')
    if not (1.0<=_a[4]<=1.5 and 0<_a[5]<1.6): _why.append('temperature')
    if abs(_a[12]-_a[1])>.025: _why.append('field-readback')
    if max(abs(_a[8])/_sens0,abs(_a[10])/_sens1)>.90: _why.append('range-headroom')
    _I=_a[8]/mc['sr0_gain']
    if not 5e-9<_I<15e-9: _why.append('drain-current')
    if _why:
        print('FAN STOP:',','.join(_why),'point',_fan_count,'B',_a[1],flush=True)
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
s.ramp(k_bg.volt,float(Vbg_fan[0])); s.ramp(k_tg.volt,float(Vtg_fan[0]))
interruptible_sleep(10)
# No finally-ramp: after interruption inspect actual state before any new move.
fan_result=s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vtg_fan,Vbg_fan],slow_delay=3.,fast_delay=3.)
print('FAN COMPLETE',fan_result.id,'B/TG/BG/Si/Ts/Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
