# Plan step 4: landau-fan; only this measure cell touches instruments.
import numpy as np
from scipy.constants import e, epsilon_0

# Read-only preflight: print expected and actual before any write.
for label in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(label, VTI.temp_logfile_candidates[label], max_age=15, max_period=12)
Ts, Tv, B0, Si0 = T_sample(), T_vaporizer(), magnet.field(), k_si()
ranges = (heater.sample_range(), heater.vaporizer_range())
ps, output = magnet.persistent_switch_on(), magnet.output_enabled()
print('Expected base Ts 1.0..1.5 K, Tv <1.6 K within 0.6 K of Ts, B=0 +/-0.02 T, Si=0 +/-0.01 V, heaters off, PS/output on')
print('Actual:', Ts, Tv, B0, Si0, ranges, ps, output, 'TG/BG:', k_tg.volt(), k_bg.volt())
assert 1 <= Ts <= 1.5 and 0 < Tv < 1.6 and abs(Ts-Tv)<0.6
assert abs(B0)<0.02 and abs(Si0)<0.01 and ranges==(0,0) and ps and output
checks=[(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
        (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
        (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
        (heater.vaporizer_setpoint,(0.,100.))]
for param,expected in checks:
    actual=(float(param.vals._min_value),float(param.vals._max_value))
    print(param.full_name,'validator expected',expected,'actual',actual)
    assert actual==expected
assert B_SESSION_CAP==10.0 and T_SESSION_CAP==100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
print('Expected TG/BG steps 0.005 V; Si rate 0.5 V/s, range 2, output 1; actual',k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate,dc205.voltage_range(),dc205.output())
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005 and dc205.ramp_rate==0.5
assert dc205.voltage_range()==2 and dc205.output()==1
print('Expected NPLC=1/1, actual', k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
amp,freq=sr1.amplitude(),sr1.frequency()
taus=(sr0.time_constant(),sr1.time_constant()); slopes=(sr0.filter_slope(),sr1.filter_slope())
print('Expected drive 1 V/13.777 Hz, tau 0.3/0.3 s, slopes 24/24; actual',amp,freq,taus,slopes)
assert abs(amp-1.)<1e-6 and abs(freq-13.777)<0.01 and taus==(0.3,0.3) and slopes==(24,24)

# Explicit run-5 calibration; density is a provisional coordinate (SI internally).
ct,cb=0.0027960593093052633,0.002160696465377614
n0,D0=-0.08937933224099137e16,-0.013e9
n_vec=np.linspace(-1.2,3.2,111)*1e16
Vtg_vec=(e*(n_vec-n0)+2*epsilon_0*(0-D0))/(2*ct)
Vbg_vec=(e*(n_vec-n0)-2*epsilon_0*(0-D0))/(2*cb)
B_vec=np.r_[0.,np.round(np.linspace(1.,6.,51),3)]
for param,vec in [(k_tg.volt,Vtg_vec),(k_bg.volt,Vbg_vec),(magnet.field,B_vec)]:
    for value in vec: param.validate(float(value))
print('52 B rows x 111 gate points; TG endpoints',Vtg_vec[[0,-1]],'BG endpoints',Vbg_vec[[0,-1]])
print('B 0 -> 6 T bare ramp floor 43.8 min; 0 -> 1 T first row transition 7.3 min; then 0.1 T = 43.8 s each plus settle')
FAST_DELAY,SLOW_DELAY=3.0,3.0
# Fixed headroom: 100 uV voltage = 10 kohm at 10 nA; 20 mV current channel.
sr1.sensitivity(100e-6); sr0.sensitivity(0.02)
assert sr1.sensitivity()==100e-6 and sr0.sensitivity()==0.02
mc=dict(meas_config)
mc.update({'sr1_gain':1.,'Si (V)':Si0,'sample_temperature:':Ts,
 'calibration':{'source_run':5,'c_tg':ct,'c_bg':cb,'n_offset_m-2':n0,'D_offset_V/m':D0,'absolute_scale':'geometry prior; nominal D=0'},
 'settling':{'tau_s':list(taus),'slope_db_oct':list(slopes),'fast_delay_s':FAST_DELAY},
 'comments':'landau-fan B_1-B_2: B=0 then 1..6 T by 0.1; n=-1.2..3.2e12 by .04 nominal D=0; Si=0; 100uV/20mV sensitivity; 3s dwell'})
s=sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(mc['comments'])
s.ramp(k_bg.volt,float(Vbg_vec[0])); s.ramp(k_tg.volt,float(Vtg_vec[0]))
interruptible_sleep(10)
# Layout: time,Bset,TGset,BGset,Ts,Tv,Itg,Ibg,sr0X,sr0P,sr1X,sr1P,Bread
followed=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field]
for param in followed:
    s.fp(param)
    s.plot('time',param)
_fan_count=[0]
_fan_trips=[]
def fan_guard(station,data):
    v=np.asarray(data,dtype=float)
    problems=[]
    if not np.all(np.isfinite(v)): problems.append('nonfinite-data')
    if abs(v[6])>1e-9 or abs(v[7])>1e-9: problems.append('gate-leakage>1nA')
    if not (1<=v[4]<=1.5 and 0<v[5]<1.6 and abs(v[4]-v[5])<0.6): problems.append('off-base-temperature')
    if not (5e-9<v[8]/mc['sr0_gain']<12e-9): problems.append('drain-current-outside-5..12nA')
    if abs(v[8])>0.9*0.02 or abs(v[10])>0.9*100e-6: problems.append('clipping-headroom')
    if abs(v[12]-v[1])>0.05: problems.append('field-readback-mismatch')
    if _fan_count[0]%len(n_vec)==0:
        try:
            for label in ('T_sample','T_vaporizer'):
                assert_thermometry_live(label,VTI.temp_logfile_candidates[label],max_age=15,max_period=12)
        except Exception as exc: problems.append('thermometry-stale: '+str(exc))
    _fan_count[0]+=1
    if problems:
        _fan_trips.extend(problems)
        print('FAN STOP',problems,'B/TG/BG:',v[1:4],flush=True)
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
try:
    fan_result=s.multimegasweep([magnet.field],[B_vec],[k_tg.volt,k_bg.volt],[Vtg_vec,Vbg_vec],slow_delay=SLOW_DELAY,fast_delay=FAST_DELAY)
finally:
    # Read actual state after completion/abort. No automatic field retraverse.
    print('FAN READBACK B/TG/BG/Si/Ts/Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer(),flush=True)
    print('FAN GUARD EVENTS:',_fan_trips,flush=True)
