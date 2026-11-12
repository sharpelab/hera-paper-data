# Plan step 4: bipolar Landau fan; all instrument access stays in measure.
from scipy.constants import e, epsilon_0

# Read-only preflight: committed validators, inherited state, and acquisition.
for _p, _expected in [(k_tg.volt, (-0.3, 1.0)), (k_bg.volt, (-1.3, 2.0)),
        (dc205.smart_voltage, (-25., 25.)), (dc205.voltage, (-25., 25.)),
        (magnet.field, (-10., 10.)), (heater.sample_setpoint, (0., 100.)),
        (heater.vaporizer_setpoint, (0., 100.))]:
    _actual = (float(_p.vals._min_value), float(_p.vals._max_value))
    print('validator', _p.full_name, 'expected', _expected, 'actual', _actual)
    assert _actual == _expected
assert B_SESSION_CAP == 10. and T_SESSION_CAP == 100.
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert k_tg.volt.step == k_bg.volt.step == 0.005 and dc205.ramp_rate == 0.5
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_Si, _rng, _out = k_si(), dc205.voltage_range(), dc205.output()
_hr = (heater.sample_range(), heater.vaporizer_range())
_ps, _enabled = magnet.persistent_switch_on(), magnet.output_enabled()
print('expected base T 1.0-1.5 K, vaporizer <1.6 K and within 0.6 K:', _Ts, _Tv)
print('expected |B|<0.02 T, Si=0 V, RNGE=2/on, heaters=0/0, PS/output=True:',
      _B, _Si, _rng, _out, _hr, _ps, _enabled)
print('starting TG/BG (set below):', k_tg.volt(), k_bg.volt())
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts) < 0.6
assert abs(_B) < .02 and abs(_Si) < .01 and _rng == 2 and _out == 1
assert _hr == (0, 0) and _ps and _enabled
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
_amp, _freq = sr1.amplitude(), sr1.frequency()
_taus = (sr0.time_constant(), sr1.time_constant())
_slopes = (sr0.filter_slope(), sr1.filter_slope())
_nplc = (k_tg.nplci(), k_bg.nplci())
print('expected drive 1 V/13.777 Hz; tau .3/.3 s, slopes 24/24, NPLC 1/1:',
      _amp, _freq, _taus, _slopes, _nplc)
assert abs(_amp-1.) < .001 and abs(_freq-13.777) < .01
assert _taus == (.3, .3) and _slopes == (24, 24) and _nplc == (1., 1.)
assert abs(sr0.sensitivity()-.02) < 1e-9
assert meas_config['sr0_gain'] == -1e6 and meas_config.get('sr1_gain',1.) == 1.
assert meas_config['bias_channel'] == 'sr1' and meas_config['bias_resistor'] == 100e6

# SI calibration algebra; density and D labels remain provisional (run 5).
_ct, _cb = .0027960593093052633, .002160696465377614
_n0, _D0 = -.08937933224099137e16, -.013e9
n_fan = np.linspace(-1.2, 3.2, 111)  # display units 1e12 cm^-2
_charge = e * (n_fan*1e16 - _n0)
_imbalance = 2*epsilon_0*(0. - _D0)
vt_fan = (_charge + _imbalance)/(2*_ct)
vb_fan = (_charge - _imbalance)/(2*_cb)
B_fan = np.r_[0., 1., 1.5, field_invB(2., 10., 65)]
for _param, _vec in ((k_tg.volt, vt_fan), (k_bg.volt, vb_fan), (magnet.field, B_fan)):
    for _value in _vec:
        _param.validate(float(_value))
print('fan shape:', len(B_fan), 'x', len(n_fan), '; TG', vt_fan[[0,-1]], 'BG', vb_fan[[0,-1]])
assert np.allclose((_ct*vt_fan+_cb*vb_fan)/e+_n0, n_fan*1e16)
assert np.max(np.abs((_ct*vt_fan-_cb*vb_fan)/(2*epsilon_0)+_D0)) < 1e-6

