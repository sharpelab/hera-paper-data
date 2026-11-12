# landau-fan-vti: D~0 electron fan, first-session calibration from run 5.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
import contextlib, io

# Preconditions are read before any write. SAFETIES are inspected, never changed.
for name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(name, VTI.temp_logfile_candidates[name], max_age=15, max_period=12)
_ts, _tv, _b, _si = T_sample(), T_vaporizer(), magnet.field(), k_si()
print(f'Expected base sample 1.0..1.5 K, vaporizer <1.6 K, B=0 +/-0.02 T, Si=0 +/-0.01 V; actual {_ts}, {_tv}, {_b}, {_si}')
assert 1.0 <= _ts <= 1.5 and 0 < _tv < 1.6 and abs(_tv-_ts)<0.6
assert abs(_b)<0.02 and abs(_si)<0.01
print('Expected heaters 0/0, PS/output on; actual', heater.sample_range(), heater.vaporizer_range(), magnet.persistent_switch_on(), magnet.output_enabled())
assert heater.sample_range()==0 and heater.vaporizer_range()==0
assert magnet.persistent_switch_on() and magnet.output_enabled()
for param, expected in [(k_tg.volt,(-.3,1.)),(k_bg.volt,(-1.3,2.)),
                        (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                        (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                        (heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(param.vals._min_value),float(param.vals._max_value))
    print(param.full_name,'validator expected',expected,'actual',actual)
    assert actual==expected
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
print('Expected DC205 range/output/rate 2/1/0.5; actual',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==.5
print('Expected gate steps .005/.005 V, NPLC 1/1; actual',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step==.005 and k_bg.volt.step==.005
assert k_tg.nplci()==1 and k_bg.nplci()==1
print('Expected drive 1 V / 13.777 Hz, tau .3 s / slope24 both lock-ins; actual',sr1.amplitude(),sr1.frequency(),sr0.time_constant(),sr1.time_constant(),sr0.filter_slope(),sr1.filter_slope())
assert abs(sr1.amplitude()-1)<.001 and abs(sr1.frequency()-13.777)<.01
assert sr0.time_constant()==.3 and sr1.time_constant()==.3
assert sr0.filter_slope()==24 and sr1.filter_slope()==24
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

CAL=dict(c_tg=.002796,c_bg=.002161,n_offset=-.0894,D_offset=-.013)
ns=np.linspace(3.2,2.8,11)
Vtgs,Vbgs=calc_gate_voltages(ns,np.zeros_like(ns),**CAL)
B_vec=field_invB(1.017617880804576,6.5,151)
assert np.all((Vtgs>=-.3)&(Vtgs<=1.)) and np.all((Vbgs>=-1.3)&(Vbgs<=2.))
assert np.all((B_vec>0)&(B_vec<=10.))
_nr,_dr=calc_nD(Vtgs,Vbgs,**CAL)
assert np.allclose(_nr,ns) and np.allclose(_dr,0)
assert np.max(np.abs(np.diff(1/B_vec)))<=1/(2*90.07484244)
assert np.max(np.abs(np.diff(ns)))<=4*cst.e/cst.h*min(B_vec)/1e16/2/1.2
print('Validated fan:',len(B_vec),'B rows x',len(ns),'density points; TG',Vtgs.min(),Vtgs.max(),'BG',Vbgs.min(),Vbgs.max())

# Fixed whole-fan range: 5 kOhm, >8x the largest spot-check resistance.
# Ten tau per density point retains the spot check's 3 s magnet-settle quality.
sr1.sensitivity(50e-6)
_sens0=sr0.sensitivity(); _sens1=sr1.sensitivity()
assert _sens0==.02 and _sens1==50e-6
mc=dict(meas_config)
mc.update({'Si (V)':_si,'sample_temperature:':_ts,'sr1_gain':1.,'gate_calibration':CAL,
           'drive_amplitude_V':1.,'sr0_tau_s':.3,'sr1_tau_s':.3,
           'sr0_filter_slope':24,'sr1_filter_slope':24,'tg_nplci':1.,'bg_nplci':1.,
           'comments':'landau-fan-vti; B_1-B_2; D~0; n=3.2->2.8e12 cm^-2 (11); B=1.01761788->6.5 T uniform 1/B (151); Vsi=0; 10 nA; sr1=50uV; tau=.3s; fast settle=3s; run5 calibration; geometry-prior scale'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,float(Vbgs[0])); s.ramp(k_tg.volt,float(Vtgs[0]))
interruptible_sleep(10)
# Start at the restored zero field and move monotonically up. Total 0->6.5 T
# bare field time = 6.5*7.3=47.45 min; the first 1.0176 T costs 7.43 min.
# First field move is in the sweep so the watcher sees the run immediately.
followed=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field]
for p in followed:
    s.fp(p)
    s.plot('time',p)
# Native layout: time, B_target, TG, BG, Ts, Tv, Itg, Ibg, X0, P0, X1, P1, B_read.
_fan_stop=[]
def fan_guard(station,data):
    try:
        for name in ('T_sample','T_vaporizer'):
            with contextlib.redirect_stdout(io.StringIO()):
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        assert np.all(np.isfinite(data)), 'nonfinite channel'
        assert 1<=data[4]<=1.5 and 0<data[5]<1.6 and abs(data[4]-data[5])<.6, 'base temperature lost'
        assert abs(data[6])<1e-9 and abs(data[7])<1e-9, 'gate current above established 1 nA trip'
        assert abs(data[8])<.85*_sens0 and abs(data[10])<.85*_sens1, 'lock-in headroom below 15 percent'
        assert 8e-9<data[8]/-1e6<12e-9, 'drain current outside 8..12 nA'
        assert abs(data[12]-data[1])<.03, 'field readback mismatch >30 mT'
    except Exception as exc:
        _fan_stop.append(str(exc))
        print('FAN STOP:',repr(exc),'at B/TG/BG=',data[1:4])
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
_fan_result=s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtgs,Vbgs],slow_delay=1.,fast_delay=3.)
print('FAN END:', 'STOP '+repr(_fan_stop) if _fan_stop else 'inspect completion metadata', 'file_id',_fan_result.id)
print('Actual field/gates/T:',magnet.field(),k_tg.volt(),k_bg.volt(),T_sample())
# Hold endpoints for analysis and an efficiently descending follow-up; no blind return.
