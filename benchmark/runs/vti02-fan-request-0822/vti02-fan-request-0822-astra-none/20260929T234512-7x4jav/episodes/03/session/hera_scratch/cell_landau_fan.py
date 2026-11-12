# Plan step 4: nominal-D=0 Landau fan. Preconditions precede all writes.
import numpy as np
import scipy.constants as _sc

for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_ts, _tv, _b = T_sample(), T_vaporizer(), magnet.field()
_vsi = k_si()
_ranges = (heater.sample_range(), heater.vaporizer_range())
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'Expected base Ts=1.0..1.5 K, Tv=0.7..1.6 K, |B|<0.02 T, Si=0, heaters off, PS/output on; actual {_ts}, {_tv}, {_b}, {_vsi}, {_ranges}, {_ps}/{_out}')
assert 1.0 <= _ts <= 1.5 and 0.7 <= _tv <= 1.6 and abs(_ts-_tv)<0.6
assert abs(_b)<0.02 and abs(_vsi)<0.01 and _ranges==(0,0) and _ps and _out
for _p, _expected in ((k_tg.volt,(-0.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                      (dc205.smart_voltage,(-25.0,25.0)), (dc205.voltage,(-25.0,25.0)),
                      (magnet.field,(-10.0,10.0)), (heater.sample_setpoint,(0.0,100.0)),
                      (heater.vaporizer_setpoint,(0.0,100.0))):
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print(f'{_p.full_name} validator expected {_expected}, actual {_actual}')
    assert _actual==_expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
_dc=(dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
print('Expected DC205 (range,output,rate)=(2,1,0.5), actual',_dc)
assert _dc==(2,1,0.5)
_ac=(sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope(),sr0.sensitivity())
print('Expected AC (1 V,13.777 Hz,0.3 s,0.3 s,24,24,0.02 V), actual',_ac)
assert abs(_ac[0]-1)<1e-6 and abs(_ac[1]-13.777)<0.01 and _ac[2:]==(0.3,0.3,24,24,0.02)
print('Gate pacing: expected steps 0.005 V, nplci=1; actual',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci(),'; inter_delays',k_tg.volt.inter_delay,k_bg.volt.inter_delay)
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005 and k_tg.nplci()==1 and k_bg.nplci()==1

# Explicit run-5 calibration; density in SI internally, display in 1e12 cm^-2.
_fcal=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,n_offset=-0.08937933224099137,D_offset=-0.013)
_fan_n=np.linspace(-1.2,3.2,221)
_q=_sc.e*(_fan_n-_fcal['n_offset'])*1e16
_delta=2*_sc.epsilon_0*(0.0-_fcal['D_offset'])*1e9
_fan_tg=(_q+_delta)/(2*_fcal['c_tg'])
_fan_bg=(_q-_delta)/(2*_fcal['c_bg'])
_fan_B=np.r_[0.0,np.round(np.arange(1.0,10.0001,0.2),4)]
for _p,_vec in ((k_tg.volt,_fan_tg),(k_bg.volt,_fan_bg),(magnet.field,_fan_B)):
    for _v in _vec: _p.validate(float(_v))
    print(f'{_p.full_name} planned {min(_vec):+.6f}..{max(_vec):+.6f}, {len(_vec)} points')
assert len(_fan_B)==47 and len(_fan_n)==221

# Only acquisition-range change; gate/field/T validators and ramp pacing untouched.
sr1.sensitivity(100e-6)
assert sr1.sensitivity()==100e-6
mc=dict(meas_config)
mc.update({'sr1_gain':1.0,'Si (V)':_vsi,'sample_temperature:':_ts,
           'gate_calibration_run5':_fcal,'density_scale_status':'geometry-anchored; CNP ratio empirical; D zero operational',
           'nominal_density_1e12_cm2':_fan_n.tolist(),'nominal_D_V_nm':0.0,
           'point_settle_s':3.0,'sr0_tau_s':_ac[2],'sr1_tau_s':_ac[3],
           'sr0_filter_slope':_ac[4],'sr1_filter_slope':_ac[5],
           'comments':'B_1-B_2 landau-fan: B 0 baseline then 1..10 T step .2; n_geom -1.2..3.2e12 step .02; nominal D0; base T; Si0; 3s settle via before hook'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B_1-B_2; run-5 CNP calibration, absolute scale geometry prior; B=0 then 1:0.2:10 T; n=-1.2:0.02:3.2 x10^12 cm^-2; Dnom=0 V/nm; Si=0 V; Ibias=10 nA; sr1=100 uV; 3 s=10tau settling; TG/BG co-swept at unchanged pacing')
s.ramp(k_bg.volt,float(_fan_bg[0])); s.ramp(k_tg.volt,float(_fan_tg[0]))
interruptible_sleep(10)
# Columns: time, Bset, TGset, BGset, then the followed values below.
_fan_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field,k_tg.volt,k_bg.volt]
for _p in _fan_follow:
    s.fp(_p)
    s.plot('time',_p)
_fan_count=[0]
_fan_trips=[]

def _fan_before(station):
    # Dwell is interruptible; sweep fast_delay=0 avoids a bare blocking sleep.
    interruptible_sleep(3)

def _fan_after(station,data):
    _fan_count[0]+=1
    ts,tv,it,ib,x0,p0,x1,p1,bread,vt,vb=map(float,data[4:])
    issues=[]
    if not np.all(np.isfinite(data)): issues.append('nonfinite read')
    if abs(it)>1e-9 or abs(ib)>1e-9: issues.append(f'gate leakage {it:g}/{ib:g} A')
    if not (1<=ts<=1.5 and 0.7<=tv<=1.6 and abs(ts-tv)<0.6): issues.append(f'off-base T {ts}/{tv}')
    if abs(x0)>=0.9*0.02 or abs(x1)>=0.9*100e-6: issues.append('lock-in range >=90%')
    if not 8e-9 <= x0/(-1e6) <= 12e-9: issues.append(f'drain current {x0/-1e6:g} A')
    if abs(bread-float(data[1]))>0.03: issues.append(f'field readback {bread} vs {data[1]}')
    if abs(vt-float(data[2]))>0.003 or abs(vb-float(data[3]))>0.003: issues.append('gate readback mismatch')
    if _fan_count[0]%221==0:
        try:
            for name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        except Exception as exc: issues.append(f'thermometry liveness: {exc}')
        print(f'FAN ROW {_fan_count[0]//221}/47 complete B={bread:.4f} T, Ts={ts:.3f}, Tv={tv:.3f}')
    if issues:
        _fan_trips.extend(issues)
        print('FAN STOP:', '; '.join(issues),flush=True)
        station.interrupt_requested=True
s.register_run_before(_fan_before,())
s.register_run_after(_fan_after,())
_fan_result=s.multimegasweep([magnet.field],[_fan_B],[k_tg.volt,k_bg.volt],[_fan_tg,_fan_bg],slow_delay=3,fast_delay=0)
print('FAN COMPLETE:',_fan_result.id,'interrupted=',_fan_result.metadata.get('interrupted'), 'trips=',_fan_trips)
print('End state B/TG/BG/Si/Ts/Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
