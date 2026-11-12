# === Landau fan: B slow 0→10 T, n_A fast +0.8→+3.2e12 cm^-2 along D=0 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Run-5 ridge-A calibration: ratio/offset data constrained; absolute capacitance = geometry prior.
CAL_FAN = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
               n_offset=-0.08937933224099137, D_offset=-0.013)

# Load-bearing preconditions: state this cell assumes and never sets.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
_Ts, _Tv, _B, _Si = T_sample(), T_vaporizer(), magnet.field(), k_si()
_sr, _vr = heater.sample_range(), heater.vaporizer_range()
_dc_range, _dc_out = dc205.voltage_range(), dc205.output()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_drive, _freq, _tau, _slope = sr1.amplitude(), sr1.frequency(), sr1.time_constant(), sr1.filter_slope()
print(f"precondition T_sample={_Ts:.3f} K (1.0–1.5), T_vaporizer={_Tv:.3f} K (<1.6), "
      f"B={_B:+.4f} T (|B|<0.05), Si={_Si:+.4f} V (0); heater ranges sample/vap={_sr}/{_vr} (0/0)")
print(f"precondition magnet PS/output={_ps}/{_out} (True/True), DC205 range/output={_dc_range}/{_dc_out} (2/1); "
      f"drive={_drive:.3f} V at {_freq:.3f} Hz (1 V,13.777 Hz), tau={_tau:.3f} s slope={_slope} dB/oct (0.3,24)")
assert 1.0 <= _Ts <= 1.5 and _Tv < 1.6 and abs(_B) < 0.05 and abs(_Si) < 0.01
assert _sr == 0 and _vr == 0 and _ps and _out and _dc_range == 2 and _dc_out == 1
assert abs(_drive-1.0) < 0.01 and abs(_freq-13.777) < 0.01 and _tau <= 0.3 and _slope == 24
assert k_tg.nplci() == 1 and k_bg.nplci() == 1
_vrange = lambda p: (float(p.vals._min_value), float(p.vals._max_value))
assert _vrange(k_tg.volt) == (-0.3, 1.0) and _vrange(k_bg.volt) == (-1.3, 2.0)
assert _vrange(dc205.smart_voltage) == (-25.0, 25.0) and _vrange(dc205.voltage) == (-25.0, 25.0)
assert _vrange(magnet.field) == (-10.0, 10.0) and B_SESSION_CAP == 10.0

n_fast = np.linspace(0.8, 3.2, 61)  # 10^12 cm^-2; A-region nominal
D_fast = np.zeros_like(n_fast)
Vtg_fast, Vbg_fast = calc_gate_voltages(n_fast, D_fast, **CAL_FAN)
n_check, D_check = calc_nD(Vtg_fast, Vbg_fast, **CAL_FAN)
B_slow = np.linspace(0.0, 10.0, 41)
assert np.max(np.abs(n_check-n_fast)) < 1e-9 and np.max(np.abs(D_check)) < 1e-9
assert np.min(Vtg_fast) >= TG_MIN and np.max(Vtg_fast) <= TG_MAX
assert np.min(Vbg_fast) >= BG_MIN and np.max(Vbg_fast) <= BG_MAX
assert B_slow.max() <= B_SESSION_CAP
print(f"fan grid {len(B_slow)} B rows × {len(n_fast)} density pts = {len(B_slow)*len(n_fast)}; "
      f"B {B_slow[0]:.2f}→{B_slow[-1]:.2f} T, n_A {n_fast[0]:.2f}→{n_fast[-1]:.2f}e12 at D≈0; "
      f"TG {Vtg_fast[0]:+.4f}→{Vtg_fast[-1]:+.4f} V, BG {Vbg_fast[0]:+.4f}→{Vbg_fast[-1]:+.4f} V")

FAST_DELAY = 2.3  # >=7.7 tau for the 24 dB/oct Rxx lock-in
I_TRIP = 1e-9
RAIL_FRAC = 0.90
sr1.sensitivity(100e-6)  # ~10 kΩ full scale at nominal 10 nA bias
print(f"sr1 sensitivity={sr1.sensitivity():.2e} V, sr0 sensitivity={sr0.sensitivity():.2e} V, "
      f"fast settle={FAST_DELAY:.1f} s; bare B-ramp floor={10/(1/7.3):.1f} min")

mc = dict(meas_config)
mc["Si (V)"] = _Si; mc["sample_temperature:"] = _Ts
mc["comments"] = ("landau-fan electron: run-5 A calibration, D=0, n_A 0.8..3.2e12 (61 × 0.04), "
                  "B 0..10 T (41 × 0.25), sr1 100 uV, fast_delay 2.3 s, Si 0")
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan')
s.add_comment(f"electron n_A +0.8..+3.2e12 cm^-2 in 0.04 steps at D=0; B 0..10 T in 0.25 steps; "
              f"TG {Vtg_fast[0]:+.4f}..{Vtg_fast[-1]:+.4f} V, BG {Vbg_fast[0]:+.4f}..{Vbg_fast[-1]:+.4f} V; "
              f"run-5 c_bg/c_tg={CAL_FAN['c_bg']/CAL_FAN['c_tg']:.3f}, "
              f"n_offset={CAL_FAN['n_offset']:+.3f}e12, D_offset={CAL_FAN['D_offset']:+.3f} V/nm; Si=0, T=base")
s.ramp(k_bg.volt, float(Vbg_fast[0])); s.ramp(k_tg.volt, float(Vtg_fast[0]))
interruptible_sleep(10)

# Layout: time, B, Vtg, Vbg, T_sample, T_vaporizer, I_tg, I_bg, sr0.X, sr0.P, sr1.X, sr1.P.
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, k_tg.volt, sr1.X)
s.plot('time', T_sample); s.plot('time', T_vaporizer)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot('time', sr0.X); s.plot('time', sr0.P)
s.plot('time', sr1.X); s.plot('time', sr1.P)

_bad = {"leak": 0, "rail": 0}
def guard(station, data):
    _bad["leak"] = _bad["leak"] + 1 if max(abs(float(data[6])), abs(float(data[7]))) > I_TRIP else 0
    _bad["rail"] = _bad["rail"] + 1 if abs(float(data[10])) > RAIL_FRAC * 100e-6 else 0
    if _bad["leak"] >= 3 or _bad["rail"] >= 3:
        print(f"FAN TRIP at B={float(data[1]):.3f} T, Vtg={float(data[2]):+.4f} V: "
              f"I_tg={float(data[6]):+.2e} A, I_bg={float(data[7]):+.2e} A, sr1.X={float(data[10]):+.2e} V; "
              f"leak/rail consecutive={_bad['leak']}/{_bad['rail']}")
        station.interrupt_requested = True
s.register_run_after(guard, ())

s.multimegasweep([magnet.field], [B_slow], [k_tg.volt, k_bg.volt], [Vtg_fast, Vbg_fast],
                 slow_delay=0, fast_delay=FAST_DELAY)
print(f"fan done: measured B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, "
      f"BG={k_bg.volt():+.4f} V, Si={k_si():+.4f} V, T_sample={T_sample():.3f} K")
