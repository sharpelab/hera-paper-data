# landau-fan-vti — fixed D=0, ridge-A calibration, electron-side FS-count fan.
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
import time as _fan_time

# Read-only preflight: every inherited assumption printed and checked before writes.
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_tg0, _bg0, _si0 = k_tg.volt(), k_bg.volt(), k_si()
_ranges = (heater.sample_range(), heater.vaporizer_range())
_ps, _output = magnet.persistent_switch_on(), magnet.output_enabled()
print('Expected base T 1.0..1.5 K, vaporizer <1.6 K, heaters off, B=0 +/-0.02 T, all gates=0 +/-0.01 V; actual:',
      _Ts, _Tv, _ranges, _B, (_tg0, _bg0, _si0), 'PS/output', _ps, _output)
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Ts-_Tv)<.6
assert _ranges == (0,0) and abs(_B)<.02 and _ps and _output
assert max(abs(_tg0),abs(_bg0),abs(_si0))<.01
for _p,_bounds in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),
                    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(_p.full_name,'validator expected',_bounds,'actual',_actual)
    assert _actual==_bounds
assert B_SESSION_CAP==10. and T_SESSION_CAP==100.
_ac=(sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope())
print('AC expected (1 V,13.777 Hz,0.3 s,0.3 s,24 dB,24 dB); actual',_ac)
assert np.allclose(_ac,(1.,13.777,.3,.3,24,24),rtol=0,atol=1e-5)
print('Gate pacing expected 5 mV, Si 0.5 V/s; actual', k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate)
assert k_tg.volt.step==.005 and k_bg.volt.step==.005 and dc205.ramp_rate==.5
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert dc205.voltage_range()==2 and dc205.output()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_channel']=='sr1' and meas_config['bias_resistor']==100e6
assert sr0.sensitivity()==.02

CAL_FAN=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
ns_fan=np.linspace(2.8,3.2,11)
B_fan=field_invB(1.017617880804576,6.4689868523317715,228)
Vt_fan,Vb_fan=calc_gate_voltages(ns_fan,np.zeros(len(ns_fan)),**CAL_FAN)
for _v in Vt_fan: k_tg.volt.validate(float(_v))
for _v in Vb_fan: k_bg.volt.validate(float(_v))
for _v in B_fan: magnet.field.validate(float(_v))
_n,_d=calc_nD(Vt_fan,Vb_fan,**CAL_FAN)
assert np.allclose(_n,ns_fan) and np.max(np.abs(_d))<1e-12
assert np.max(np.abs(np.diff(1/B_fan)))<=1/(2*136.5)
print('Fan',len(B_fan),'B rows x',len(ns_fan),'densities; gates',Vt_fan[[0,-1]],Vb_fan[[0,-1]],
      'ramp floor including positioning', (B_fan[-1]-_B)*7.3,'min')

# Fixed scale inherited from both spot checks: 50 uV = 5 kOhm at 10 nA.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6
mc=dict(meas_config)
mc.update({'Si (V)':_si0,'sample_temperature:':_Ts,'sr1_gain':1.,
           'gate_calibration':CAL_FAN,'n_axis_1e12_cm2':ns_fan.tolist(),
           'comments':'D=0 electron FS fan; ridge-A run5 cal; n=2.8..3.2e12; B=1.017618..6.468987 T; uniform 1/B 228x11; 3 s dwell; sr1 50 uV; Si 0; first 3 rows then every 30 min checkpoints'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('tetralayer-stacking-fs-count: sr1 B_1-B_2; n=+2.8..+3.2e12 cm^-2 (11), D=0 V/nm; B=1.017618..6.468987 T (228 uniform-inverse-field rows); Si=0; 10 nA; 3 s dwell; 50 uV; cal run5 geometry scale; model 5 partner periods nominal')
s.ramp(k_bg.volt,float(Vb_fan[0]));s.ramp(k_tg.volt,float(Vt_fan[0]))
interruptible_sleep(10)
# Magnet positioning occurs as the first sweep row, recorded and watched. No separate blind traverse.
# Columns: time,B,Vtg,Vbg,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.plot('time',_p)
_fan_last_fresh=0.
_fan_guard_reason=[]
def fan_guard(station,data):
    global _fan_last_fresh
    _reason=None
    if not np.all(np.isfinite(data)): _reason='nonfinite acquired value'
    elif abs(data[6])>1e-9 or abs(data[7])>1e-9: _reason='gate current exceeds existing 1 nA trip'
    elif not 1.0<=data[4]<=1.5 or not 0<data[5]<1.6: _reason='base temperature outside preflight window'
    elif abs(data[10])>=.9*50e-6 or abs(data[8])>=.9*.02: _reason='lock-in headroom below 10 percent'
    elif not 8e-9 < data[8]/(-1e6) < 11e-9: _reason='drain current outside 8..11 nA'
    if _fan_time.monotonic()-_fan_last_fresh>60:
        try:
            for _nm in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_nm,VTI.temp_logfile_candidates[_nm],max_age=15,max_period=12)
        except Exception as _err: _reason='thermometry freshness: '+str(_err)
        _fan_last_fresh=_fan_time.monotonic()
    if _reason:
        _fan_guard_reason.append(_reason)
        print('FAN STOP:',_reason,'at B,TG,BG',data[1:4])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
fan_result=s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vt_fan,Vb_fan],slow_delay=1.,fast_delay=3.)
# Hold final actual field and gates for analysis; no automatic restore or retraverse.
print('FAN END: interrupted=',fan_result.metadata.get('interrupted',False),'guard=',_fan_guard_reason)
print('Actual B,TG,BG,Si,T_sample:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample())
