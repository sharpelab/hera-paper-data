# Electron D=0 per-column SdH fan: region-A calibration from gatemap run 5.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
           n_offset=-0.08937933224099137, D_offset=-0.013)
N_LO, N_HI, D0 = 2.4, 3.2, 0.0  # 1e12 cm^-2, V/nm
N_N, N_B, B_START, B_END = 20, 102, 0.9, 10.0
FAST_DELAY, SLOW_DELAY = 2.1, 0.0
SENS, I_TRIP = 100e-6, 1e-9

# Preconditions: these are state the fan assumes but does not set. Print the
# readback before any instrument write; a mismatch raises before the field moves.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"],
                        max_age=15, max_period=12)
_T, _Tv = T_sample(), T_vaporizer()
_B, _tg, _bg, _si = magnet.field(), k_tg.volt(), k_bg.volt(), k_si()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_h1, _h2 = heater.sample_range(), heater.vaporizer_range()
_dc_range, _dc_out = dc205.voltage_range(), dc205.output()
print(f"preconditions: T_sample={_T:.3f} K (1.0..1.5), T_vaporizer={_Tv:.3f} K (0.7..1.5), "
      f"B={_B:+.4f} T (|B|<0.05), TG={_tg:+.4f}, BG={_bg:+.4f}, Si={_si:+.4f} V (all 0); "
      f"PS={_ps}, output={_out} (both True), heater ranges={_h1}/{_h2} (0/0), "
      f"DC205 range/output={_dc_range}/{_dc_out} (2/1)")
assert 1.0 <= _T <= 1.5 and 0.7 <= _Tv <= 1.5
assert abs(_B) < 0.05 and abs(_tg) < 0.01 and abs(_bg) < 0.01 and abs(_si) < 0.01
assert _ps and _out and _h1 == 0 and _h2 == 0 and _dc_range == 2 and _dc_out == 1
assert (TG_MIN, TG_MAX, BG_MIN, BG_MAX, SI_MIN, SI_MAX) == (-0.3, 1.0, -1.3, 2.0, -25.0, 25.0)
assert B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0
_tau, _slope = sr1.time_constant(), sr1.filter_slope()
print(f"settling/bias: sr1 tau={_tau} s (0.3), slope={_slope} dB/oct (24), "
      f"drive={sr1.amplitude()} V (1.0), sr0 sens={sr0.sensitivity()} V (0.02)")
assert _tau == 0.3 and _slope == 24 and abs(sr1.amplitude()-1.0) < 0.01
assert abs(sr0.sensitivity()-0.02) < 1e-9

ns = np.linspace(N_HI, N_LO, N_N)
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, **CAL)
B_vec = 1.0 / np.linspace(1.0/B_START, 1.0/B_END, N_B)
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX))
assert np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert np.all((0 < B_vec) & (B_vec <= B_SESSION_CAP))
for v in Vtgs: k_tg.volt.vals.validate(float(v))
for v in Vbgs: k_bg.volt.vals.validate(float(v))
for b in B_vec: magnet.field.vals.validate(float(b))
_nr, _dr = calc_nD(Vtgs, Vbgs, **CAL)
assert np.max(abs(_nr - ns)) < 1e-4 and np.max(abs(_dr)) < 1e-4
_inv_step = abs(1/B_vec[1] - 1/B_vec[0])
_FL = 33.0848  # h*n_max/(4e), n_max=3.2e12 cm^-2
_half_ray = 0.0435238  # 0.5*(4e/h)*B_start in 1e12 cm^-2
assert _inv_step <= 1/(3*_FL) and abs(ns[1]-ns[0]) <= _half_ray
print(f"grid: {N_B} B rows {B_vec[0]:.3f}->{B_vec[-1]:.3f} T, "
      f"d(1/B)={_inv_step:.5f} 1/T; {N_N} n points {ns[0]:+.2f}->{ns[-1]:+.2f}e12, "
      f"Vtg {Vtgs[0]:+.4f}->{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}->{Vbgs[-1]:+.4f} V")

# The first field move is a bare blocking ramp from the verified ~0 T state.
# Every subsequent row moves monotonically upward; no return ramp is hidden.
magnet.field(float(B_vec[0]))
print(f"positioned B={magnet.field():+.4f} T (target {B_START:+.3f})")
assert abs(magnet.field() - B_START) < 0.02
sr1.sensitivity(SENS)
print(f"sr1 sensitivity={sr1.sensitivity()} V (100 uV), fast delay={FAST_DELAY} s")

mc = dict(meas_config)
mc["Si (V)"] = _si
mc["sample_temperature:"] = _T
mc["comments"] = (f"landau-fan-vti: electron D=0 (run-5 region-A cal), n {N_HI:+.2f}->{N_LO:+.2f}e12 "
                  f"({N_N} pts), B {B_START:+.2f}->{B_END:+.2f} T ({N_B} uniform-1/B rows), "
                  f"fast_delay {FAST_DELAY}s, sr1 sens {SENS*1e6:.0f}uV, Vsi 0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'electron side; D={D0:+.3f} V/nm; n={N_HI:+.2f} to {N_LO:+.2f}e12 cm^-2, '
              f'TG={Vtgs[0]:+.4f} to {Vtgs[-1]:+.4f} V, BG={Vbgs[0]:+.4f} to {Vbgs[-1]:+.4f} V; '
              f'B={B_START:+.2f} to {B_END:+.2f} T, {N_B} uniform-1/B rows; '
              f'run-5 ratio={CAL["c_bg"]/CAL["c_tg"]:.4f}, n_offset={CAL["n_offset"]:+.4f}e12, '
              f'D_offset={CAL["D_offset"]:+.3f}; fast_delay={FAST_DELAY}s; sr1={SENS*1e6:.0f}uV')
s.ramp(k_bg.volt, float(Vbgs[0]))
s.ramp(k_tg.volt, float(Vtgs[0]))
interruptible_sleep(10)

# Row: [time, B, TG, BG, T_sample, TGcurr, BGcurr, sr0X, sr0P, sr1X, sr1P].
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    itg, ibg = abs(float(data[5])), abs(float(data[6]))
    vx = abs(float(data[9]))
    if itg > I_TRIP or ibg > I_TRIP or vx > 0.9*SENS:
        print(f"FAN TRIP B={float(data[1]):+.3f} T, TG={float(data[2]):+.3f}, BG={float(data[3]):+.3f} V: "
              f"|I_tg|={itg:.2e}, |I_bg|={ibg:.2e} A, |sr1X|={vx:.2e} V")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
# Intentional endpoint: +10 T, n=+2.4e12; this leaves field for a follow-up.
print(f"fan done: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V")
