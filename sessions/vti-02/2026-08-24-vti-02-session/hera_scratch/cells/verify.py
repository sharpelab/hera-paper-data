# HERA — VERIFY. READ-ONLY BY CONSTRUCTION: every statement below is a get.
# No parameter is set, no ramp is issued, no sweep is started. Walks the
# session brief's [VERIFY] checklist; the LAST printed line is the
# machine-readable verdict the autonomy grant keys on.
_fails = []


def chk(name, ok, detail):
    print(f"[{'PASS' if ok else 'FAIL'}] {name:<24} {detail}")
    if not ok:
        _fails.append(name)


# --- 1. magnet at 0 T (measured readback, never the last set) -------------
try:
    _B = magnet.field()
    _st = magnet._status()
    _psw, _out = magnet.persistent_switch_on(), magnet.output_enabled()
    chk("magnet-at-zero", abs(_B) <= 0.02 and bool(_psw) and bool(_out),
        f"field()={_B:+.4f} T | status={_st} | psw={_psw} output={_out}")
except Exception as e:
    chk("magnet-at-zero", False, repr(e))

# --- 2. SAFETIES committed == device-card operating limits ----------------
# Device card, Gate-operating-limits table + session caps. Compared as numbers.
_CARD = {
    "k_2400_tg.volt":            (k_2400_tg.volt,            -0.3,   +1.0),
    "k_2400_bg.volt":            (k_2400_bg.volt,            -1.3,   +2.0),
    "dc205.smart_voltage":       (dc205.smart_voltage,      -25.0,  +25.0),
    "dc205.voltage":             (dc205.voltage,            -25.0,  +25.0),
    "magnet.field":              (magnet.field,             -10.0,  +10.0),
    "heater.sample_setpoint":    (heater.sample_setpoint,     0.0,  100.0),
    "heater.vaporizer_setpoint": (heater.vaporizer_setpoint,  0.0,  100.0),
}
for _name, (_p, _lo, _hi) in _CARD.items():
    try:
        _v = _p.vals
        _got = (getattr(_v, "_min_value", None), getattr(_v, "_max_value", None))
        _ok = isinstance(_v, validators.Numbers) and _got == (_lo, _hi)
        chk(f"safeties:{_name.split('.')[-1]}", _ok,
            f"{_name}.vals = {_v} (card: [{_lo}, {_hi}])")
    except Exception as e:
        chk(f"safeties:{_name.split('.')[-1]}", False, repr(e))
# k_si must be the same object the validator was committed on.
chk("safeties:k_si-binding", k_si is dc205.smart_voltage,
    f"k_si is dc205.smart_voltage -> {k_si is dc205.smart_voltage}")

# --- 3. thermometry live + base T holding ---------------------------------
_Ts = _Tv = float("nan")
try:
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"],
                            max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"],
                            max_age=15, max_period=12)
    _Ts, _Tv = T_sample(), T_vaporizer()
    chk("base-T", 1.10 <= _Ts <= 1.40, f"T_sample = {_Ts:.3f} K (expect 1.2-1.3 K)")
except Exception as e:
    chk("base-T", False, repr(e))

# --- 4. heaters off, vaporizer tracking base ------------------------------
try:
    _sr, _vr = int(heater.sample_range()), int(heater.vaporizer_range())
    chk("heaters-off", _sr == 0 and _vr == 0,
        f"sample_range={_sr} vaporizer_range={_vr} (both must be 0)")
    chk("vaporizer-tracks-base", _Tv < 2.0,
        f"T_vaporizer = {_Tv:.3f} K (T_sample = {_Ts:.3f} K)")
except Exception as e:
    chk("heaters-off", False, repr(e))

# --- 5. contacts hardwired, no mux this cooldown --------------------------
_CARD_WIRING = {"source": "T_0", "drain": "B_3",
                "sr1+": "B_1", "sr1-": "B_2", "sr2": "n.c.", "sr3": "n.c."}
