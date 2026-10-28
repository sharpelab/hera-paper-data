# Plan step 4: bipolar D~0 Landau fan; all instrument calls stay in measure.
# Preconditions first; no instrument writes until every check below passes.
import json
from pathlib import Path
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages

def _fan_expect(label, actual, expected, ok):
    print(f'{label}: actual={actual}; expected={expected}')
    assert ok, f'FAN PRECONDITION FAILED: {label}'

for _p, _limits in (
    (k_tg.volt, (-0.3, 1.0)), (k_bg.volt, (-1.3, 2.0)),
    (dc205.smart_voltage, (-25.0, 25.0)), (dc205.voltage, (-25.0, 25.0)),
    (magnet.field, (-10.0, 10.0)),
    (heater.sample_setpoint, (0.0, 100.0)), (heater.vaporizer_setpoint, (0.0, 100.0)),
):
    _actual = (float(_p.vals._min_value), float(_p.vals._max_value))
    _fan_expect(_p.full_name+' validator', _actual, _limits, _actual == _limits)
_fan_expect('session caps', (B_SESSION_CAP,T_SESSION_CAP), (10.,100.),
            (B_SESSION_CAP,T_SESSION_CAP) == (10.,100.))
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_fan_expect('sample temperature K', _Ts, '1.0..1.5', 1.0 <= _Ts <= 1.5)
_fan_expect('vaporizer temperature K', _Tv, '<1.6 and within 0.6 of sample',
            0 < _Tv < 1.6 and abs(_Tv-_Ts) < .6)
_fan_expect('handoff field T', _B, '|B|<0.03', abs(_B) < .03)
_ranges = (heater.sample_range(), heater.vaporizer_range())
_fan_expect('heater ranges', _ranges, (0,0), _ranges == (0,0))
_ps = (magnet.persistent_switch_on(), magnet.output_enabled())
_fan_expect('magnet switch/output', _ps, (True,True), all(_ps))
_si = (dc205.voltage_range(), dc205.output(), k_si(), dc205.ramp_rate)
_fan_expect('Si range/output/V/ramp_rate', _si, '(2,1,0,0.5)',
            _si[0] == 2 and _si[1] == 1 and abs(_si[2]) < .01 and _si[3] == .5)
