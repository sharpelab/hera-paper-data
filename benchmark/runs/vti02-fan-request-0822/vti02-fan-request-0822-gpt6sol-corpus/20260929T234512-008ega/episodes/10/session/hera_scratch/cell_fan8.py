# Electron-side D=0 Landau fan: tetralayer FS counting, cal from run 5.
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
FAN_CAL = dict(c_tg=0.0027960593093052633, c_bg=0.002160696465377614,
               n_offset=-0.08937933224099137, D_offset=-0.013)

# Assumed state (the cell does not set these): print expected vs actual before any move.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_hr = (heater.sample_range(), heater.vaporizer_range())
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
print(f"preflight: T_sample {_T:.3f} K (1.0..1.5); T_vaporizer {_Tv:.3f} K (<1.5); "
      f"field {_B:+.4f} T (0 +/-0.05); Si {_Si:+.4f} V (0 +/-0.01); "
      f"heater ranges {_hr} (0,0); PS/output {_ps}/{_out} (True/True)")
print(f"preflight: TG/BG nplci {k_tg.nplci()}/{k_bg.nplci()} (1/1); "
      f"drive {sr1.amplitude()} V (1); sr0/sr1 tau {sr0.time_constant()}/{sr1.time_constant()} s (0.3/0.3); "
      f"slopes {sr0.filter_slope()}/{sr1.filter_slope()} (24/24); magnet settle {magnet.settle_s} s (>=3)")
assert 1.0 <= _T <= 1.5 and _Tv < 1.5 and abs(_B) < 0.05 and abs(_Si) < 0.01
assert _hr == (0, 0) and _ps and _out
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
assert abs(sr1.amplitude() - 1.0) < 0.01
assert sr0.time_constant() == sr1.time_constant() == 0.3
assert sr0.filter_slope() == sr1.filter_slope() == 24 and magnet.settle_s >= 3
assert (k_tg.volt.vals.min_value, k_tg.volt.vals.max_value) == (-0.3, 1.0)
assert (k_bg.volt.vals.min_value, k_bg.volt.vals.max_value) == (-1.3, 2.0)
assert (dc205.smart_voltage.vals.min_value, dc205.smart_voltage.vals.max_value) == (-25.0, 25.0)
assert (magnet.field.vals.min_value, magnet.field.vals.max_value) == (-10.0, 10.0)
assert heater.sample_setpoint.vals.max_value == heater.vaporizer_setpoint.vals.max_value == 100.0

n_vec = np.linspace(2.4, 3.2, 22)  # 1e12 cm^-2; two samples/ray at B=0.8 T.
D_vec = np.zeros_like(n_vec)
Vtgs, Vbgs = calc_gate_voltages(n_vec, D_vec, FAN_CAL['c_tg'], FAN_CAL['c_bg'],
                                FAN_CAL['n_offset'], FAN_CAL['D_offset'])
B_vec = field_invB(0.8, 10.0, 131)  # uniform 1/B, ascending from present 0 T.
assert np.all((TG_MIN <= Vtgs) & (Vtgs <= TG_MAX))
assert np.all((BG_MIN <= Vbgs) & (Vbgs <= BG_MAX))
assert B_vec.min() > 0 and B_vec.max() <= B_SESSION_CAP
_ncheck, _Dcheck = calc_nD(Vtgs, Vbgs, FAN_CAL['c_tg'], FAN_CAL['c_bg'],
                           FAN_CAL['n_offset'], FAN_CAL['D_offset'])
assert np.max(np.abs(_ncheck - n_vec)) < 1e-8 and np.max(np.abs(_Dcheck)) < 1e-8
print(f"grid: {len(B_vec)} B rows x {len(n_vec)} n; B {B_vec[0]:.3f}->{B_vec[-1]:.3f} T, "
      f"delta(1/B)={abs(1/B_vec[1]-1/B_vec[0]):.6f} 1/T; "
      f"Vtg {Vtgs[0]:+.4f}->{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}->{Vbgs[-1]:+.4f}")

sr1.sensitivity(50e-6)  # fixed 5 kOhm full scale at 10 nA; run-6 amplitude had <=0.11 FS.
FAST_DELAY, SLOW_DELAY = 2.1, 1.0  # 7 tau at 24 dB/oct; field driver also settles 3 s.
I_TRIP, X_TRIP = 1e-9, 0.9 * sr1.sensitivity()
mc = dict(meas_config); mc['Si (V)'] = _Si; mc['sample_temperature:'] = _T
mc['comments'] = (f"landau-fan-vti electron D=0 run-5 cal; n +2.40..+3.20e12 (22), "
                  f"B +0.8..+10 T (131 uniform-1/B), Si=0, sr1=50uV, fast_delay=2.1s")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f"region A electron D=0 V/nm; n {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}e12 cm^-2 (22); "
              f"B {B_vec[0]:+.2f}..{B_vec[-1]:+.1f} T (131 uniform-1/B); "
              f"Vtg {Vtgs[0]:+.4f}..{Vtgs[-1]:+.4f}, Vbg {Vbgs[0]:+.4f}..{Vbgs[-1]:+.4f} V; "
              f"Si=0, run-5 cal, sr1=50uV, fast_delay={FAST_DELAY}s")

# Gate line and leak preflight before the long field move.
try:
    s.ramp(k_bg.volt, Vbgs[0]); s.ramp(k_tg.volt, Vtgs[0])
    interruptible_sleep(10)
    _Itg, _Ibg = k_tg.curr(), k_bg.curr()
    print(f"gate preflight: TG {k_tg.volt():+.4f} V, I {_Itg*1e12:+.1f} pA; "
          f"BG {k_bg.volt():+.4f} V, I {_Ibg*1e12:+.1f} pA; expect |I|<1 nA")
    assert abs(_Itg) < I_TRIP and abs(_Ibg) < I_TRIP
except BaseException:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    raise

# Each fp channel gets a live trace. Row layout:
# [time, B, Vtg, Vbg, T_sample, I_tg, I_bg, sr0_X, sr0_P, sr1_X, sr1_P].
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot('time', T_sample)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_bg.volt, k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr0.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr1.P)

def fan_guard(station, data):
    i_tg, i_bg, x1, temp = abs(float(data[5])), abs(float(data[6])), abs(float(data[9])), float(data[4])
    if i_tg > I_TRIP or i_bg > I_TRIP or x1 >= X_TRIP or not (1.0 <= temp <= 1.5):
        print(f"FAN TRIP B={float(data[1]):+.3f} T nline Vtg={float(data[2]):+.4f}: "
              f"|I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A; |sr1_X|={x1:.3e} V; T={temp:.3f} K")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

try:
    magnet.field(B_vec[0])  # 0->0.8 T: ~6 min at 0.137 T/min; blocking + 3 s settle.
    print(f"field positioned: measured {magnet.field():+.4f} T, target {B_vec[0]:+.4f} T")
    assert abs(magnet.field() - B_vec[0]) < 0.02
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
    print(f"post fan: measured field {magnet.field():+.4f} T; gates TG {k_tg.volt():+.4f}, BG {k_bg.volt():+.4f} V")
