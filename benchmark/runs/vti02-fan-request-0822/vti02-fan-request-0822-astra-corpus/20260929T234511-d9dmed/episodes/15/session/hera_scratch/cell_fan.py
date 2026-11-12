# landau-fan-vti: electron branch tracking; all hardware access stays in measure.
from pathlib import Path
from contextlib import redirect_stdout
import io
import time as fan_clock
import numpy as np
from hera.analysis import field_invB
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Read-only preflight; no writes before all checks pass.
for name in ('T_sample', 'T_vaporizer'):
    assert_thermometry_live(name, VTI.temp_logfile_candidates[name], max_age=15, max_period=12)
Ts, Tv, B0 = T_sample(), T_vaporizer(), magnet.field()
Si = dc205.smart_voltage()
ps, out = magnet.persistent_switch_on(), magnet.output_enabled()
ranges = (heater.sample_range(), heater.vaporizer_range())
print(f'Expected base Ts=1.0..1.5 K, Tv<1.6 K, |B|<0.02 T, Si=0 V, heaters off, PS/output on; actual {Ts=}, {Tv=}, {B0=}, {Si=}, {ranges=}, {ps=}, {out=}')
assert 1.0 <= Ts <= 1.5 and 0 < Tv < 1.6 and abs(Ts-Tv) < .6
assert abs(B0) < .02 and abs(Si) < .01 and ranges == (0,0) and ps and out
for param, expected in [(k_tg.volt,(-.3,1.0)), (k_bg.volt,(-1.3,2.0)),
                        (dc205.smart_voltage,(-25.,25.)), (dc205.voltage,(-25.,25.)),
                        (magnet.field,(-10.,10.)), (heater.sample_setpoint,(0.,100.)),
                        (heater.vaporizer_setpoint,(0.,100.))]:
    actual = (float(param.vals._min_value), float(param.vals._max_value))
    print(param.full_name, 'validator expected',expected,'actual',actual)
    assert actual == expected
assert B_SESSION_CAP == 10 and T_SESSION_CAP == 100
assert k_tg is k_2400_tg and k_bg is k_2400_bg and k_si is dc205.smart_voltage
assert WIRING == {'source':'T_0','drain':'B_3','sr1+':'B_1','sr1-':'B_2',
                  'sr2+':'n.c.','sr2-':'n.c.','sr3+':'n.c.','sr3-':'n.c.'}
assert meas_config['sr0_gain'] == -1e6 and meas_config['bias_resistor'] == 100e6 and meas_config['bias_channel'] == 'sr1'
for lk in (sr0,sr1):
    tau, slope = lk.time_constant(), lk.filter_slope()
    print(lk.name, 'expected tau=.3 s, slope=24 dB/oct; actual',tau,slope)
    assert abs(tau-.3) < 1e-6 and slope == 24
amp, hz = sr1.amplitude(), sr1.frequency()
print('Expected drive 1 V / 13.777 Hz; actual',amp,hz)
assert abs(amp-1.) < 1e-6 and abs(hz-13.777) < .01
print('Expected Si range=2, output=1, ramp_rate=.5; actual',dc205.voltage_range(),dc205.output(),dc205.ramp_rate)
assert dc205.voltage_range() == 2 and dc205.output() == 1 and dc205.ramp_rate == .5
assert k_tg.volt.step == .005 and k_bg.volt.step == .005
print('Expected gate NPLC=1; actual',k_tg.nplci(),k_bg.nplci())
assert k_tg.nplci() == 1 and k_bg.nplci() == 1

CAL_FAN = dict(c_tg=.002796, c_bg=.002161, n_offset=-.0894, D_offset=-.013)
ns_fan = np.linspace(2.8,3.2,11)
Vtgs_fan, Vbgs_fan = calc_gate_voltages(ns_fan,np.zeros_like(ns_fan),**CAL_FAN)
B_lo_fan = 1.017617880804576  # run 6, sdh_onset(b_hi=5, bg_degree=5)
B_hi_fan = 6.4689868523317715 # nominal ABAB partner at n=2.8: exactly 5 periods
B_vec_fan = field_invB(B_lo_fan,B_hi_fan,113)
assert np.all((Vtgs_fan>=-.3)&(Vtgs_fan<=1.)) and np.all((Vbgs_fan>=-1.3)&(Vbgs_fan<=2.))
assert B_vec_fan.min() > 0 and B_vec_fan.max() <= 10
n_back,D_back = calc_nD(Vtgs_fan,Vbgs_fan,**CAL_FAN)
assert np.allclose(n_back,ns_fan) and np.allclose(D_back,0)
f_guard = 1.2*(3.2+.426297538)*10.33916924
assert np.max(np.abs(np.diff(1/B_vec_fan))) <= 1/(3*f_guard)
assert 1.2*np.max(np.diff(ns_fan)) <= B_lo_fan/10.33916924/2
print('Fan 113 B x 11 n; n range',ns_fan[[0,-1]],'TG',Vtgs_fan[[0,-1]],'BG',Vbgs_fan[[0,-1]])
print('B range',B_vec_fan[[0,-1]],'ramp floor from actual B (min)',abs(B_hi_fan-B0)*7.3)

