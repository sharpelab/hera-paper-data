# === Electron D=0 FS-count fan (`landau-fan-vti`): n +2.4..+3.2e12, B 0.7->10 T ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Run-5 region-A calibration: ratio data-calibrated, absolute scale geometry-prior.
CAL_FAN = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)

# Preconditions: inherited state that this cell does not set.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_t, _tv, _b, _si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_drive, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
_tg_nplc, _bg_nplc = k_tg.nplci(), k_bg.nplci()
print(f'precondition sample {_t:.3f} K [1.0,1.5], vaporizer {_tv:.3f} K [0.7,1.4], '
      f'field {_b:+.4f} T [|B|<0.05], Si {_si:+.4f} V [|Si|<0.01]')
print(f'precondition PS heater {_ps} [True], output {_out} [True], '
      f'drive {_drive:.3f} V [1.0], tau {_tau:.3f} s [0.3], '
      f'slope {_slope} dB/oct [24], TG/BG NPLC {_tg_nplc}/{_bg_nplc} [1/1]')
assert 1.0 <= _t <= 1.5 and 0.7 <= _tv <= 1.4 and abs(_b) < 0.05 and abs(_si) < 0.01
assert _ps and _out and abs(_drive - 1.0) < 0.005 and abs(_tau - 0.3) < 1e-6 and _slope == 24
assert _tg_nplc == 1 and _bg_nplc == 1
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0

ns_fan = np.linspace(2.4, 3.2, 25)  # 1e12 cm^-2; 2.03 points/filling ray at 0.7 T
Ds_fan = np.zeros_like(ns_fan)
Vtg_fan, Vbg_fan = calc_gate_voltages(ns_fan, Ds_fan, CAL_FAN['c_tg'], CAL_FAN['c_bg'],
                                      CAL_FAN['n_offset'], CAL_FAN['D_offset'])
assert np.all((Vtg_fan >= TG_MIN) & (Vtg_fan <= TG_MAX))
assert np.all((Vbg_fan >= BG_MIN) & (Vbg_fan <= BG_MAX))
_ncheck, _dcheck = calc_nD(Vtg_fan, Vbg_fan, CAL_FAN['c_tg'], CAL_FAN['c_bg'],
                            CAL_FAN['n_offset'], CAL_FAN['D_offset'])
assert np.allclose(_ncheck, ns_fan) and np.max(np.abs(_dcheck)) < 1e-9
B_fan = field_invB(0.7, 10.0, 133)
assert B_fan[0] > 0 and B_fan[-1] <= B_SESSION_CAP and np.all(np.diff(B_fan) > 0)
FAST_DELAY, SLOW_DELAY, I_TRIP = 1.8, 1.0, 1e-9  # 6tau at 24 dB/oct
print(f'grid: {len(B_fan)} B rows x {len(ns_fan)} n points = {len(B_fan)*len(ns_fan)}; '
      f'B {B_fan[0]:.3f}->{B_fan[-1]:.3f} T, n {ns_fan[0]:.2f}->{ns_fan[-1]:.2f}e12')
print(f'gate line: TG {Vtg_fan[0]:+.4f}->{Vtg_fan[-1]:+.4f} V; '
      f'BG {Vbg_fan[0]:+.4f}->{Vbg_fan[-1]:+.4f} V; max |D|={np.max(np.abs(_dcheck)):.2e} V/nm')

# Fixed range precedes all gate/field motion. Sr0 remains at the operator's 20 mV range.
sr1.sensitivity(50e-6)
assert abs(sr1.sensitivity() - 50e-6) < 1e-9 and abs(sr0.sensitivity() - 0.02) < 1e-6
print(f'ranges: sr1 {sr1.sensitivity():.2e} V (5 kΩ at 10 nA), sr0 {sr0.sensitivity():.3f} V')

mc = dict(meas_config); mc['Si (V)'] = _si; mc['sample_temperature:'] = _t
mc['comments'] = ('landau-fan-vti FS count, electron region A: D=0, n=+2.4..+3.2e12 cm^-2 '
                  '(25 pts), B=0.7..10 T (133 uniform-1/B rows), Si=0, sr1 50uV, '
                  'fast_delay=1.8s; run-5 cal ratio=0.773, absolute scale geometry-prior')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('landau-fan')
s.add_comment('FS-count electron; n +2.4..+3.2e12 cm^-2 (25), D 0 V/nm; '
              'B +0.7->+10 T (133 uniform-1/B); TG +0.7544..+0.9836 V, '
              'BG +0.8697..+1.1663 V; Si 0; run 5 cal; sr1 50 uV, 10 nA; '
              'fast_delay 1.8 s, slow_delay 1 s')

# Data layout: [time, B, Vtg, Vbg, T_sample, T_vaporizer,
#               I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P].
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample); s.plot('time', T_vaporizer)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_leak_guard(station, data):
    i_tg, i_bg = abs(float(data[6])), abs(float(data[7]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f'LEAK TRIP at B={float(data[1]):+.3f} T, TG={float(data[2]):+.4f} V, '
              f'BG={float(data[3]):+.4f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

try:
    s.ramp(k_bg.volt, Vbg_fan[0]); s.ramp(k_tg.volt, Vtg_fan[0])
    interruptible_sleep(10)
    _itg, _ibg = k_tg.curr(), k_bg.curr()
    print(f'start gate-current check: TG {_itg*1e12:+.0f} pA, BG {_ibg*1e12:+.0f} pA [<1 nA]')
    assert abs(_itg) < I_TRIP and abs(_ibg) < I_TRIP
    magnet.field(float(B_fan[0]))  # blocking ramp + driver settle; no separate wait
    print(f'field at fan start: {magnet.field():+.4f} T [0.7±0.05]')
    assert abs(magnet.field() - B_fan[0]) < 0.05
    s.multimegasweep([magnet.field], [B_fan], [k_tg.volt, k_bg.volt],
                     [Vtg_fan, Vbg_fan], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f'parked gates: TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V; '
          f'field measured={magnet.field():+.4f} T (field held for next arc step)')
