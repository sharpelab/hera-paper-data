# landau-fan-vti: paired D=0 n-line, monotonic positive-B fan.
# Preconditions are read-only; do not change validators, ramp steps, or pacing.
from sharpelab_nb.gates import calc_gate_voltages
for _p, _expected in ((k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
        (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
        (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
        (heater.vaporizer_setpoint,(0.,100.))):
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(f'{_p.full_name} validator: expected {_expected}, actual {_actual}')
    assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B=T_sample(),T_vaporizer(),magnet.field()
_Si=k_si(); _ranges=(heater.sample_range(),heater.vaporizer_range())
_PS,_out=magnet.persistent_switch_on(),magnet.output_enabled()
print(f'Expected base Ts 1.0..1.5, Tv 0.5..1.6 K, B~0 T, Si=0, heaters off, PS/output on; actual {_Ts}, {_Tv}, {_B}, {_Si}, {_ranges}, {_PS}/{_out}')
assert 1.0<=_Ts<=1.5 and .5<=_Tv<=1.6 and abs(_Tv-_Ts)<.6
assert abs(_B)<.02 and abs(_Si)<.01 and _ranges==(0,0) and _PS and _out
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
               'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
for _li in (sr0,sr1):
    _tau,_slope=_li.time_constant(),_li.filter_slope()
    print(f'{_li.name}: expected tau=0.3 s, slope=24; actual {_tau}, {_slope}')
    assert _tau==.3 and _slope==24
_A,_f=sr1.amplitude(),sr1.frequency()
print(f'Drive expected 1 V, 13.777 Hz; actual {_A}, {_f}; current sens expected 20 mV, actual {sr0.sensitivity()}')
assert abs(_A-1)<1e-6 and abs(_f-13.777)<.01 and sr0.sensitivity()==.02
for _g in (k_tg,k_bg):
    print(f'{_g.name}: expected NPLC=1, step=.005; actual {_g.nplci()}, {_g.volt.step}; gate now {_g.volt()} V')
    assert _g.nplci()==1 and _g.volt.step==.005

# Same rounded calibration as run 6, preserving its +3.2 shared gate point.
CAL=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
ns=np.linspace(2.8,3.2,10)
Vtgs,Vbgs=calc_gate_voltages(ns,np.zeros_like(ns),**CAL)
B_vec=field_invB(1.0309096913954,7.05,238)
assert np.all((Vtgs>=-.3)&(Vtgs<=1.)) and np.all((Vbgs>=-1.3)&(Vbgs<=2.))
assert np.all(np.diff(B_vec)>0) and max(B_vec)<=10
assert max(abs(np.diff(1/B_vec)))<=.0035
print(f'Grid {len(B_vec)}x{len(ns)}; TG {Vtgs[0]:.6f}..{Vtgs[-1]:.6f}, BG {Vbgs[0]:.6f}..{Vbgs[-1]:.6f}; B {_B:.4f}->7.05 T, bare ramp ~{(7.05-_B)*7.3:.1f} min')
# Explicit fixed acquisition setup; 50 uV = 5 kOhm nominal full scale.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
mc=dict(meas_config)
mc.update({'Si (V)':_Si,'sample_temperature:':_Ts,'sr1_gain':1.,
 'comments':'D=0 electron fan, n=2.8..3.2e12; B=1.03091..7.05 T; 238x10; run-5 calibration; sr1 50uV; 3s settle=10tau; NPLC1',
 'gate_calibration':CAL,'n_points_e12':ns.tolist(),'D_V_per_nm':0.,
 'onset_caveat':'run6 b_hi4 degree5:1.03091 T; degree3 marginal light tone, robust onset1.38 T'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('tetralayer-stacking-fs-count Step4; B_1-B_2; n=+2.8..+3.2e12 cm^-2, D=0; B=1.0309096914->7.05 T uniform1/B 238 rows x10; Vsi=0; baseT; run6 shared n=3.2; onset uncertainty 1.0..1.4T')
# Actual row: time,B,Vtg,Vbg,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P.
followed=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P]
for _p in followed:
    s.fp(_p)
    s.plot('time',_p)
s.plot(k_tg.volt,magnet.field,sr1.X)
s.ramp(k_bg.volt,float(Vbgs[0])); s.ramp(k_tg.volt,float(Vtgs[0]))
interruptible_sleep(3)
# No pre-positioning: the sweep writes its run directory BEFORE its first field move.
_guard={'last_fresh':0.,'trip':None}
def fan_before(station):
    # Native fast_delay uses sleep; use the interruptible dwell explicitly.
    interruptible_sleep(3.,show_progress=False)
    if time.monotonic()-_guard['last_fresh']>=30:
        for name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        _guard['last_fresh']=time.monotonic()
def fan_after(station,data):
    vals=np.asarray(data[4:],dtype=float)
    why=[]
    if not np.all(np.isfinite(vals)): why.append('nonfinite read')
    if not (1.0<=data[4]<=1.5 and .5<=data[5]<=1.6): why.append('temperature off base')
    if abs(data[6])>1e-9 or abs(data[7])>1e-9: why.append('gate current >1 nA')
    if abs(data[8])>=.9*.02 or abs(data[10])>=.9*50e-6: why.append('lockin near full scale')
    if not 8e-9<=data[8]/-1e6<=11e-9: why.append('drain current outside 8..11 nA')
    if why:
        _guard['trip']='; '.join(why)
        print(f'FAN STOP: {_guard["trip"]}; B={data[1]}, TG={data[2]}, BG={data[3]}')
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
fan_result=s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1.,fast_delay=0.)
# Hold endpoints, including on interruption: do not issue a cleanup field move.
print('FAN END: actual B/TG/BG',magnet.field(),k_tg.volt(),k_bg.volt(),'guard',_guard['trip'])
