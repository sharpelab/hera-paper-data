# Plan step 4: fixed-D Landau fan, B_1-B_2, starting from handoff zero field.
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preconditions before any instrument writes.
for label, parameter, limits in (
    ('TG', k_tg.volt, (-0.3, 1.0)), ('BG', k_bg.volt, (-1.3, 2.0)),
    ('Si', dc205.smart_voltage, (-25.0, 25.0)), ('Si raw', dc205.voltage, (-25.0, 25.0)),
    ('B', magnet.field, (-10.0, 10.0)),
    ('T sample', heater.sample_setpoint, (0.0, 100.0)),
    ('T vaporizer', heater.vaporizer_setpoint, (0.0, 100.0))):
    actual = (float(parameter.vals._min_value), float(parameter.vals._max_value))
    print(f'{label} validator: expected {limits}, actual {actual}')
    assert actual == limits, f'{label} validator mismatch'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
for name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(name, VTI.temp_logfile_candidates[name], max_age=15, max_period=12)
_fan_Ts, _fan_Tv = T_sample(), T_vaporizer()
_fan_B0, _fan_Si = magnet.field(), k_si()
_fan_ps, _fan_output = magnet.persistent_switch_on(), magnet.output_enabled()
_fan_ranges = (heater.sample_range(), heater.vaporizer_range())
print(f'Expected base Ts 1.0..1.5 K, Tv<1.6 K within 0.6 K of sample, heaters 0/0; actual {_fan_Ts}, {_fan_Tv}, {_fan_ranges}')
print(f'Expected |B|<0.02 T, Si=0 V, PS/output on; actual {_fan_B0:+.5f}, {_fan_Si:+.4f}, {_fan_ps}/{_fan_output}')
print(f'Start gates TG/BG (will be set): {k_tg.volt():+.5f}/{k_bg.volt():+.5f} V')
assert 1.0 <= _fan_Ts <= 1.5 and _fan_Tv < 1.6 and abs(_fan_Tv-_fan_Ts)<0.6
assert _fan_ranges == (0, 0) and abs(_fan_B0)<0.02 and abs(_fan_Si)<0.01
assert _fan_ps and _fan_output
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
assert k_si is dc205.smart_voltage and k_tg is k_2400_tg and k_bg is k_2400_bg
_fan_wiring = {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
               'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
print(f'Expected hardwired contact map {_fan_wiring}; actual {WIRING}')
assert WIRING == _fan_wiring
_fan_drive, _fan_freq = sr1.amplitude(), sr1.frequency()
_fan_taus = (sr0.time_constant(), sr1.time_constant())
_fan_slopes = (sr0.filter_slope(), sr1.filter_slope())
_fan_nplc = (k_tg.nplci(), k_bg.nplci())
print(f'Expected drive 1 V/13.777 Hz, tau .3/.3 s, slope 24/24, NPLC 1/1; actual {_fan_drive}/{_fan_freq}, {_fan_taus}, {_fan_slopes}, {_fan_nplc}')
print(f'Gate pacing TG/BG: steps {k_tg.volt.step}/{k_bg.volt.step}, inter_delay {k_tg.volt.inter_delay}/{k_bg.volt.inter_delay}; unchanged')
assert abs(_fan_drive-1.0)<1e-6 and abs(_fan_freq-13.777)<0.01
assert _fan_taus == (0.3,0.3) and _fan_slopes == (24,24) and _fan_nplc == (1,1)
assert k_tg.volt.step==0.005 and k_bg.volt.step==0.005
assert meas_config['sr0_gain']==-1e6 and meas_config.get('sr1_gain',1)==1
assert meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'

FAN_CAL = dict(c_tg=0.0027960593093052633,c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137,D_offset=-0.013)
fan_n = np.linspace(-1.2, 3.2, 111)  # units 1e12 cm^-2, absolute scale provisional
fan_tg, fan_bg = calc_gate_voltages(fan_n, np.zeros_like(fan_n), **FAN_CAL)
fan_B = np.concatenate(([0.0,0.7,1.0,1.25], field_invB(1.5,4.0,61), np.linspace(4.2,10.0,30)))
assert len(fan_B)==95 and np.all(np.diff(fan_B)>0)
assert np.all((-0.3<=fan_tg)&(fan_tg<=1.0)) and np.all((-1.3<=fan_bg)&(fan_bg<=2.0))
assert np.all((0<=fan_B)&(fan_B<=10.0))
_check_n,_check_D = calc_nD(fan_tg,fan_bg,**FAN_CAL)
assert np.allclose(_check_n,fan_n) and np.max(np.abs(_check_D))<1e-10
print(f'Fan {len(fan_B)} x {len(fan_n)} points; TG {fan_tg[0]:+.6f}..{fan_tg[-1]:+.6f} V, BG {fan_bg[0]:+.6f}..{fan_bg[-1]:+.6f} V')
print('Ramp budget: 10 T * 7.3 A/T / (1 A/min) = 73 min; total estimate 12 h incl reads, 3 s dwell, flyback, margin')

# Acquisition settings only; no validator, gate pacing, or heater changes.
sr1.sensitivity(100e-6)
sr0.sensitivity(20e-3)
_fan_sens0, _fan_sens1 = sr0.sensitivity(),sr1.sensitivity()
assert np.isclose(_fan_sens0,20e-3) and np.isclose(_fan_sens1,100e-6)
mc = dict(meas_config)
mc.update({'Si (V)':_fan_Si, 'sample_temperature:':_fan_Ts, 'sr1_gain':1.0,
           'calibration':dict(FAN_CAL, source_run=5, absolute_scale='geometry prior', D_zero='working symmetry estimate'),
           'fan_n_1e12_cm2':fan_n.tolist(),'D_V_per_nm':0.0,
           'lockin_tau_s':list(_fan_taus),'lockin_slope_dB':list(_fan_slopes),
           'comments':'B_1-B_2; D~0; n -1.2..3.2e12 provisional; B 0..10 T ascending; Si0; 3s dwell; full accessible carrier signs'})
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('plan step 4; B_1-B_2; run5 working D=0; n_A=-1.2..+3.2e12 cm^-2,111 pts; B controls 0,.7,1,1.25; inverse-B 1.5..4T 61pts then4.2..10T 30pts; Si0; sr1 100uV; dwell3s; density scale geometry-prior')
# Raw lock-in channels: gains are applied only by downstream analysis.
_fan_follow = [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field,k_tg.volt,k_bg.volt]
for parameter in _fan_follow:
    s.fp(parameter)
    s.plot('time',parameter)
# Fixed point layout: time, Bset, TGset, BGset, then _fan_follow above.
_fan_count = 0
_fan_stop_reasons = []
def fan_guard(station, data):
    global _fan_count
    values=np.asarray(data,dtype=float)
    reasons=[]
    if not np.all(np.isfinite(values)): reasons.append('nonfinite data')
    if abs(values[6])>1e-9 or abs(values[7])>1e-9: reasons.append('gate current >1nA')
    if abs(values[8])>0.90*_fan_sens0 or abs(values[10])>0.90*_fan_sens1: reasons.append('lock-in headroom <10%')
    if values[8]/mc['sr0_gain']<5e-9: reasons.append('drain current <5nA')
    if not (1.0<=values[4]<=1.5 and values[5]<1.6 and abs(values[5]-values[4])<0.6): reasons.append('temperature outside base window')
    if abs(values[12]-values[1])>0.03: reasons.append('field readback mismatch >30mT')
    if abs(values[13]-values[2])>0.01 or abs(values[14]-values[3])>0.01: reasons.append('gate readback mismatch >10mV')
    if _fan_count % 10 == 0:
        try:
            for name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        except Exception as exc: reasons.append(str(exc))
    if _fan_count < 3 or _fan_count % len(fan_n)==len(fan_n)-1:
        print(f'FAN checkpoint point {_fan_count+1}: Bset/read={values[1]:.4f}/{values[12]:.4f}T, I={values[8]/mc["sr0_gain"]*1e9:.3f}nA, X={values[10]*1e6:.3f}uV, Ts={values[4]:.3f}K')
    _fan_count += 1
    if reasons:
        _fan_stop_reasons.extend(reasons)
        print('FAN STOP / E0 required:', '; '.join(reasons))
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
s.ramp(k_bg.volt,float(fan_bg[0])); s.ramp(k_tg.volt,float(fan_tg[0]))
interruptible_sleep(10)
fan_result=s.multimegasweep([magnet.field],[fan_B],[k_tg.volt,k_bg.volt],[fan_tg,fan_bg],slow_delay=3,fast_delay=3)
print(f'FAN result data/{fan_result.id}, interrupted={fan_result.metadata.get("interrupted")}, stops={_fan_stop_reasons}')
# Holds endpoint; no unattended return ramp. Interrupt does not stop a CAEN ramp.
print(f'Actual end state: B={magnet.field():+.5f}T, TG={k_tg.volt():+.5f}V, BG={k_bg.volt():+.5f}V, Si={k_si():+.4f}V, Ts={T_sample():.3f}K, Tv={T_vaporizer():.3f}K')