sr1.sensitivity(100e-6)  # acquisition headroom, no limit/pacing change
assert sr1.sensitivity() == 100e-6
mc = dict(meas_config)
mc.update({'Si (V)': _Si, 'sample_temperature:': _Ts, 'sr1_gain': 1.,
           'comments': 'Bipolar D~0 Landau fan, B_1-B_2; calibration run 5; absolute scale provisional',
           'fan_calibration': {'c_tg':_ct, 'c_bg':_cb, 'n_offset_m-2':_n0, 'D_offset_V/m':_D0},
           'fan_nominal_n_1e12_cm-2': n_fan.tolist(), 'fan_nominal_D_V/nm': 0.,
           'lockin_tau_s': list(_taus), 'lockin_filter_dB': list(_slopes), 'gate_NPLC': list(_nplc)})
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment('B_1-B_2; B=0,1,1.5 T then 65 inverse-B points 2->10 T; n=-1.2..3.2e12 cm^-2 in .04e12 steps; nominal D=0; Si=0; base T; 3 s dwell; sr1=100 uV; run-5 calibration; 68x111')
# Raw lock-in values stored with fp gain=1; channel gains are in metadata.
_follow = [T_sample, T_vaporizer, k_tg.curr, k_bg.curr, sr0.X, sr0.P,
           sr1.X, sr1.P, magnet.field, k_tg.volt, k_bg.volt, k_si]
for _param in _follow:
    s.fp(_param)
    s.plot('time', _param)
s.ramp(k_bg.volt, float(vb_fan[0]))
s.ramp(k_tg.volt, float(vt_fan[0]))
interruptible_sleep(10)

_fan_trip = []
_last_freshness = [0.]
def _fan_freshness(station):
    if time.monotonic() - _last_freshness[0] > 60:
        for _name in ('T_sample', 'T_vaporizer'):
            assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
        _last_freshness[0] = time.monotonic()

def _fan_guard(station, data):
    # [time, B_set, TG_set, BG_set, followed values in the order above]
    ts, tv, it, ib, x0, p0, x1, p1, bm, tg, bg, si = map(float, data[4:])
    reasons = []
    if not np.all(np.isfinite(data)): reasons.append('nonfinite readback')
    if abs(it)>1e-9 or abs(ib)>1e-9: reasons.append('gate leakage >1 nA')
    if abs(x0)>=.9*.02 or abs(x1)>=.9*100e-6: reasons.append('lock-in headroom <10%')
    if not 5e-9 < x0/mc['sr0_gain'] < 15e-9: reasons.append('drain current outside 5-15 nA')
    if not (1.0 <= ts <= 1.5 and 0 < tv < 1.6 and abs(tv-ts)<.6): reasons.append('base temperature mismatch')
    if abs(bm-float(data[1]))>.02: reasons.append('field mismatch >20 mT')
    if abs(tg-float(data[2]))>.003 or abs(bg-float(data[3]))>.003 or abs(si)>.01:
        reasons.append('gate readback mismatch')
    if reasons:
        _fan_trip.extend(reasons)
        print('FAN STOP:', reasons, 'B readback', bm, 'gates', tg,bg,si, 'T',ts,tv)
        station.interrupt_requested = True
s.register_run_before(_fan_freshness, ())
s.register_run_after(_fan_guard, ())
fan_result = s.multimegasweep([magnet.field], [B_fan], [k_tg.volt,k_bg.volt],
                            [vt_fan,vb_fan], slow_delay=3., fast_delay=3.)
print('FAN RESULT', fan_result.id, 'interrupted', fan_result.metadata.get('interrupted'), 'trips', _fan_trip)
print('actual endpoint B/TG/BG/Si/Ts/Tv:', magnet.field(), k_tg.volt(), k_bg.volt(), k_si(), T_sample(), T_vaporizer())
