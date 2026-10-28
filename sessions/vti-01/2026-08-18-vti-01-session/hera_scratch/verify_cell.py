# VERIFY — session-start checklist (session brief, [VERIFY] section).
# Read-only by construction: every access is a get/read; no setpoints, no
# ranges, no outputs are written. The grant keys on the printed verdict line:
#   VERIFY: ALL GREEN   |   VERIFY: FAIL <items>
_checks = []

def _check(name, ok, detail):
    _checks.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")

# --- 1. Magnet at 0 T (measured readback, both paths) ---
try:
    _B = magnet.field()
    _Bs = magnet._status()["field"]
    print(_B, _Bs)  # brief-specified read, verbatim
    _check("magnet_zero", abs(_B) < 0.02 and abs(_Bs) < 0.02,
           f"field()={_B:+.4f} T, _status()={_Bs:+.4f} T (require |B| < 0.02 T)")
except Exception as e:
    _check("magnet_zero", False, f"read failed: {e!r}")

# --- 2. SAFETIES committed == device-card operating limits (live validators) ---
def _rng(p):
    return (p.vals._min_value, p.vals._max_value)

try:
    _expected = {
        "k_2400_tg.volt": (-0.8, 0.8),
        "k_2400_bg.volt": (-5.0, 5.0),
        "dc205.smart_voltage": (-20.0, 20.0),
        "dc205.voltage": (-20.0, 20.0),
        "magnet.field": (-10.0, 10.0),
        "heater.sample_setpoint": (0.0, 100.0),
        "heater.vaporizer_setpoint": (0.0, 100.0),
    }
    _actual = {
        "k_2400_tg.volt": _rng(k_2400_tg.volt),
        "k_2400_bg.volt": _rng(k_2400_bg.volt),
        "dc205.smart_voltage": _rng(dc205.smart_voltage),
        "dc205.voltage": _rng(dc205.voltage),
        "magnet.field": _rng(magnet.field),
        "heater.sample_setpoint": _rng(heater.sample_setpoint),
        "heater.vaporizer_setpoint": _rng(heater.vaporizer_setpoint),
    }
    _bad = {k: (_actual[k], _expected[k]) for k in _expected if _actual[k] != _expected[k]}
    _check("safeties_committed", not _bad,
           "all 7 validators match the device card" if not _bad
           else f"(actual, expected) mismatches: {_bad}")
except Exception as e:
    _check("safeties_committed", False, f"validator read failed: {e!r}")

# --- 3. Thermometry live + base T holding; vaporizer tracking base ---
try:
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
    _Ts, _Tv = T_sample(), T_vaporizer()
    _check("base_T", 1.1 <= _Ts <= 1.4, f"T_sample={_Ts:.3f} K (base band 1.2-1.3 K, accept 1.1-1.4)")
    _check("vaporizer_tracks_base", _Tv < 1.6, f"T_vaporizer={_Tv:.3f} K (require < 1.6 K)")
except Exception as e:
    _check("base_T", False, f"thermometry liveness/read failed: {e!r}")

# --- 4. Heaters off (both ranges 0) ---
try:
    _hr1, _hr2 = heater.sample_range(), heater.vaporizer_range()
    _check("heaters_off", _hr1 == 0 and _hr2 == 0,
           f"sample_range={_hr1}, vaporizer_range={_hr2} (require 0, 0)")
except Exception as e:
    _check("heaters_off", False, f"range read failed: {e!r}")

# --- 5. He level (budget number surfaced to the operator) ---
try:
    from drivers.AMI_1700 import AMI_1700
    try:
        _ami = qcodes.Instrument.find_instrument("ami_he")
    except Exception:
        _ami = AMI_1700("ami_he", "TCPIP0::192.168.0.100::7180::SOCKET")
    _he = _ami.He_level()
    _check("he_level_read", _he > 1.0, f"He level = {_he:.2f} in "
           "(budget call is the operator's - number surfaced in the notify)")
except Exception as e:
    _check("he_level_read", False, f"He level read failed: {e!r}")

# --- 6. Contacts hardwired per device card (documentation dicts vs card) ---
try:
    _wiring_exp = {"source": "T_SD", "drain": "B_SD",
                   "sr1+": "B_SD", "sr1-": "L4",
                   "sr2+": "L4", "sr2-": "L1",
                   "sr3+": "L3", "sr3-": "L2"}
    _cfg_ok = (meas_config["sr0_gain"] == -1e6
               and meas_config["bias_resistor"] == 10e6
               and meas_config["bias_channel"] == "sr1")
    _check("contacts_per_card", WIRING == _wiring_exp and _cfg_ok,
           "WIRING + meas_config match the provided contact configuration"
           if (WIRING == _wiring_exp and _cfg_ok)
           else f"WIRING={WIRING}, gain={meas_config['sr0_gain']}, "
                f"Rbias={meas_config['bias_resistor']}, bias_ch={meas_config['bias_channel']}")
except Exception as e:
    _check("contacts_per_card", False, f"config compare failed: {e!r}")

# --- 7. DC205 (Si gate): +/-100 V range (RNGE 2), output on, 0 V, sanctioned ramp rate ---
try:
    _rc, _out, _vsi = dc205.voltage_range(), dc205.output(), dc205.voltage()
    _rr = dc205.ramp_rate
    _check("dc205_state", _rc == 2 and _out == 1 and abs(_vsi) < 0.005 and _rr == 0.5,
           f"range={_rc} (need 2), output={_out} (need 1), V={_vsi:+.4f} (need ~0), "
           f"ramp_rate={_rr} V/s (need 0.5)")
except Exception as e:
    _check("dc205_state", False, f"DC205 read failed: {e!r}")

# --- Verdict (machine-readable; the grant keys on this line) ---
_fails = [n for n, ok in _checks if not ok]
print()
if _fails:
    print(f"VERIFY: FAIL {','.join(_fails)}")
else:
    print("VERIFY: ALL GREEN")