try:
    _mux_absent = not ({"mux", "qswitch", "contact_mux"} & set(globals()))
    _live_names = set(qcodes.Instrument._all_instruments)
    _no_qsw = not any(("qsw" in n.lower()) or ("switch" in n.lower()) for n in _live_names)
    chk("contacts-hardwired", _mux_absent and _no_qsw and WIRING == _CARD_WIRING,
        f"mux absent={_mux_absent and _no_qsw} | WIRING matches card={WIRING == _CARD_WIRING} | {WIRING}")
    chk("meas-config-channels",
        meas_config["source"] == "T_0" and meas_config["sr0_gain"] == -1e6
        and meas_config["sr1"] == "B_1 - B_2" and meas_config["bias_resistor"] == 100e6
        and meas_config["bias_channel"] == "sr1",
        f"source={meas_config['source']} sr0={meas_config['sr0']} "
        f"sr0_gain={meas_config['sr0_gain']:g} sr1={meas_config['sr1']} "
        f"Rbias={meas_config['bias_resistor']:g}")
except Exception as e:
    chk("contacts-hardwired", False, repr(e))

# --- 6. DC205 on +/-100 V range, output on, at 0 V ------------------------
try:
    _rng = int(dc205.voltage_range())
    _outp = int(dc205.output())
    _vsi = float(dc205.voltage())
    chk("dc205-state", _rng == 2 and _outp == 1 and abs(_vsi) <= 1e-3,
        f"range={_rng} (need 2 = +/-100 V) output={_outp} voltage={_vsi:+.4f} V "
        f"ramp_rate={dc205.ramp_rate} V/s")
except Exception as e:
    chk("dc205-state", False, repr(e))

# --- informational: acquisition state (recorded, NOT gating) --------------
print("\n--- informational: acquisition state (not gating) ---")
_lv = {}
for _n, _srN in (("sr0", sr0), ("sr1", sr1), ("sr2", sr2), ("sr3", sr3)):
    try:
        _s, _t, _f = _srN.sensitivity(), _srN.time_constant(), _srN.filter_slope()
        _x, _y, _r = _srN.X(), _srN.Y(), _srN.R()
        _lv[_n] = dict(sens=_s, tau=_t, slope=_f, X=_x, Y=_y, R=_r)
        print(f"{_n}: sens={_s:<9.3g} tau={_t:<6g}s slope={_f:g}dB/oct  "
              f"X={_x:+.4g}  Y={_y:+.4g}  R={_r:.4g}  fs=|R|/sens={abs(_r) / _s:6.2f}")
    except Exception as e:
        print(f"{_n}: <error {e!r}>")
try:
    _amp, _frq = sr1.amplitude(), sr1.frequency()
    _Ibias = _amp / meas_config["bias_resistor"]
    _Imeas = _lv["sr0"]["X"] / meas_config["sr0_gain"]
    print(f"drive: {_amp} V @ {_frq} Hz through {meas_config['bias_resistor']:.3g} ohm "
          f"-> I_bias = {_Ibias * 1e9:.3f} nA")
    print(f"sr0 -> I_measured = {_Imeas * 1e9:+.4f} nA "
          f"({100 * abs(_Imeas) / _Ibias:.1f}% of I_bias)")
    if abs(_Imeas) > 1e-13:
        print(f"sr1 (B_1-B_2) at V_tg=V_bg=V_si=0 -> Rxx = {_lv['sr1']['X'] / _Imeas:+.4g} ohm")
    print(f"gate leakage: TG {k_2400_tg.curr() * 1e12:+.1f} pA | "
          f"BG {k_2400_bg.curr() * 1e12:+.1f} pA")
    _hot = [n for n, d in _lv.items() if n in ("sr0", "sr1") and abs(d["R"]) / d["sens"] > 0.9]
    if _hot:
        print(f"ADVISORY (not a VERIFY gate): {_hot} at >90% of full scale — "
              f"sensitivity needs raising before any sweep. Operator ask.")
except Exception as e:
    print(f"<informational block error {e!r}>")

# --- verdict (must be the last line) --------------------------------------
print()
print("VERIFY: ALL GREEN" if not _fails else f"VERIFY: FAIL {','.join(_fails)}")
