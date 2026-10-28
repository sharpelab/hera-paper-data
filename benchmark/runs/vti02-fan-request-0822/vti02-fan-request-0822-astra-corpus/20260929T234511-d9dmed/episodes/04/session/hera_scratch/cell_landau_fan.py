# landau-fan-vti: electron D~0 fan; run-5 calibration, run-6 shared-density anchor.
# Read-only preconditions before any instrument write.
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

def _fan_limits(p):
    return (float(p.vals._min_value), float(p.vals._max_value))
for _name, _p, _expected in [
    ('TG', k_2400_tg.volt, (-0.3, 1.0)), ('BG', k_2400_bg.volt, (-1.3, 2.0)),
    ('Si', dc205.smart_voltage, (-25.0, 25.0)), ('Si raw', dc205.voltage, (-25.0, 25.0)),
    ('field', magnet.field, (-10.0, 10.0)),
    ('sample setpoint', heater.sample_setpoint, (0.0, 100.0)),
    ('vaporizer setpoint', heater.vaporizer_setpoint, (0.0, 100.0))]:
    _actual = _fan_limits(_p)
    print(f'{_name}: expected validator {_expected}; actual {_actual}')
    assert _actual == _expected, f'SAFETIES mismatch: {_name}'
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
for _name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(_name, VTI.temp_logfile_candidates[_name], max_age=15, max_period=12)
_Ts, _Tv, _B0, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_hr = (heater.sample_range(), heater.vaporizer_range())
_ps = (magnet.persistent_switch_on(), magnet.output_enabled())
print(f'Expected base 1.0..1.5 K, vaporizer <1.6 K, B~0 (+/-0.02 T), Si=0 (+/-0.01 V), heaters off, PS/output on; actual {_Ts}, {_Tv}, {_B0}, {_Si}, {_hr}, {_ps}')
assert 1.0 <= _Ts <= 1.5 and 0 < _Tv < 1.6 and abs(_Tv-_Ts) < 0.6
assert abs(_B0) < 0.02 and abs(_Si) < 0.01 and _hr == (0,0) and all(_ps)
print('Expected fixed wiring T_0 -> B_3, sr1 B_1-B_2; actual', WIRING)
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2', 'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert 'mux' not in globals()
print('Expected Si range/output/rate 2/1/0.5; actual',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range() == 2 and dc205.output() == 1 and dc205.ramp_rate == 0.5
print('Expected TG/BG step 0.005 V, NPLC 1; actual',k_tg.volt.step,k_bg.volt.step,k_tg.nplci(),k_bg.nplci())
assert k_tg.volt.step == 0.005 and k_bg.volt.step == 0.005
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
_drive, _freq = sr1.amplitude(), sr1.frequency()
print('Expected drive 1 V, 13.777 Hz; actual',_drive,_freq)
assert abs(_drive-1.0) < 1e-6 and abs(_freq-13.777) < 0.01
for _li in (sr0,sr1):
    _tau, _slope = _li.time_constant(), _li.filter_slope()
    print(f'{_li.name}: expected tau 0.3 s, slope 24 dB/oct; actual {_tau}, {_slope}')
    assert _tau == 0.3 and _slope == 24
assert meas_config['sr0_gain'] == -1e6 and meas_config['bias_resistor'] == 100e6 and meas_config['bias_channel'] == 'sr1'
print('Expected sr0 sensitivity 0.02 V; actual',sr0.sensitivity())
assert sr0.sensitivity() == 0.02

CAL_FAN = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
B_LO, B_HI = 1.0309096913954, 7.05
# Full nominal Luttinger frequency <=33.09 T; observed harmonic candidates extend to 130 T.
N_B = int(np.ceil((1/B_LO-1/B_HI)*2*130.0))+1
# Include +20% density-scale allowance in the density-axis ray-Nyquist floor.
N_N = int(np.ceil((3.2-2.8)*1.2/(B_LO/10.33916924/2)))+1
ns_fan = np.linspace(2.8,3.2,N_N)
B_fan = field_invB(B_LO,B_HI,N_B)
Vt_fan,Vb_fan = calc_gate_voltages(ns_fan,np.zeros_like(ns_fan),**CAL_FAN)
for _p,_vec in ((k_tg.volt,Vt_fan),(k_bg.volt,Vb_fan),(magnet.field,B_fan)):
    for _v in _vec: _p.validate(float(_v))
_nr,_Dr = calc_nD(Vt_fan,Vb_fan,**CAL_FAN)
assert np.allclose(_nr,ns_fan) and np.max(abs(_Dr)) < 1e-10
assert np.max(abs(np.diff(1/B_fan))) <= 1/(2*130)
assert 1.2*np.max(np.diff(ns_fan)) <= B_LO/10.33916924/2
print(f'Grid {N_B} x {N_N} = {N_B*N_N}; B {B_LO:.6f}->{B_HI:.2f} T; n_A 2.8..3.2e12, D_A~0; TG {Vt_fan.min():.5f}..{Vt_fan.max():.5f}, BG {Vb_fan.min():.5f}..{Vb_fan.max():.5f} V')

# Fixed range, unchanged excitation/filter/pacing. All elapsed waits are interruptible.
sr1.sensitivity(50e-6)
assert sr1.sensitivity() == 50e-6
mc_fan = dict(meas_config)
mc_fan.update({'Si (V)':_Si,'sample_temperature:':_Ts,'sr1_gain':1.0,
              'gate_calibration':CAL_FAN,'fan_density_1e12_cm2':ns_fan.tolist(),
              'comments':'electron D_A~0, n_A 2.8..3.2e12, B 1.0309097->7.05 T uniform 1/B; run-6 anchor; onset sensitivity remains a caveat',
              'lockin_tau_s':0.3,'lockin_slope_db_oct':24,'settling_s':3.0})
s = sweep.AsyncStation(mc_fan)
s.add_comment('landau-fan-vti')
s.add_comment(f'n_A=+2.8..+3.2e12 cm^-2 ({N_N} pts); D_A=0 V/nm; B={B_LO:.7f}->7.05 T ({N_B} rows uniform 1/B); Si=0 V; 10 nA; sr1=50 uV; fast dwell=3 s=10 tau; run-5 calibration; run-6 shared n=3.2 anchor; positive B only')
s.ramp(k_bg.volt,float(Vb_fan[0])); s.ramp(k_tg.volt,float(Vt_fan[0]))
interruptible_sleep(3)
# Position from measured ~0: 1.031 T * 7.3 min/T = 7.53 min + driver's 3 s settle.
magnet.field(B_LO)
print('Positioned field: expected',B_LO,'actual',magnet.field())
assert abs(magnet.field()-B_LO) < 0.02

# Layout: time,B_set,Vtg,Vbg,Ts,Tv,Itg,Ibg,X0,P0,X1,P1,B_read.
for _p in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P,magnet.field):
    s.fp(_p)
    s.plot('time',_p)  # Every recorded value is visible, including phase/temperature/readback.
