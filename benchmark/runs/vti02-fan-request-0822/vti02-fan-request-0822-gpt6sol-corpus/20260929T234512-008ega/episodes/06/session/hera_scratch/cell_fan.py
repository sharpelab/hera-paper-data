# === landau-fan-vti: D=0 electron, n=+2.6..+3.2e12, B=0.9..8 T, 100x22 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Session calibration from run 5: ratio data-calibrated, absolute scale geometry prior.
CAL = dict(c_tg=2.796e-3, c_bg=2.161e-3, n_offset=-0.0894, D_offset=-0.013)
ns = np.linspace(2.6, 3.2, 22)  # 1e12 cm^-2
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset'])
B_vec = 1 / np.linspace(1 / 0.9, 1 / 8.0, 100)  # uniform inverse field, increasing B
assert len(B_vec) == 100 and np.all(np.diff(B_vec) > 0) and B_vec[-1] <= B_SESSION_CAP
assert np.all((Vtgs >= TG_MIN) & (Vtgs <= TG_MAX)) and np.all((Vbgs >= BG_MIN) & (Vbgs <= BG_MAX))
assert np.max(np.abs(np.array(calc_nD(Vtgs, Vbgs, CAL['c_tg'], CAL['c_bg'], CAL['n_offset'], CAL['D_offset']))[1])) < 1e-8
print(f'fan n {ns[0]:+.3f}..{ns[-1]:+.3f}e12; TG {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f} V; BG {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V; B {B_vec[0]:.3f}..{B_vec[-1]:.3f} T')

# Silent preconditions: handoff parked field and gates at zero; base T and Si gate unchanged.
assert_thermometry_live('T_sample', VTI.temp_logfile_candidates['T_sample'], max_age=15, max_period=12)
assert_thermometry_live('T_vaporizer', VTI.temp_logfile_candidates['T_vaporizer'], max_age=15, max_period=12)
_T, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_tg, _bg, _si = k_tg.volt(), k_bg.volt(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_tau, _slope, _amp = sr1.time_constant(), sr1.filter_slope(), sr1.amplitude()
print(f'precondition T_sample={_T:.3f} K [1.0,1.5], T_vaporizer={_Tv:.3f} K [0.7,1.5], B={_B:+.4f} T [|B|<0.05]; TG={_tg:+.4f}, BG={_bg:+.4f}, Si={_si:+.4f} V [all≈0]; PS heater={_ps}, output={_out}; sr1 tau={_tau} s, slope={_slope} dB/oct, amplitude={_amp} V; NPLC TG/BG={k_tg.nplci()}/{k_bg.nplci()}, magnet settle={magnet.settle_s} s')
assert 1.0 <= _T <= 1.5 and 0.7 <= _Tv <= 1.5 and abs(_B) < 0.05
assert abs(_tg) < 0.02 and abs(_bg) < 0.02 and abs(_si) < 0.01
assert _ps and _out and abs(_tau - 0.3) < 0.01 and _slope == 24 and abs(_amp - 1.0) < 0.02
assert k_tg.nplci() == 1 and k_bg.nplci() == 1 and magnet.settle_s >= 3.0

# Fixed sensitivity; field positioning blocks until the target is reached.
sr1.sensitivity(50e-6)
print(f'sr1 fixed sensitivity={sr1.sensitivity()} V (5 kOhm at 10 nA); positioning field at {B_vec[0]:.3f} T')
magnet.field(float(B_vec[0]))
_Bp = magnet.field()
print(f'field positioned: actual {_Bp:.4f} T versus target {B_vec[0]:.4f} T')
assert abs(_Bp - B_vec[0]) < 0.02

mc = dict(meas_config); mc['Si (V)'] = _si; mc['sample_temperature:'] = _T
mc['comments'] = 'landau-fan-vti: electron D=0 run-5 cal, n +2.6..+3.2e12 (22), B +0.9..+8 T uniform 1/B (100), sr1 50uV, fast_delay 2.1s'
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron D=0; n {ns[0]:+.3f}..{ns[-1]:+.3f}e12 cm^-2 ({len(ns)} points); B {B_vec[0]:+.3f}..{B_vec[-1]:+.3f} T ({len(B_vec)} uniform-1/B rows); run-5 cal c_bg/c_tg={CAL["c_bg"]/CAL["c_tg"]:.3f}, n_offset={CAL["n_offset"]:+.4f}e12, D_offset={CAL["D_offset"]:+.3f} V/nm; sr1 50uV, tau 0.3s, 24dB, fast_delay 2.1s')
s.ramp(k_bg.volt, float(Vbgs[0])); s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# Row layout: time, B, TG, BG, T_sample, I_TG, I_BG, sr0.X/P, sr1.X/P.
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, sr1.P); s.plot(k_tg.volt, sr0.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
I_TRIP = 1e-9
def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[5])), abs(float(data[6]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f'LEAK TRIP B={float(data[1]):+.3f} T, n-line TG={float(data[2]):+.3f} V: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A')
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=1.0, fast_delay=2.1)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
    print(f'post-run readback: B={magnet.field():+.4f} T; TG={k_tg.volt():+.4f}, BG={k_bg.volt():+.4f} V; T_sample={T_sample():.3f} K')
