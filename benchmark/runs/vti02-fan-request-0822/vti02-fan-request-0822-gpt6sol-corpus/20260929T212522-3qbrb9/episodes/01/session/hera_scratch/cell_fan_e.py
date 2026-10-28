# Electron-side D=0 FS-count fan; run-5 calibration, runs 6/7 spot-check design.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
           n_offset=-0.08937933224099137, D_offset=-0.013)
ns = np.linspace(3.2, 2.7, 12)  # 1e12 cm^-2; high-density electron window
Ds = np.zeros_like(ns)           # V/nm
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
B_vec = np.round(np.linspace(1.0, 10.0, 901), 4)  # 10 mT, monotonic upward
assert len(ns) == 12 and len(B_vec) == 901 and np.all(np.diff(B_vec) > 0)
assert B_vec[-1] <= B_SESSION_CAP == 10.0
assert TG_MIN == -0.3 and TG_MAX == 1.0 and BG_MIN == -1.3 and BG_MAX == 2.0
for vtg, vbg in zip(Vtgs, Vbgs):
    k_tg.volt.validate(float(vtg)); k_bg.volt.validate(float(vbg))
magnet.field.validate(float(B_vec[0])); magnet.field.validate(float(B_vec[-1]))
print(f'plan: n {ns[0]:+.3f} to {ns[-1]:+.3f}e12, D=0; '
      f'TG {Vtgs.min():+.4f}..{Vtgs.max():+.4f} V, BG {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V; '
      f'B {B_vec[0]:.2f}..{B_vec[-1]:.2f} T ({len(B_vec)} rows x {len(ns)} points)')
print('roundtrip endpoints:', calc_nD(Vtgs[0], Vbgs[0], **CAL),
      calc_nD(Vtgs[-1], Vbgs[-1], **CAL))

# Silent preconditions: read actual state before positioning or gate writes.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_tg, _bg, _si = k_tg.volt(), k_bg.volt(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_hr = (heater.sample_range(), heater.vaporizer_range())
_amp, _tau, _slope = sr1.amplitude(), sr1.time_constant(), sr1.filter_slope()
print(f'precondition: T_sample={_T:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (<1.5), '
      f'B={_B:+.4f} T (~0), TG={_tg:+.4f} V (0), BG={_bg:+.4f} V (0), Si={_si:+.4f} V (0)')
print(f'precondition: PS heater={_ps} (True), output={_out} (True), heater ranges={_hr} ((0,0)), '
      f'drive={_amp:.3f} V (1), sr1 tau={_tau:.3f} s (0.3), slope={_slope} dB/oct (24)')
assert 1.0 <= _T <= 1.5 and _Tv < 1.5 and abs(_B) < 0.05
assert abs(_tg) < 0.01 and abs(_bg) < 0.01 and abs(_si) < 0.01
assert _ps and _out and _hr == (0, 0)
assert abs(_amp - 1.0) < 0.02 and abs(_tau - 0.3) < 1e-6 and _slope == 24
assert dc205.voltage_range() == 2 and dc205.output() == 1

# Set a fixed sensitivity; sr0's 20 mV range and 0.3 s filter are inherited from state0.
sr1.sensitivity(50e-6)
print(f'sr1 sensitivity={sr1.sensitivity():.2e} V (expect 50 uV), '
      f'sr0 sensitivity={sr0.sensitivity():.3g} V (expect 20 mV)')
assert abs(sr1.sensitivity() - 50e-6) < 1e-9 and abs(sr0.sensitivity() - 0.02) < 1e-6

# Blocking VTI ramp: measured readback after positioning, before the data run starts.
magnet.field(float(B_vec[0]))
_Bstart = magnet.field()
print(f'positioned B={_Bstart:+.4f} T; expected {B_vec[0]:+.4f} T')
assert abs(_Bstart - B_vec[0]) < 0.02

mc = dict(meas_config)
mc['Si (V)'] = _si
mc['sample_temperature:'] = _T
mc['comments'] = ('landau-fan-vti electron FS count; n +3.2 to +2.7e12 cm^-2, D=0, '
                  'B 1 to 10 T x 10 mT, 12 paired-gate points, sr1 50 uV, fast_delay 2.4 s; cal run 5')
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment('electron region B_1-B_2; D=0 V/nm; n +3.2 to +2.7e12 cm^-2 (12); '
              'B +1 to +10 T (901 x 10 mT); TG +0.9836 to +0.8403 V, BG +1.1663 to +0.9809 V; '
              'Si=0 V; run-5 calibration; sr1 50 uV, tau 0.3 s/24 dB, fast_delay 2.4 s')
s.ramp(k_bg.volt, float(Vbgs[0]))
s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# Row layout: time,B,TG,BG,T_sample,I_TG,I_BG,sr0_X,sr0_P,sr1_X,sr1_P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
for _channel in (T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P):
    s.plot('time', _channel)
s.plot(k_tg.volt, sr1.X)

_leak = {'consecutive': 0}
def fan_leak_guard(station, data):
    itg, ibg = abs(float(data[5])), abs(float(data[6]))
    _leak['consecutive'] = _leak['consecutive'] + 1 if max(itg, ibg) > 1e-9 else 0
    if _leak['consecutive'] >= 2:
        print(f'LEAK TRIP: B={float(data[1]):+.3f} T, TG={float(data[2]):+.4f} V, '
              f'|I_TG|={itg:.3e} A, |I_BG|={ibg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(fan_leak_guard, ())

_fan_result = s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                               slow_delay=0, fast_delay=2.4)
if _fan_result.metadata.get('interrupted'):
    print(f'interrupted: actual B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V')
    raise RuntimeError('Fan interrupted; inspect partial data and actual state before another move')
# Park the gates only after a completed/clean sweep; keep B at 10 T for next arc step.
s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
print(f'done: B={magnet.field():+.3f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V')