_gate_state = (k_tg.volt(),k_bg.volt(),k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
_fan_expect('handoff TG/BG V, steps, NPLC', _gate_state, '(0,0,.005,.005,1,1)',
            abs(_gate_state[0]) < .001 and abs(_gate_state[1]) < .001 and _gate_state[2:] == (.005,.005,1.,1.))
_wiring_expected = {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                    'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
_fan_expect('hardwired contacts', WIRING, _wiring_expected, WIRING == _wiring_expected and 'mux' not in globals())
_drive = (sr1.amplitude(),sr1.frequency())
_fan_expect('drive V/Hz', _drive, '(1.0,13.777)', abs(_drive[0]-1.) < 1e-6 and abs(_drive[1]-13.777)<.01)
_acq = {name: {'tau':obj.time_constant(), 'slope':obj.filter_slope(), 'sensitivity':obj.sensitivity()}
        for name,obj in (('sr0',sr0),('sr1',sr1))}
_fan_expect('lock-in tau/slope', _acq, 'both 0.3 s / 24 dB per octave; sr0 20 mV',
            all(a['tau']==.3 and a['slope']==24 for a in _acq.values()) and _acq['sr0']['sensitivity']==.02)
_fan_expect('channel gains/bias', (meas_config['sr0_gain'],meas_config.get('sr1_gain',1.),meas_config['bias_resistor'],meas_config['bias_channel']),
            '(-1e6,1,1e8,sr1)', meas_config['sr0_gain']==-1e6 and meas_config.get('sr1_gain',1.)==1.
            and meas_config['bias_resistor']==1e8 and meas_config['bias_channel']=='sr1')

# Explicit calibration avoids the stale geometry-only `cal` from setup.
FAN_CAL = dict(c_tg=.0027960593093052633, c_bg=.002160696465377614,
               n_offset=-.08937933224099137, D_offset=-.013)
n_fan = np.linspace(-1.2,3.2,89)  # nominal 1e12 cm^-2; absolute scale provisional
Vtg_fan,Vbg_fan = calc_gate_voltages(n_fan,0.,**FAN_CAL)
B_fan = np.r_[0.,.5,.75,1.,field_invB(1.25,6.,103)]
for _p,_vec in ((k_tg.volt,Vtg_fan),(k_bg.volt,Vbg_fan),(magnet.field,B_fan)):
    for _v in _vec:
        _p.validate(float(_v))
print(f'FAN GRID: {len(B_fan)} x {len(n_fan)} = {len(B_fan)*len(n_fan)} points; '
      f'TG {Vtg_fan.min():+.6f}..{Vtg_fan.max():+.6f} V; BG {Vbg_fan.min():+.6f}..{Vbg_fan.max():+.6f} V; '
      f'B {_B:+.4f}->6 T; bare ramp floor {(6-_B)*7.3:.1f} min')

# Restore useful headroom after state0 replay (which restored sr1 to 2 uV).
sr1.sensitivity(100e-6)
_fan_expect('sr1 sensitivity V',sr1.sensitivity(),.0001,sr1.sensitivity()==.0001)
_acq['sr1']['sensitivity']=sr1.sensitivity()
mc = dict(meas_config)
mc.update({'Si (V)':_si[2], 'sample_temperature:':_Ts, 'sr1_gain':1.,
           'fan_calibration':FAN_CAL, 'density_scale':'geometry anchored, provisional',
           'D_origin':'run 5 resistance-minimum proxy, provisional',
           'acquisition_readback':_acq, 'comments':'landau-fan: bipolar operational D~0; B 0..6 T; Si 0; base T'})
s = sweep.AsyncStation(mc, basedir=str(Path(main_dir)/'data'))
s.add_comment('landau-fan')
s.add_comment('plan step 4; B_1-B_2; n_A nominal -1.2..+3.2e12 cm^-2 (89, step .05); D proxy 0 V/nm; '
              'B context 0,.5,.75,1 T then 103 inverse-B rows 1.25..6 T; TG -0.277033..0.983594 V, '
              'BG -0.465040..1.166281 V; Si 0 V; 3 s fast + 3 s row dwell; '
              'sr1 100 uV, tau .3 s/24 dB; run-5 calibration; gates retain .005 V pacing')
s.ramp(k_bg.volt,float(Vbg_fan[0])); s.ramp(k_tg.volt,float(Vtg_fan[0]))
interruptible_sleep(10)
# Raw X is stored with gain=1; metadata carries physical preamp gains for analysis.
_followed = [T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,
             magnet.field,k_tg.volt,k_bg.volt]
for _p in _followed:
    s.fp(_p)
    s.plot('time',_p)
_fan_index = {p.full_name:4+i for i,p in enumerate(_followed)}
_fan_guard = {'points':0, 'reason':None}

def _fan_check_after(station,data):
    def value(p):
        return float(data[_fan_index[p.full_name]])
    issues=[]
    if not np.isfinite(np.asarray(data,dtype=float)).all(): issues.append('nonfinite data')
    if abs(value(k_tg.curr))>1e-9 or abs(value(k_bg.curr))>1e-9: issues.append('gate leakage >1 nA')
    _idrain=value(sr0.X)/mc['sr0_gain']
    if not 5e-9 < _idrain < 15e-9: issues.append('drain outside 5..15 nA')
    if abs(value(sr0.X))>.9*_acq['sr0']['sensitivity'] or abs(value(sr1.X))>.9*_acq['sr1']['sensitivity']:
        issues.append('lock-in >90% full scale')
    if not 1.0 <= value(T_sample) <= 1.5 or not 0 < value(T_vaporizer) < 1.6:
        issues.append('base temperature failed')
    if abs(value(magnet.field)-float(data[1]))>.03: issues.append('field mismatch >30 mT')
    if abs(value(k_tg.volt)-float(data[2]))>.003 or abs(value(k_bg.volt)-float(data[3]))>.003:
        issues.append('gate readback mismatch >3 mV')
    # Check advancing worker files once per row; no extra instrument driver imports.
    if _fan_guard['points'] % len(n_fan)==0:
        try:
            for name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        except Exception as exc:
            issues.append(f'thermometry freshness: {exc}')
    _fan_guard['points'] += 1
    if issues:
        _fan_guard['reason']='; '.join(issues)
        print('FAN STOP:',_fan_guard['reason'],'B/TG/BG=',data[1:4],flush=True)
        station.interrupt_requested=True
s.register_run_after(_fan_check_after,())
try:
    fan_result=s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],
                               [Vtg_fan,Vbg_fan],slow_delay=3.,fast_delay=3.)
finally:
    print('FAN final readback:', {'B_T':magnet.field(),'TG_V':k_tg.volt(),'BG_V':k_bg.volt(),
          'Si_V':k_si(),'Ts_K':T_sample(),'Tv_K':T_vaporizer(),'guard_reason':_fan_guard['reason']},flush=True)
# No blind park: next field trajectory starts from this measured endpoint.