_fan_stop = []
_fan_row = [None]
def _fan_guard(station,data):
    _b = float(data[1])
    if _fan_row[0] != _b:
        for _name in ('T_sample','T_vaporizer'):
            try:
                assert_thermometry_live(_name,VTI.temp_logfile_candidates[_name],max_age=15,max_period=12)
            except Exception as _err:
                _fan_stop.append(f'thermometry freshness: {_err}')
        _fan_row[0] = _b
    if not np.all(np.isfinite(np.asarray(data,dtype=float))): _fan_stop.append('nonfinite readback')
    if max(abs(data[6]),abs(data[7])) > 1e-9: _fan_stop.append('gate leakage >1 nA')
    if not (1.0 <= data[4] <= 1.5 and 0 < data[5] < 1.6): _fan_stop.append('off base temperature')
    if abs(data[10]) >= 0.9*50e-6 or abs(data[8]) >= 0.9*0.02: _fan_stop.append('lock-in near full scale')
    if not 8e-9 <= data[8]/-1e6 <= 12e-9: _fan_stop.append('drain current outside 8..12 nA')
    if abs(data[12]-_b) > 0.02: _fan_stop.append('field readback mismatch')
    if _fan_stop:
        print('FAN STOP:',_fan_stop)
        station.interrupt_requested = True
s.register_run_after(_fan_guard,())
_fan_result = s.multimegasweep([magnet.field],[B_fan],[k_tg.volt,k_bg.volt],[Vt_fan,Vb_fan],slow_delay=1,fast_delay=3)
print('Fan file_id',_fan_result.id,'interrupted',_fan_result.metadata.get('interrupted',False),'guards',_fan_stop)
# Hold endpoint deliberately; no automatic field retraverse or close-out.
print('Actual endpoint B,TG,BG,Si,Ts,Tv:',magnet.field(),k_tg.volt(),k_bg.volt(),k_si(),T_sample(),T_vaporizer())
