# Plan step 4 — both-carrier Landau fan; no safety or pacing changes.
import json
from pathlib import Path

# Read assumed state before any write.
for name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(name, VTI.temp_logfile_candidates[name], max_age=15, max_period=12)
Ts, Tv, B0 = T_sample(), T_vaporizer(), magnet.field()
si0 = k_si()
ranges = (heater.sample_range(), heater.vaporizer_range())
print(f'Expected base Ts 1.0..1.5 K, Tv<1.6 K, |B|<0.02 T, Si=0, heaters off; actual {Ts=}, {Tv=}, {B0=}, {si0=}, {ranges=}')
assert 1.0 <= Ts <= 1.5 and 0 < Tv < 1.6 and abs(Tv-Ts)<0.6
assert abs(B0)<0.02 and abs(si0)<0.01 and ranges==(0,0)
ps, output = magnet.persistent_switch_on(), magnet.output_enabled()
print('Expected PS/output on; actual', ps, output)
assert ps and output and not magnet.is_ramping()
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for param, bounds in [(k_tg.volt,(-0.3,1.0)),(k_bg.volt,(-1.3,2.0)),
                      (dc205.smart_voltage,(-25.,25.)),(dc205.voltage,(-25.,25.)),
                      (magnet.field,(-10.,10.)),(heater.sample_setpoint,(0.,100.)),
                      (heater.vaporizer_setpoint,(0.,100.))]:
    actual=(float(param.vals._min_value),float(param.vals._max_value))
    print(param.full_name,'expected validator',bounds,'actual',actual)
    assert actual==bounds
assert B_SESSION_CAP==10 and T_SESSION_CAP==100
print('Pacing expected TG/BG step 0.005 V, Si 0.5 V/s; actual',k_tg.volt.step,k_bg.volt.step,dc205.ramp_rate)
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005 and dc205.ramp_rate==0.5
assert dc205.voltage_range()==2 and dc205.output()==1
assert WIRING=={'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
amp, freq = sr1.amplitude(), sr1.frequency()
print('Expected drive 1 V / 13.777 Hz; actual',amp,freq)
assert abs(amp-1.)<1e-6 and abs(freq-13.777)<0.01
for inst in (sr0,sr1):
    tau,slope=inst.time_constant(),inst.filter_slope()
    print(inst.name,'expected tau 0.3 s / slope 24 dB; actual',tau,slope)
    assert tau==0.3 and slope==24
print('Expected NPLC 1/1; actual',k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci()==1 and k_bg.nplci()==1
assert meas_config['sr0_gain']==-1e6 and meas_config.get('sr1_gain',1)==1
assert meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

# Explicit SI inversion of session run-5 calibration; n* scale remains prior-anchored.
fc = json.loads((Path(main_dir)/'hera_scratch'/'cal_run5.json').read_text())
assert fc['run']==5 and abs(fc['ratio']-0.7727648902821315)<1e-9
n_star=np.linspace(-1.2,3.2,111)
charge=(n_star-fc['n_offset'])*1e16*cst.e
imbalance=(0.-fc['D_offset'])*1e9*2*cst.epsilon_0
fan_tg=(charge+imbalance)/(2*fc['c_tg'])
fan_bg=(charge-imbalance)/(2*fc['c_bg'])
fan_B=np.r_[0.,field_invB(1.5,10.,101)]
for param,vec in [(k_tg.volt,fan_tg),(k_bg.volt,fan_bg),(magnet.field,fan_B)]:
    for value in vec: param.validate(float(value))
    print(param.full_name,'planned min/max',float(vec.min()),float(vec.max()),'points',len(vec))
# Fixed 100 uV sensitivity protects CNP over the full density line (run 5).
sr1.sensitivity(100e-6)
assert sr1.sensitivity()==100e-6 and sr0.sensitivity()==0.02
mc=dict(meas_config)
mc.update({'Si (V)':si0,'sample_temperature:':Ts,'fan_calibration':fc,
           'nominal_density_units':'1e12 cm^-2; absolute scale geometry prior',
           'sr1_gain':1.,'sr0_tau':0.3,'sr1_tau':0.3,'filter_slope_dB':24,
           'comments':'landau-fan; B_1-B_2; inferred D=0; n* -1.2..3.2; Si=0; base T; run-5 calibration'})
s=sweep.AsyncStation(mc, basedir=str(Path(main_dir)/'data'))
s.add_comment('landau-fan')
s.add_comment('Plan step 4: B=0 baseline then 1.5->10 T, 101 uniform-1/B rows; n*=-1.2..3.2 x10^12 cm^-2, 111 points; inferred D=0; Si=0 V; 3 s dwell; 100 uV sr1; absolute density and D-zero provisional')
# Raw lock-in values (gain=1): analysis applies metadata gains once.
fan_follow=[T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field,k_tg.volt,k_bg.volt]
for p in fan_follow:
    s.fp(p)
    s.plot('time',p)
fan_index={p.full_name:4+i for i,p in enumerate(fan_follow)}
fan_count=0
fan_bad=0

def fan_before(station):
    global fan_count
    if fan_count%len(n_star)==0:
        for name in ('T_sample','T_vaporizer'):
            assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        print('Row',fan_count//len(n_star),'B actual',magnet.field(),'T',T_sample(),T_vaporizer())

def fan_after(station,data):
    global fan_count, fan_bad
    def val(p): return float(data[fan_index[p.full_name]])
    reasons=[]
    if max(abs(val(k_tg.curr)),abs(val(k_bg.curr)))>1e-9: reasons.append('gate leakage >1 nA')
    if not (1.0<=val(T_sample)<=1.5 and 0<val(T_vaporizer)<1.6): reasons.append('base temperature lost')
    if abs(val(magnet.field)-float(data[1]))>0.02: reasons.append('field mismatch >20 mT')
    if abs(val(k_tg.volt)-float(data[2]))>0.005 or abs(val(k_bg.volt)-float(data[3]))>0.005: reasons.append('gate readback mismatch')
    if abs(val(sr1.X))>0.9e-4 or abs(val(sr0.X))>0.018: reasons.append('lock-in headroom <10%')
    current=val(sr0.X)/mc['sr0_gain']
    if not 8e-9<current<12e-9: reasons.append('drain current outside 8..12 nA')
    fan_bad=fan_bad+1 if reasons else 0
    fan_count+=1
    if fan_bad>=2 or any('mismatch' in x or 'temperature' in x for x in reasons):
        print('FAN STOP:',reasons,'B target',data[1],flush=True)
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
s.ramp(k_bg.volt,float(fan_bg[0])); s.ramp(k_tg.volt,float(fan_tg[0]))
interruptible_sleep(10)
fan_result=s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_tg,fan_bg],slow_delay=3.,fast_delay=3.)
print('Fan result',fan_result.id,'interrupted',fan_result.metadata.get('interrupted'))
print('Actual endpoint B/TG/BG/Si/Ts/Tv',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
# Hold endpoint for analysis; no automatic retraverse or close-out.
