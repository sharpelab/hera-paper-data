# HERA — plan step 4a: Landau fan 0 -> 8 T at D ~ 0, measure-while-ramping
# (magnet ramps continuously at its fixed 0.137 T/min; gates co-swept along the constant-D line each row;
#  B is read per point -> rows are slanted in B, analysis bins on the measured field)
_T, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_st = magnet._status()
print(f"precheck: T_sample={_T:.3f} K (want 1.0-1.4) | B={_B:.4f} T (want |B|<0.02) | V_si={_Vsi:.3f} V (want 0) | "
      f"PS on={_st['persistent_switch_on']} output={_st['output_enabled']} | gates now V_tg={k_tg.volt():.3f} V_bg={k_bg.volt():.3f}")
assert 1.0 <= _T <= 1.4, "T_sample out of base window"
assert abs(_B) < 1.5, "magnet not near zero (relaunch: ramp already in progress from the first attempt, cell 42)"
assert abs(_Vsi) < 0.01, "Si not at 0 V"
assert _st["persistent_switch_on"] and _st["output_enabled"], "magnet PS/output not ready"
for _s in (sr0, sr1):
    _s.time_constant(0.1)

# constant-D line through the CNP-ridge R minimum (run 3/4): slope dV_tg/dV_bg = c_bg/c_tg = CNP_RATIO
CNP_RATIO = 0.71                       # run 4 ridge refit (hole-side rows), c_bg/c_tg
VT0, VB0 = 0.11, 0.00                  # run 4: R_CNP minimum (248 Ω) on the ridge = D ~ 0 point
_vb = np.round(np.arange(VB0 - 0.70, VB0 + 1.25 + 1e-9, 0.015), 4)
_vt = VT0 + CNP_RATIO * (_vb - VB0)
_vt, _vb = sanitize_tg_bg(_vt, _vb, tg_lims, bg_lims)
assert _vt.min() >= TG_MIN and _vt.max() <= TG_MAX and _vb.min() >= BG_MIN and _vb.max() <= BG_MAX
B_TARGET = 8.0
_row_s = len(_vt) * 0.72 + 4.0                                   # per-row estimate (run 4: 0.68 s/pt + field read) + flyback
N_ROWS = int(np.ceil((B_TARGET - _B) / magnet.slew_T_per_s / _row_s)) + 2   # rows to cover the remaining ramp, +2 rows at 8 T
print(f"fan: {N_ROWS} rows x {len(_vt)} pts (V_bg {_vb[0]:+.3f}..{_vb[-1]:+.3f}, V_tg {_vt[0]:+.3f}..{_vt[-1]:+.3f}); "
      f"~{_row_s:.0f} s/row, ramp {B_TARGET/magnet.slew_T_per_s/60:.0f} min, est total {N_ROWS*_row_s/60:.0f} min")

fan_row = qcodes.Parameter("fan_row", set_cmd=None, get_cmd=None, initial_value=0)
meas_config["sample_temperature:"] = T_sample()
meas_config["Si (V)"] = dc205.voltage()
meas_config["comments"] = f"landau-fan-up: B 0->8 T continuous ramp, gates along D~0 line through ({VT0:+.3f},{VB0:+.3f}), {N_ROWS} rows; Si=0, base T"
s = sweep.AsyncStation(meas_config)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.Y).fp(magnet.field).fp(k_tg.curr).fp(k_bg.curr).fp(T_sample)
s.add_comment("landau-fan-up")
s.add_comment(f"multimegasweep fan_row x [k_tg.volt,k_bg.volt] along V_tg={VT0:+.3f}+{CNP_RATIO}*(V_bg-({VB0:+.3f})), "
              f"V_bg {_vb[0]:+.3f}..{_vb[-1]:+.3f} @15mV ({len(_vt)} pts); magnet start_field_ramp(8.0) then {N_ROWS} rows, "
              f"B read per point; fast_delay 0.5 s, tau 100 ms; V_si=0; I_bias 10 nA")
# multimegasweep row = [time, fan_row, V_tg, V_bg, *followed] -> sr1_X idx 6, sr1_Y idx 7
ar1 = SrAutoRange(sr1, cols=(6, 7), gain=1.0, lo=1e-6, hi=0.5)
s.register_run_after(ar1, args=())
for _p in (sr1.X, sr0.X, sr1.Y, magnet.field, sr0.P, k_tg.curr, k_bg.curr, T_sample):
    s.plot(k_bg.volt, _p)

# park the gates at the row start before the ramp begins (paced by volt.step)
k_bg.volt(_vb[0]); k_tg.volt(_vt[0])
time.sleep(1.0)
magnet.start_field_ramp(B_TARGET)
print(f"ramp started at {time.strftime('%H:%M:%S')}; B={magnet.field():.4f} T, is_ramping={magnet.is_ramping()}")
_t0 = time.time()
try:
    res = s.multimegasweep([fan_row], [np.arange(N_ROWS, dtype=float)], [k_tg.volt, k_bg.volt], [_vt, _vb],   # float rows: int64 setpoints broke the metadata JSON (run 5)
                           slow_delay=0.0, fast_delay=0.5, init_delay=False)
finally:
    _dt = time.time() - _t0
    print(f"sweep ended after {_dt/60:.1f} min; B={magnet.field():.4f} T, is_ramping={magnet.is_ramping()}")
magnet.wait_for_ramp()
print(f"run {res.id}: {_dt/60:.1f} min, {_dt/(N_ROWS*len(_vt)):.3f} s/pt; B={magnet.field():.4f} T; sr1 autorange steps {len(ar1.log)}")
print(f"end state: V_tg={k_tg.volt():.4f} V, V_bg={k_bg.volt():.4f} V, T_sample={T_sample():.3f} K, sr1 sens={sr1.sensitivity()} V")
