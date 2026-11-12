# === VERIFY — session-start checks (read-only by construction) ===
# Every call below is a get/read; nothing is set. Last printed line is the
# machine-readable verdict the E1 grant keys on.
import time as _time
_fails = []

def _check(name, ok, detail):
    print(f"[{'OK  ' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        _fails.append(name)

def _vr(vals):  # qcodes validators.Numbers -> (min, max)
    return (float(vals._min_value), float(vals._max_value))

# --- 1. Magnet at 0 T (measured readback, both read paths) + output/PS state
_B = magnet.field()
_st = magnet._status()
_check("magnet_zero", abs(_B) < 0.02 and abs(_st['field']) < 0.02,
       f"field()={_B:+.4f} T, _status()['field']={_st['field']:+.4f} T (tol 20 mT)")
_check("magnet_output", _st['output_enabled'] and _st['persistent_switch_on'],
       f"output_enabled={_st['output_enabled']}, persistent_switch_on={_st['persistent_switch_on']}")

# --- 2. SAFETIES committed == device card (numbers compared, not eyeballed)
_card = {"tg": (-0.3, 1.0), "bg": (-1.3, 2.0), "si": (-25.0, 25.0),
         "B": (-10.0, 10.0), "T": (0.0, 100.0)}
_live = {"tg": _vr(k_2400_tg.volt.vals), "bg": _vr(k_2400_bg.volt.vals),
         "si": _vr(dc205.smart_voltage.vals), "si_raw": _vr(dc205.voltage.vals),
         "B": _vr(magnet.field.vals),
         "T": _vr(heater.sample_setpoint.vals), "T_vap": _vr(heater.vaporizer_setpoint.vals)}
for _k, _ref in (("tg", "tg"), ("bg", "bg"), ("si", "si"), ("si_raw", "si"),
                 ("B", "B"), ("T", "T"), ("T_vap", "T")):
    _check(f"validator_{_k}", _live[_k] == _card[_ref], f"committed {_live[_k]} vs card {_card[_ref]}")
_check("session_caps", B_SESSION_CAP == 10.0 and T_SESSION_CAP == 100.0,
       f"B_SESSION_CAP={B_SESSION_CAP}, T_SESSION_CAP={T_SESSION_CAP}")
_check("gate_aliases", (k_tg is k_2400_tg) and (k_bg is k_2400_bg) and (k_si is dc205.smart_voltage),
       "k_tg->k_2400_tg, k_bg->k_2400_bg, k_si->dc205.smart_voltage")

# --- 3. Base T holding, thermometry logfiles live (freshness >= 2-3 write periods)
try:
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
    _live_ok = True
except Exception as _e:
    print("   thermometry liveness error:", _e)
    _live_ok = False
_check("thermometry_live", _live_ok, "worker logfiles advancing (max_age 15 s, max_period 12 s)")
_Ts = T_sample(); _Tv = T_vaporizer()
_check("base_T", 1.0 <= _Ts <= 1.4, f"T_sample={_Ts:.3f} K (expect 1.2-1.3 K; accept 1.0-1.4)")

# --- 4. Heaters off (both ranges 0); vaporizer tracking base
_sr, _vrg = heater.sample_range(), heater.vaporizer_range()
_check("heaters_off", _sr == 0 and _vrg == 0, f"sample_range={_sr}, vaporizer_range={_vrg}")
_check("vaporizer_tracks_base", _Tv < 1.6 and abs(_Tv - _Ts) < 0.6,
       f"T_vaporizer={_Tv:.3f} K vs T_sample={_Ts:.3f} K")

# --- 5. Contacts hardwired (no mux) — notebook WIRING == device-card provided configuration
_card_wiring = {"source": "T_0", "drain": "B_3", "sr1+": "B_1", "sr1-": "B_2",
                "sr2+": "n.c.", "sr2-": "n.c.", "sr3+": "n.c.", "sr3-": "n.c."}
_check("contacts_hardwired", WIRING == _card_wiring and 'mux' not in globals(),
       f"WIRING={WIRING}; no ContactMux instance in kernel")
_check("meas_config_channels", meas_config["sr0_gain"] == -1e6 and meas_config["bias_channel"] == "sr1"
       and meas_config["bias_resistor"] == 100e6,
       f"sr0_gain={meas_config['sr0_gain']}, bias_channel={meas_config['bias_channel']}, R_bias={meas_config['bias_resistor']:.0e}")

# --- 6. DC205 (Si gate): +/-100 V range (RNGE 2), output on, reading 0 V, ramp pacing as set
_rng, _out, _vsi = dc205.voltage_range(), dc205.output(), dc205.voltage()
_check("dc205_state", _rng == 2 and _out == 1 and abs(_vsi) < 0.01,
       f"range code={_rng} (need 2), output={_out}, V={_vsi:+.4f} V")
_check("dc205_ramp_rate", abs(dc205.ramp_rate - 0.5) < 1e-9, f"ramp_rate={dc205.ramp_rate} V/s (consent-gated)")

# --- 7. Gates parked at 0, Keithley step pacing in place, lock-ins answering
_vtg, _vbg = k_tg.volt(), k_bg.volt()
_check("gates_zero", abs(_vtg) < 1e-3 and abs(_vbg) < 1e-3, f"V_tg={_vtg:+.4f} V, V_bg={_vbg:+.4f} V")
_check("keithley_step", k_2400_tg.volt.step == 0.005 and k_2400_bg.volt.step == 0.005,
       f"volt.step tg={k_2400_tg.volt.step}, bg={k_2400_bg.volt.step} V")
_f, _a = sr1.frequency(), sr1.amplitude()
_check("lockin_drive", abs(_f - 13.777) < 0.01 and 0 < _a <= 1.0,
       f"sr1 f={_f:.3f} Hz, amp={_a} V -> I_bias={_a/100e6*1e9:.2f} nA; sr0 sens={sr0.sensitivity()}, sr1 sens={sr1.sensitivity()}, tau={sr1.time_constant()} s")

# --- He budget: not readable from this kernel (AMI 1700 not connected here) — operator attests in the grant.
print("[INFO] He level: operator-attested (not readable from this kernel)")

print("VERIFY: ALL GREEN" if not _fails else f"VERIFY: FAIL {','.join(_fails)}")
