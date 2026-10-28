# === Plan step 1: D_A=0 electron Landau fan, B slow 0.5→10 T, n_A fast +0.50→+3.10e12 ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

# Run-5 CNP/D-line calibration: ratio and offsets data-derived, c_tg absolute scale geometry anchored.
CAL_FAN = dict(c_tg=2.7960593093052633e-3, c_bg=2.160696465377614e-3,
               n_offset=-0.08937933224099137, D_offset=-0.013)
n_fast = np.linspace(0.50, 3.10, 53)  # 1e12 cm^-2, 0.05e12 step
D_fast = np.zeros_like(n_fast)         # V/nm, region-A D=0
Vtg_fast, Vbg_fast = calc_gate_voltages(n_fast, D_fast, **CAL_FAN)
B_rows = np.round(np.arange(0.5, 10.0001, 0.1), 3)
assert len(B_rows) == 96 and len(n_fast) == 53
assert np.all((Vtg_fast >= TG_MIN) & (Vtg_fast <= TG_MAX))
assert np.all((Vbg_fast >= BG_MIN) & (Vbg_fast <= BG_MAX))
assert np.all(np.abs(B_rows) <= B_SESSION_CAP)
_n_check, _D_check = calc_nD(Vtg_fast, Vbg_fast, **CAL_FAN)
assert np.max(np.abs(_n_check - n_fast)) < 1e-8 and np.max(np.abs(_D_check)) < 1e-8
print(f"fan grid: {len(B_rows)} B rows {B_rows[0]:.2f}→{B_rows[-1]:.2f} T × {len(n_fast)} density points "
      f"n_A={n_fast[0]:.2f}→{n_fast[-1]:.2f}e12; TG={Vtg_fast.min():+.4f}…{Vtg_fast.max():+.4f} V, "
      f"BG={Vbg_fast.min():+.4f}…{Vbg_fast.max():+.4f} V")

# Read-only preconditions: this cell does not set T, Si, magnet switch/output, or current-read precision.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
_Ts, _Tv, _B = T_sample(), T_vaporizer(), magnet.field()
_si, _tg, _bg = k_si(), k_tg.volt(), k_bg.volt()
_ps, _out = magnet.persistent_switch_on(), magnet.output_enabled()
_rh, _rv = heater.sample_range(), heater.vaporizer_range()
_ntg, _nbg = k_tg.nplci(), k_bg.nplci()
print(f"precondition expected base/0T/0V/heaters-off: T_sample={_Ts:.3f} K, T_vaporizer={_Tv:.3f} K, "
      f"B={_B:+.4f} T, Si={_si:+.4f} V, TG={_tg:+.4f} V, BG={_bg:+.4f} V, "
      f"heater ranges={_rh}/{_rv}, PS/output={_ps}/{_out}, gate NPLC={_ntg}/{_nbg}")
assert 1.0 <= _Ts <= 1.5 and 0.6 <= _Tv <= 1.5
assert abs(_B) < 0.03 and abs(_si) < 0.01 and abs(_tg) < 0.02 and abs(_bg) < 0.02
assert _rh == 0 and _rv == 0 and _ps and _out
assert _ntg == 1 and _nbg == 1
assert (TG_MIN,TG_MAX,BG_MIN,BG_MAX,SI_MIN,SI_MAX,B_SESSION_CAP,T_SESSION_CAP) == (-0.3,1.0,-1.3,2.0,-25.0,25.0,10.0,100.0)

# Fixed sensitivity, bias, and dwell: 2.1 s = 7 tau at 24 dB/oct.
assert abs(sr1.amplitude() - 1.0) < 0.01 and abs(sr1.time_constant() - 0.3) < 1e-6 and sr1.filter_slope() == 24
assert abs(sr0.time_constant() - 0.3) < 1e-6 and sr0.filter_slope() == 24
sr1.sensitivity(100e-6)
_sens = sr1.sensitivity()
assert abs(_sens - 100e-6) < 1e-9
print(f"drive={sr1.amplitude():.3f} V / 100 MOhm = 10 nA; sr1 sensitivity={_sens*1e6:.0f} uV "
      f"(Rxx full scale ~{_sens/1e-8:.0f} Ohm); fast delay=2.1 s; field settle={magnet.settle_s} s")

mc = dict(meas_config)
mc["Si (V)"] = _si; mc["sample_temperature:"] = _Ts
mc["comments"] = ("landau-fan electron D_A=0 from run-5 calibration; n_A +0.50..+3.10e12 cm^-2 / 0.05e12, "
                  "B +0.5..+10.0 T / 0.1 T, TG/BG co-swept; Si=0, base T; sr1 100 uV, 2.1 s fast settle")
s = sweep.AsyncStation(mc)
s.add_comment("landau-fan")
s.add_comment("electron D_A=0; run-5 cal c_bg/c_tg=0.773, n_offset=-0.0894e12, D_offset=-0.013 V/nm; "
              "n_A=+0.50..+3.10e12 cm^-2 (53), B=+0.5..+10.0 T (96); Si=0 V, base T; sr1 100 uV; "
              "hardwired source T_0, drain B_3, Rxx B_1-B_2; density scale geometry anchored")

# Establish the first fast point, then make the 0→0.5 T blocking ramp before writing the first run row.
s.ramp(k_bg.volt, float(Vbg_fast[0])); s.ramp(k_tg.volt, float(Vtg_fast[0]))
interruptible_sleep(10)
magnet.field(float(B_rows[0]))
print(f"start readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V, "
      f"I_tg={k_tg.curr()*1e12:+.0f} pA, I_bg={k_bg.curr()*1e12:+.0f} pA, T={T_sample():.3f} K")
assert abs(magnet.field() - B_rows[0]) < 0.03
assert abs(k_tg.curr()) < 1e-9 and abs(k_bg.curr()) < 1e-9

# Row layout: time, B, TG, BG, T_sample, T_vaporizer, I_tg, I_bg, sr0_X, sr1_X.
s.fp(T_sample).fp(T_vaporizer).fp(k_tg.curr).fp(k_bg.curr).fp(sr0.X).fp(sr1.X)
s.plot("time", T_sample); s.plot("time", T_vaporizer)
s.plot("time", k_tg.curr); s.plot("time", k_bg.curr)
s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, sr1.X)

def fan_guard(station, data):
    itg, ibg, x1 = abs(float(data[6])), abs(float(data[7])), abs(float(data[9]))
    if itg > 1e-9 or ibg > 1e-9 or x1 > 0.9 * _sens:
        print(f"FAN TRIP B={float(data[1]):.3f} T, TG={float(data[2]):+.4f} V: "
              f"|I_tg|={itg*1e12:.0f} pA, |I_bg|={ibg*1e12:.0f} pA, |sr1.X|={x1*1e6:.1f} uV")
        station.interrupt_requested = True
s.register_run_after(fan_guard, ())

s.multimegasweep([magnet.field], [B_rows], [k_tg.volt, k_bg.volt], [Vtg_fast, Vbg_fast],
                 slow_delay=0, fast_delay=2.1, init_delay=False)
print(f"fan end/readback: B={magnet.field():+.4f} T, TG={k_tg.volt():+.4f} V, BG={k_bg.volt():+.4f} V, "
      f"Si={k_si():+.4f} V, T_sample={T_sample():.3f} K")