# Acquisition only: no validator, operating limit, gate step, or Si ramp edits.
sr0.sensitivity(.02)
sr1.sensitivity(50e-6) # same as spot checks: 5 kOhm nominal FS
mc = dict(meas_config)
mc.update({'Si (V)':Si, 'sample_temperature:':Ts, 'sr1_gain':1,
           'gate_calibration':CAL_FAN, 'n_values_1e12_cm2':ns_fan.tolist(),
           'point_dwell_s':3.0, 'sr0_tau_s':.3, 'sr1_tau_s':.3,
           'comments':'electron D~0 fan; n 2.8..3.2e12; run-5 calibration; 113 uniform-inverse-B rows x 11 densities; B 1.017617881..6.468986852 T; spot runs 6/7'})
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('n=+2.8..+3.2e12 cm^-2 (11); D=0 V/nm region-A run-5 calibration; B=1.017617881..6.468986852 T (113 uniform 1/B); Si=0; base T; sr1 B_1-B_2, source T_0, drain B_3; 3 s dwell; 50 uV sensitivity; gates/field stay at endpoint')
# Row: time, B_target, Vtg, Vbg, Ts, Tv, Itg, Ibg, sr0X, sr0P, sr1X, sr1P.
for param in (T_sample,T_vaporizer,k_tg.curr,k_bg.curr,sr0.X,sr0.P,sr1.X,sr1.P):
    s.fp(param)
    s.plot('time',param) # every followed value visible live
s.plot(k_tg.volt,magnet.field,sr1.X)
fan_guard_state = {'point':0,'last_freshness':-np.inf,'stop':[]}
def fan_before(station):
    # Explicit interruptible 10-tau settling at every gate point.
    interruptible_sleep(3.0)
    if fan_clock.monotonic()-fan_guard_state['last_freshness'] >= 10:
        with redirect_stdout(io.StringIO()):
            for name in ('T_sample','T_vaporizer'):
                assert_thermometry_live(name,VTI.temp_logfile_candidates[name],max_age=15,max_period=12)
        fan_guard_state['last_freshness'] = fan_clock.monotonic()
def fan_after(station,data):
    reasons=[]
    if not np.all(np.isfinite(np.asarray(data,dtype=float))): reasons.append('nonfinite read')
    if not 1.0 <= data[4] <= 1.5 or not 0 < data[5] < 1.6: reasons.append('temperature off base')
    if max(abs(data[6]),abs(data[7])) > 1e-9: reasons.append('gate current >1 nA')
    if abs(data[8]) >= .018 or abs(data[10]) >= 45e-6: reasons.append('lock-in >=90% full scale')
    current=data[8]/(-1e6)
    if not 8e-9 <= current <= 12e-9: reasons.append('drain current outside 8..12 nA')
    if fan_guard_state['point'] % len(ns_fan) == 0:
        actual_B=magnet.field()
        print(f'ROW B target={data[1]:.6f}, measured={actual_B:.6f} T')
        if abs(actual_B-data[1]) > .02: reasons.append('field readback mismatch >20 mT')
    fan_guard_state['point'] += 1
    if reasons:
        fan_guard_state['stop'].extend(reasons)
        print('FAN STOP:',reasons,'at B',data[1])
        station.interrupt_requested=True
s.register_run_before(fan_before,())
s.register_run_after(fan_after,())
s.ramp(k_bg.volt,float(Vbgs_fan[0])); s.ramp(k_tg.volt,float(Vtgs_fan[0]))
# First slow-axis set positions from the measured ~0 T; no extra ramp or wait.
fan_result=s.multimegasweep([magnet.field],[B_vec_fan],[k_tg.volt,k_bg.volt],
                           [Vtgs_fan,Vbgs_fan],slow_delay=1,fast_delay=0)
print('FAN END:', 'STOPPED '+str(fan_guard_state['stop']) if fan_result.metadata.get('interrupted') else 'COMPLETE')
print('Actual endpoint B, TG, BG:',magnet.field(),k_tg.volt(),k_bg.volt())
# Hold endpoints for the next deliberate decision; never silently re-traverse.
