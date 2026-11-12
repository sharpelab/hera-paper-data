# HERA — VERIFY: session-start gate, per the session brief's [VERIFY] list.
# READ-ONLY BY CONSTRUCTION: parameter gets and namespace reads only. No sets,
# no ramps, no range changes, no new instrument connections.
import numpy as np

_fails = []


def _check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name:<26} {detail}")
    if not ok:
        _fails.append(name)


def _vrange(param):
    v = getattr(param, "vals", None)
    return (getattr(v, "_min_value", None), getattr(v, "_max_value", None))


def _rng_ok(got, want):
    if got[0] is None or got[1] is None:
        return False
    return bool(np.isclose(got[0], want[0]) and np.isclose(got[1], want[1]))


print("=== 1. magnet ===")
_B = magnet.field()
_st = magnet._status()
_check("magnet-at-zero", abs(_B) <= 0.02 and abs(_st["field"]) <= 0.02,
       f"field()={_B:+.4f} T, _status()['field']={_st['field']:+.4f} T (tol 0.02 T)")
_check("magnet-output-ready", bool(_st["output_enabled"]) and bool(_st["persistent_switch_on"]),
       f"output_enabled={_st['output_enabled']}, persistent_switch_on={_st['persistent_switch_on']}, "
       f"loop={_st['loop_mode']}, V={_st['voltage']:.3f}")

print()
print("=== 2. SAFETIES validators vs device card ===")
for _nm, _param, _want in [
    ("tg-validator",         k_2400_tg.volt,           (-0.3, 1.0)),
    ("bg-validator",         k_2400_bg.volt,           (-1.3, 2.0)),
    ("si-smart-validator",   dc205.smart_voltage,      (-25.0, 25.0)),
    ("si-raw-validator",     dc205.voltage,            (-25.0, 25.0)),
    ("field-cap-validator",  magnet.field,             (-10.0, 10.0)),
    ("T-sample-setpt-cap",   heater.sample_setpoint,   (0.0, 100.0)),
    ("T-vap-setpt-cap",      heater.vaporizer_setpoint, (0.0, 100.0)),
]:
    _got = _vrange(_param)
    _check(_nm, _rng_ok(_got, _want), f"committed {_got}  vs card {_want}")
_check("field-cap-vs-driver", 10.0 <= magnet.max_field_T,
       f"session cap 10.0 T <= driver max_field_T {magnet.max_field_T} T")

print()
print("=== 3. thermometry ===")
try:
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
    _live_ok, _live_msg = True, "both worker logfiles live (age<=15 s, period<=12 s)"
except Exception as _e:
    _live_ok, _live_msg = False, f"{type(_e).__name__}: {_e}"
_check("thermometry-live", _live_ok, _live_msg)
_Ts, _Tv = T_sample(), T_vaporizer()
_check("base-T-holding", 1.0 <= _Ts <= 1.4, f"T_sample={_Ts:.3f} K (window 1.0-1.4; card base 1.2-1.3)")
_check("vaporizer-at-base", _Tv <= 1.5, f"T_vaporizer={_Tv:.3f} K (tracks base, no ladder running)")

print()
print("=== 4. heaters off ===")
_r1, _r2 = heater.sample_range(), heater.vaporizer_range()
_check("heaters-off", int(_r1) == 0 and int(_r2) == 0, f"sample_range={_r1}, vaporizer_range={_r2}")
print(f"      setpoints on record (inert at range 0): sample={heater.sample_setpoint()} K, "
      f"vaporizer={heater.vaporizer_setpoint()} K")

print()
print("=== 5. gates parked / DC205 ===")
_vtg, _vbg, _vsi = k_2400_tg.volt(), k_2400_bg.volt(), dc205.voltage()
_check("gates-at-zero", abs(_vtg) < 1e-3 and abs(_vbg) < 1e-3 and abs(_vsi) < 0.01,
       f"V_tg={_vtg:+.4f} V, V_bg={_vbg:+.4f} V, V_si={_vsi:+.4f} V")
_rngc, _out = dc205.voltage_range(), dc205.output()
_check("dc205-range-output", int(_rngc) == 2 and int(_out) == 1,
       f"range code={_rngc} (need 2 = +/-100 V), output={_out}")
_check("dc205-ramp-rate", bool(np.isclose(dc205.ramp_rate, 0.5)),
       f"ramp_rate={dc205.ramp_rate} V/s (card pacing 0.5; raising it is consent-gated)")

print()
print("=== 6. contacts / measurement config vs device card ===")
_WIRING_CARD = {
    "source": "T_0", "drain": "B_3",
    "sr1+": "B_1", "sr1-": "B_2",
    "sr2+": "n.c.", "sr2-": "n.c.",
    "sr3+": "n.c.", "sr3-": "n.c.",
}
_check("contact-map", WIRING == _WIRING_CARD, f"{WIRING}")
_mc_ok = (meas_config.get("source") == "T_0"
          and meas_config.get("sr0_gain") == -1e6
          and meas_config.get("bias_resistor") == 100e6
          and meas_config.get("bias_channel") == "sr1")
_check("meas-config", _mc_ok,
       f"source={meas_config.get('source')}, sr0_gain={meas_config.get('sr0_gain')}, "
       f"R_bias={meas_config.get('bias_resistor')}, bias_channel={meas_config.get('bias_channel')}")
_check("no-mux-bound", ("mux" not in globals()) and ("qswitch" not in globals()),
       "hardwired breakout this cooldown; no ContactMux/QSwitch in namespace")

print()
print("=== 7. drive + lock-in state (recorded here; not in run metadata) ===")
_amp, _frq = sr1.amplitude(), sr1.frequency()
_ibias = _amp / meas_config["bias_resistor"]
print(f"      drive (sr1 osc): {_amp} V @ {_frq} Hz  ->  I_bias = {_ibias:.4e} A across "
      f"{meas_config['bias_resistor']:.3g} ohm")
for _nm, _sr in [("sr0", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)]:
    print(f"      {_nm}: sens={_sr.sensitivity()}, tau={_sr.time_constant()} s, "
          f"slope={_sr.filter_slope()} dB/oct")
_check("drive-frequency", bool(np.isclose(_frq, 13.777, atol=0.01)), f"{_frq} Hz (card 13.777 Hz)")
_check("drive-nonzero", _amp > 0, f"amplitude={_amp} V -> I_bias={_ibias:.4e} A")

print()
print("=== 8. He budget ===")
print("      NOT GATED HERE - AMI 1700 not bound in this kernel and deliberately not")
print("      connected (shared TCP instrument, possibly held by the influx logger).")
print("      Operator confirms He budget with the grant.")

print()
if _fails:
    print(f"failing items ({len(_fails)}): {', '.join(_fails)}")
    print(f"VERIFY: FAIL {_fails[0]}")
else:
    print("VERIFY: ALL GREEN")
