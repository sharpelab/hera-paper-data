# landau-fan-vti: B_1-B_2, D_A=0, n_A=+2.8..+3.2e12; run-5 calibration.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preflight: all assumptions and the committed safety envelope.
for _p, _limits in [(k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name, 'validator expected', _limits, 'actual', _actual)
    assert _actual == _limits
assert B_SESSION_CAP == 10 and T_SESSION_CAP == 100
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv,_B0,_Si=T_sample(),T_vaporizer(),magnet.field(),k_si()
_ranges=(heater.sample_range(),heater.vaporizer_range())
_ps,_out=magnet.persistent_switch_on(),magnet.output_enabled()
print('expected: sample 1.0..1.5 K, vaporizer <1.6 K within 0.6 K, B=0 +/-0.05 T, Si=0 +/-0.01 V, heaters off, PS/output on')
print('actual:',_Ts,_Tv,_B0,_Si,_ranges,_ps,_out)
assert 1 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts)<0.6
assert abs(_B0)<0.05 and abs(_Si)<0.01 and _ranges==(0,0) and _ps and _out
print('gate pacing expected 5 mV / Si 0.5 V/s; actual',k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate)
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005 and dc205.ramp_rate==0.5
print('Si RNGE/output expected 2/1; actual',dc205.voltage_range(),dc205.output())
assert dc205.voltage_range()==2 and dc205.output()==1
for _li in (sr0,sr1):
    _tau,_slope=_li.time_constant(),_li.filter_slope()
    print(_li.name,'tau/slope expected 0.3/24; actual',_tau,_slope)
    assert np.isclose(_tau,0.3) and _slope==24
_A,_Hz=sr1.amplitude(),sr1.frequency()
print('drive expected 1 V, 13.777 Hz; actual',_A,_Hz)
assert np.isclose(_A,1.) and abs(_Hz-13.777)<0.01
print('NPLC expected 1/1; actual',k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

CAL_FAN=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,
             n_offset=-0.08937933224099137,D_offset=-0.013)
ns_fan=np.linspace(2.8,3.2,10)
Vtgs,Vbgs=calc_gate_voltages(ns_fan,np.zeros(10),**CAL_FAN)
_nr,_dr=calc_nD(Vtgs,Vbgs,**CAL_FAN)
assert np.allclose(_nr,ns_fan) and np.max(abs(_dr))<1e-12
assert np.all((Vtgs>=-.3)&(Vtgs<=1.)) and np.all((Vbgs>=-1.3)&(Vbgs<=2.))
B_lo=1.0309096913954; B_hi=7.1
_u1=np.linspace(1/B_lo,1/3.5,int(np.ceil((1/B_lo-1/3.5)/(.01/1.01)))+1)
_u2=np.linspace(1/3.5,1/B_hi,int(np.ceil((1/3.5-1/B_hi)/(.5/143)))+1)
B_fan=1/np.r_[_u1,_u2[1:]]
assert len(B_fan)==113 and np.all(np.diff(B_fan)>0) and B_fan.max()<=10
print('fan:',len(B_fan),'B rows x',len(ns_fan),'densities; Vtg',Vtgs[[0,-1]],'Vbg',Vbgs[[0,-1]])
print('B positioning from actual to first row: minutes',abs(B_lo-_B0)*7.3,'; total traverse to 7.1 T ~51.8 min from zero')
# Explicit fixed acquisition preset. Pacing, time constants and safety limits are untouched.
sr1.sensitivity(50e-6)
assert np.isclose(sr1.sensitivity(),50e-6)
assert np.isclose(sr0.sensitivity(),.02)
mc=dict(meas_config)
mc.update({'sr1_gain':1., 'Si (V)':_Si,'sample_temperature:':_Ts,
           'gate_calibration':CAL_FAN,'n_units':'1e12 cm^-2','n_setpoints':ns_fan.tolist(),
           'D_V_per_nm':0.,'comments':'landau-fan-vti; B_1-B_2; n_A=2.8..3.2e12, D_A=0; B=1.03090969..7.1 T ascending; 113x10; fast dwell 3 s; sr1 50 uV; cal run 5'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('B_1-B_2; n_A +2.8..+3.2e12 cm^-2, D_A=0 V/nm; 113 B rows 1.03090969->7.1 T; 10 n points; segmented uniform 1/B, refined above 3.5 T for harmonics; 3 s fast dwell; sr1=50 uV, I_bias=10 nA; calibration run 5, absolute scale geometry prior; checkpoint first 3 rows and every 20 rows')
# Fixed row layout: time,Bset,Vtgset,Vbgset,Ts,Tv,Itg,Ibg,I_X,I_P,V_X,V_P,Bread,TGread,BGread,Si.
_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,
         magnet.field,k_tg.volt,k_bg.volt,k_si]
for _p in _follow:
    s.fp(_p)
    s.plot('time',_p)
_guard_count=[0]
def fan_guard(station,data):
    _d=np.asarray(data,dtype=float)
    _issues=[]
    if not np.all(np.isfinite(_d)): _issues.append('nonfinite read')
    if not (1<=_d[4]<=1.5 and 0<_d[5]<1.6 and abs(_d[4]-_d[5])<.6): _issues.append('base temperature')
    if max(abs(_d[6]),abs(_d[7]))>1e-9: _issues.append('gate leakage >1 nA')
    if abs(_d[10])>=.9*50e-6 or abs(_d[8])>=.9*.02: _issues.append('lock-in range')
    if not 8e-9 < _d[8]/-1e6 < 12e-9: _issues.append('drain current')
    if abs(_d[12]-_d[1])>.03: _issues.append('field tracking')
    if max(abs(_d[13]-_d[2]),abs(_d[14]-_d[3]))>.003 or abs(_d[15])>.01: _issues.append('gate tracking')
    if _guard_count[0]%10==0:
        try:
            for _name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
        except Exception as _exc: _issues.append(str(_exc))
    _guard_count[0]+=1
    if _issues:
        print('FAN STOP:', '; '.join(_issues), 'Bset/read',_d[1],_d[12])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
s.ramp(k_bg.volt,float(Vbgs[0])); s.ramp(k_tg.volt,float(Vtgs[0]))
interruptible_sleep(3)
# The sweep's first slow-axis set performs the blocking positioning ramp; no duplicate ramp.
s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1,fast_delay=3)
print('fan end readback:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
print('Field and gates hold at actual endpoint for analysis; no automatic retraverse or close-out.')
