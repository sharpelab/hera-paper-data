# landau-fan-vti: region-A D=0, electron n=3.2 -> 2.8e12 cm^-2.
# Read-only preconditions precede every instrument write.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
import numpy as np

for _p, _limits in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                    (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                    (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                    (heater.vaporizer_setpoint,(0.,100.))]:
    _actual=(float(_p.vals._min_value),float(_p.vals._max_value))
    print('SAFETIES',_p.full_name,'expected',_limits,'actual',_actual)
    assert _actual == _limits, 'SAFETIES mismatch; stop before writes'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ('T_sample','T_vaporizer'):
    assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
_Ts,_Tv=T_sample(),T_vaporizer()
_B0=magnet.field(); _ps=magnet.persistent_switch_on(); _out=magnet.output_enabled()
_ranges=(heater.sample_range(),heater.vaporizer_range())
_si=(dc205.voltage_range(),dc205.output(),k_si())
print('PRECHECK T sample/vaporizer',_Ts,_Tv,'expected 1.0..1.5 / <1.6 K; heater ranges',_ranges,'expected (0,0)')
print('PRECHECK B',_B0,'expected |B|<0.05 T; PS/output',_ps,_out,'expected True/True; Si',_si,'expected (2,1,0)')
print('GATE starting readback',k_tg.volt(),k_bg.volt(),'V; both are set by this cell')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts)<0.6
assert _ranges==(0,0) and abs(_B0)<0.05 and _ps and _out
assert _si[0]==2 and _si[1]==1 and abs(_si[2])<0.01
print('PACING TG/BG step',k_tg.volt.step,k_bg.volt.step,'expected .005/.005; Si rate',dc205.ramp_rate,'expected .5')
assert k_tg.volt.step==.005 and k_bg.volt.step==.005 and dc205.ramp_rate==.5
print('NPLC',k_tg.nplci(),k_bg.nplci(),'expected 1/1')
assert k_tg.nplci()==1 and k_bg.nplci()==1
print('DRIVE',sr1.amplitude(),sr1.frequency(),'expected 1 V, 13.777 Hz')
assert abs(sr1.amplitude()-1.0)<1e-6 and abs(sr1.frequency()-13.777)<.01
for _sr in (sr0,sr1):
    _tau,_slope=_sr.time_constant(),_sr.filter_slope()
    print('LOCKIN',_sr.name,'tau/slope',_tau,_slope,'expected .3 s / 24 dB')
    assert _tau==.3 and _slope==24
assert abs(sr0.sensitivity()-.02)<1e-9
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
               'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'} and 'mux' not in globals()
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_channel']=='sr1' and meas_config['bias_resistor']==100e6

FAN_CAL=dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,
             n_offset=-0.08937933224099137,D_offset=-0.013)
FAN_NS=np.linspace(3.2,2.8,11)
FAN_B=field_invB(1.017617880804576,6.5,151)
FAN_VT,FAN_VB=calc_gate_voltages(FAN_NS,np.zeros_like(FAN_NS),**FAN_CAL)
_ncheck,_dcheck=calc_nD(FAN_VT,FAN_VB,**FAN_CAL)
assert np.allclose(_ncheck,FAN_NS) and np.max(np.abs(_dcheck))<1e-10
for _p,_vec in ((k_tg.volt,FAN_VT),(k_bg.volt,FAN_VB),(magnet.field,FAN_B)):
    for _v in _vec: _p.validate(float(_v))
assert max(abs(np.diff(1/FAN_B))) <= 1/(2*89.98296952833738)
assert 1.2*max(abs(np.diff(FAN_NS))) <= 4*cst.e/cst.h*min(FAN_B)/1e16/2
print('FAN 151 B x 11 n; B',FAN_B[[0,-1]],'n',FAN_NS[[0,-1]],'TG',FAN_VT[[0,-1]],'BG',FAN_VB[[0,-1]])
print('Ramp budget from actual B to endpoint:',abs(6.5-_B0)*7.3,'min at 1 A/min; no automatic field return')

# Acquisition choices, not safety-surface changes. Keep operator pacing/tau.
sr1.sensitivity(50e-6)
assert abs(sr1.sensitivity()-50e-6)<1e-12
mc=dict(meas_config)
mc.update({'Si (V)':_si[2],'sample_temperature:':_Ts,
           'comments':'landau-fan-vti; n_A 3.2->2.8e12, D_A=0; B 1.017618->6.5 T uniform inverse B; 151x11; run-5 calibration; sr1 50uV, fast dwell 3s',
           'gate_calibration':FAN_CAL,'n_A_setpoints_1e12':FAN_NS.tolist(),
           'sr0_tau_s':.3,'sr1_tau_s':.3,'filter_slope_dB':24,
           'onset_provenance':'run6 local B<=5T degree5; qualified background-sensitive 1.017618T',
           'timing_provenance':'run5 1.0985s at 1s dwell; runs6/7 ramp overhead 3.08s/step'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('n_A=3.2->2.8e12 cm^-2, D_A=0 V/nm, B=1.0176178808->6.5 T, 151 inverse-B rows x 11 density points; Vsi=0; base T; B_1-B_2; calibration run5; 50uV; 3s=10tau')
# Row: time, B_set, TG, BG, T_sample, T_vaporizer, Itg, Ibg, sr0X, sr0P, sr1X, sr1P.
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(_p)
    s.plot('time',_p)
s.plot(k_tg.volt,sr1.X)
_last_fan_B=None
_fan_trips=[]
def fan_guard(station,data):
    global _last_fan_B
    _why=[]
    if not np.all(np.isfinite(data)): _why.append('nonfinite data')
    if not 1.0<=float(data[4])<=1.5 or not 0<float(data[5])<1.6: _why.append('base temperature lost')
    if max(abs(float(data[6])),abs(float(data[7])))>1e-9: _why.append('gate current exceeds existing 1nA trip')
    if abs(float(data[10]))>=.9*50e-6 or abs(float(data[8]))>=.9*.02: _why.append('lock-in near full scale')
    _idrain=float(data[8])/-1e6
    if not 8e-9<_idrain<12e-9: _why.append('drain current outside 8..12nA')
    if _last_fan_B!=float(data[1]):
        _last_fan_B=float(data[1])
        try:
            for _name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
            _bm=magnet.field()
            print(f'ROW B expected {_last_fan_B:.6f}, measured {_bm:.6f} T')
            if abs(_bm-_last_fan_B)>.02: _why.append('field readback mismatch')
        except Exception as _err: _why.append(str(_err))
    if _why:
        _fan_trips.extend(_why)
        print('FAN STOP:',_why,'B/TG/BG=',data[1:4])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
s.ramp(k_bg.volt,float(FAN_VB[0])); s.ramp(k_tg.volt,float(FAN_VT[0]))
interruptible_sleep(3)
# First blocking B set is performed by multimegasweep after the run dir opens.
# No pre-ramp or blind return: the data monitor is armed before execution.
_fan_result=s.multimegasweep([magnet.field],[FAN_B],[k_tg.volt,k_bg.volt],[FAN_VT,FAN_VB],slow_delay=1.,fast_delay=3.)
print('FAN END file_id',_fan_result.id,'interrupted',_fan_result.metadata.get('interrupted',False),'trips',_fan_trips)
print('ACTUAL B/TG/BG/Tsample/Tvap',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample(),T_vaporizer())
# Hold the endpoint for analysis and the next deliberate move.
