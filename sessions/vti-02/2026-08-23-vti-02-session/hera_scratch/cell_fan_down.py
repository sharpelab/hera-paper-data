# HERA — plan step 4b: Landau fan 8 -> 0 T at finite D (plateau knee), measure-while-ramping down
_T, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_st = magnet._status()
print(f"precheck: T_sample={_T:.3f} K (want 1.0-1.5) | B={_B:.4f} T (want ~8, not ramping) | is_ramping={magnet.is_ramping()} | "
      f"V_si={_Vsi:.3f} V (want 0) | PS on={_st['persistent_switch_on']} output={_st['output_enabled']} | gates now V_tg={k_tg.volt():.3f} V_bg={k_bg.volt():.3f}")
assert 1.0 <= _T <= 1.5, "T_sample out of base window"
assert 7.9 <= _B <= 8.1 and not magnet.is_ramping(), "magnet not holding at 8 T"
assert abs(_Vsi) < 0.01, "Si not at 0 V"
assert _st["persistent_switch_on"] and _st["output_enabled"], "magnet PS/output not ready"
for _s in (sr0, sr1):
    _s.time_constant(0.1)

# constant-D line through the run-4 CNP point at V_bg = -0.85 (R_CNP 2.6 kOhm, D-D0 ~ +0.20 V/nm: knee of the plateau)
CNP_RATIO = 0.71
VT0, VB0 = 0.657, -0.85
_vb = np.round(np.arange(VB0 - 0.50, VB0 + 0.55 + 1e-9, 0.0075), 4)
_vt = VT0 + CNP_RATIO * (_vb - VB0)
_vt, _vb = sanitize_tg_bg(_vt, _vb, tg_lims, bg_lims)
assert _vt.min() >= TG_MIN and _vt.max() <= TG_MAX and _vb.min() >= BG_MIN and _vb.max() <= BG_MAX
B_TARGET = 0.0
_row_s = len(_vt) * 0.72 + 4.0
N_ROWS = int(np.ceil((_B - B_TARGET) / magnet.slew_T_per_s / _row_s)) + 2
print(f"fan: {N_ROWS} rows x {len(_vt)} pts (V_bg {_vb[0]:+.3f}..{_vb[-1]:+.3f}, V_tg {_vt[0]:+.3f}..{_vt[-1]:+.3f}); "
      f"~{_row_s:.0f} s/row, ramp {(_B-B_TARGET)/magnet.slew_T_per_s/60:.0f} min, est total {N_ROWS*_row_s/60:.0f} min")

fan_row = qcodes.Parameter("fan_row", set_cmd=None, get_cmd=None, initial_value=0)
meas_config["sample_temperature:"] = T_sample()
meas_config["Si (V)"] = dc205.voltage()
meas_config["comments"] = f"landau-fan-down: B 8->0 T continuous ramp, gates along D-D0~+0.20 line through ({VT0:+.3f},{VB0:+.3f}), {N_ROWS} rows; Si=0, base T"
s = sweep.AsyncStation(meas_config)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.Y).fp(magnet.field).fp(k_tg.curr).fp(k_bg.curr).fp(T_sample)
s.add_comment("landau-fan-down")
s.add_comment(f"multimegasweep fan_row x [k_tg.volt,k_bg.volt] along V_tg={VT0:+.3f}+{CNP_RATIO}*(V_bg-({VB0:+.3f})), "
              f"V_bg {_vb[0]:+.3f}..{_vb[-1]:+.3f} @7.5mV ({len(_vt)} pts); magnet start_field_ramp(0.0) from 8 T then {N_ROWS} rows, "
              f"B read per point; fast_delay 0.5 s, tau 100 ms; V_si=0; I_bias 10 nA")
ar1 = SrAutoRange(sr1, cols=(6, 7), gain=1.0, lo=1e-6, hi=0.5)
s.register_run_after(ar1, args=())
for _p in (sr1.X, sr0.X, sr1.Y, magnet.field, sr0.P, k_tg.curr, k_bg.curr, T_sample):
    s.plot(k_bg.volt, _p)

k_bg.volt(_vb[0]); k_tg.volt(_vt[0])
time.sleep(1.0)
magnet.start_field_ramp(B_TARGET)
print(f"ramp started at {time.strftime('%H:%M:%S')}; B={magnet.field():.4f} T, is_ramping={magnet.is_ramping()}")
_t0 = time.time()
try:
    res = s.multimegasweep([fan_row], [np.arange(N_ROWS, dtype=float)], [k_tg.volt, k_bg.volt], [_vt, _vb],
                           slow_delay=0.0, fast_delay=0.5, init_delay=False)
finally:
    _dt = time.time() - _t0
    print(f"sweep ended after {_dt/60:.1f} min; B={magnet.field():.4f} T, is_ramping={magnet.is_ramping()}")
magnet.wait_for_ramp()
print(f"run {res.id}: {_dt/60:.1f} min, {_dt/(N_ROWS*len(_vt)):.3f} s/pt; B={magnet.field():.4f} T; sr1 autorange steps {len(ar1.log)}")
print(f"end state: V_tg={k_tg.volt():.4f} V, V_bg={k_bg.volt():.4f} V, T_sample={T_sample():.3f} K, sr1 sens={sr1.sensitivity()} V")
