# landau-fan-vti: run-6 onset and run-5 calibration; E1 continuation.
# Preconditions first. No safety surfaces or gate pacing are changed.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
import warnings
from sharpelab_nb.thermometry import StaleThermometryWarning

for label, param, expected in [
    ('TG', k_tg.volt, (-0.3, 1.0)), ('BG', k_bg.volt, (-1.3, 2.0)),
    ('Si', dc205.smart_voltage, (-25., 25.)), ('Si raw', dc205.voltage, (-25., 25.)),
    ('B', magnet.field, (-10., 10.)),
    ('sample setpoint', heater.sample_setpoint, (0., 100.)),
    ('vaporizer setpoint', heater.vaporizer_setpoint, (0., 100.))]:
    actual = (float(param.vals._min_value), float(param.vals._max_value))
    print(f'{label} validator: expected {expected}, actual {actual}')
    assert actual == expected, f'{label} validator mismatch'
assert B_SESSION_CAP == 10. and T_SESSION_CAP == 100.
for name in ['T_sample', 'T_vaporizer']:
    assert_thermometry_live(name, VTI.temp_logfile_candidates[name], max_age=15, max_period=12)
_ts, _tv, _b, _si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_hr = (heater.sample_range(), heater.vaporizer_range())
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f'Expected base Ts 1.0-1.5 K, Tv<1.6 K, B~0 T, Si=0 V, heaters OFF, magnet ON; actual {_ts}, {_tv}, {_b}, {_si}, {_hr}, {_ps}, {_out}')
assert 1.0 <= _ts <= 1.5 and 0 < _tv < 1.6 and abs(_tv-_ts)<0.6
assert abs(_b)<0.05 and abs(_si)<0.01 and _hr==(0,0) and _ps and _out
assert dc205.voltage_range()==2 and dc205.output()==1 and dc205.ramp_rate==0.5
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2','sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain']==-1e6 and meas_config['bias_resistor']==100e6 and meas_config['bias_channel']=='sr1'
_acq = (sr1.amplitude(), sr1.frequency(), sr0.time_constant(), sr1.time_constant(), sr0.filter_slope(), sr1.filter_slope(), k_tg.nplci(), k_bg.nplci(), k_tg.volt.step, k_bg.volt.step)
print('Expected drive/timing: (1 V,13.777 Hz,0.3 s,0.3 s,24,24,1,1,0.005,0.005); actual', _acq)
assert np.allclose(_acq, (1.,13.777,.3,.3,24,24,1,1,.005,.005), rtol=0, atol=1e-6)
print('Starting gate readbacks (set by this cell next):',k_tg.volt(),k_bg.volt())

CAL_FAN = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137, D_offset=-0.013)
ns_fan = np.linspace(3.2, 2.7, 14)
B_fan = field_invB(1.017617880804576, 9.2, 120)
Vt_fan, Vb_fan = calc_gate_voltages(ns_fan, np.zeros_like(ns_fan), **CAL_FAN)
assert np.all((Vt_fan>=-0.3)&(Vt_fan<=1.0)) and np.all((Vb_fan>=-1.3)&(Vb_fan<=2.0))
assert np.all((B_fan>0)&(B_fan<=10)) and np.all(np.diff(B_fan)>0)
_nback, _dback = calc_nD(Vt_fan, Vb_fan, **CAL_FAN)
assert np.allclose(_nback,ns_fan) and np.max(np.abs(_dback))<1e-10
print('Fan: 120 B rows x 14 n columns; TG', Vt_fan.min(),Vt_fan.max(),'BG',Vb_fan.min(),Vb_fan.max())
print('Field ramp budget from actual state:',(9.2-_b)/(.137),'min, including initial positioning; no return traverse.')
# 50 uV gives 5 kOhm nominal FS. Run 6 max 530 Ohm at n=3.2;
# conservative low-n allowance 5x plus 3.2/2.7 scaling is 3.14 kOhm.
sr1.sensitivity(50e-6)
assert sr1.sensitivity()==50e-6 and sr0.sensitivity()==.02
B_fan_read = qcodes.Parameter('B_fan_read', unit='T', get_cmd=magnet.field)
mc_fan = dict(meas_config)
mc_fan.update({'Si (V)':_si, 'sample_temperature:':_ts, 'calibration_run':5,
               'calibration':CAL_FAN, 'density_units':'1e12 cm^-2',
               'density_setpoints':ns_fan.tolist(), 'D_V_per_nm':0.,
               'sr0_tau_s':.3, 'sr1_tau_s':.3, 'filter_slope_dB_oct':24,
               'comments':'landau-fan-vti; B_1-B_2; n_A=+3.2 to +2.7e12, D_A=0; B=1.0176178808 to 9.2 T, uniform 1/B 120x14; Vsi=0; 10nA; 3s dwell; 50uV sr1; cal run5; onset run6 b_hi=5'})
s = sweep.AsyncStation(mc_fan)
s.add_comment('landau-fan-vti')
s.add_comment(mc_fan['comments'])
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(B_fan_read)
for p in [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,B_fan_read]:
    s.plot('time',p)
s.plot(k_tg.volt,sr1.X)

_fan_count = 0
_fan_stop = []
def fan_guard(station, data, writer):
    global _fan_count
    _fan_count += 1
    d = dict(zip(writer.metadata['columns'],data))
    reasons=[]
    if abs(d['k_2400_tg_curr'])>1e-9 or abs(d['k_2400_bg_curr'])>1e-9: reasons.append('gate leakage >1nA')
    if not 1.0<=d['T_sample']<=1.5 or not 0<d['T_vaporizer']<1.6: reasons.append('temperature outside base window')
    if abs(d['sr1_X'])>=.9*50e-6 or abs(d['sr0_X'])>=.9*.02: reasons.append('lock-in nearing rail')
    if not 8e-9<d['sr0_X']/-1e6<12e-9: reasons.append('drain current outside 8-12 nA')
    if abs(d['B_fan_read']-d['magnet_field'])>.03: reasons.append('field readback mismatch >30mT')
    if not np.all(np.isfinite(data)): reasons.append('nonfinite measurement')
    if (_fan_count-1)%len(ns_fan)==0:
        try:
            for name in ['T_sample','T_vaporizer']:
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        except Exception as exc: reasons.append(str(exc))
    if reasons:
        _fan_stop.extend(reasons)
        print('FAN STOP:', '; '.join(reasons))
        station.interrupt_requested=True
s.register_run_after(fan_guard,())
# Position gates and field once. FastBi field calls block and settle themselves.
s.ramp(k_bg.volt,float(Vb_fan[0])); s.ramp(k_tg.volt,float(Vt_fan[0]))
interruptible_sleep(3)
# The writer opens before the first blocking ramp, so hera-watch sees this run.
_result_fan = s.multimegasweep([magnet.field],[B_fan], [k_tg.volt,k_bg.volt],
                             [Vt_fan,Vb_fan], slow_delay=1.,fast_delay=3.)
# Hold on interruption; no hidden return ramp or automatic recovery.
print('Fan endpoint B/TG/BG/Si:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si())
print('Fan guard reasons:',_fan_stop)
print('Fan finished; inspect metadata interrupted flag before the next move.')
