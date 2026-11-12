# HERA — VERIFY (read-only by construction; no instrument writes). The last
# printed line is the machine-readable verdict the E1 grant keys on.
from sharpelab_nb.thermometry import assert_thermometry_live
_fails = []
def _chk(name, ok, detail):
    print(f"[{'OK  ' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        _fails.append(name)
def _vr(p):
    v = p.vals
    return (getattr(v, "_min_value", None), getattr(v, "_max_value", None))

# 1. Magnet at 0 T, output + persistent switch on
try:
    _B, _Bs = magnet.field(), magnet._status()["field"]
    print(_B, _Bs)
    _chk("magnet-zero", abs(_B) < 0.02 and abs(_Bs) < 0.02, f"field()={_B:.4f} T, _status field={_Bs:.4f} T")
    _chk("magnet-output", bool(magnet.output_enabled()) and bool(magnet.persistent_switch_on()),
         f"output_enabled={magnet.output_enabled()}, persistent_switch_on={magnet.persistent_switch_on()}")
except Exception as e:
    _chk("magnet-read", False, repr(e))

# 2. SAFETIES committed == device card operating limits (exact numbers)
_card = {
    "k_2400_tg.volt": (k_2400_tg.volt, (-0.3, 1.0)),
    "k_2400_bg.volt": (k_2400_bg.volt, (-1.3, 2.0)),
    "dc205.smart_voltage": (dc205.smart_voltage, (-25.0, 25.0)),
    "dc205.voltage": (dc205.voltage, (-25.0, 25.0)),
    "magnet.field": (magnet.field, (-10.0, 10.0)),
    "heater.sample_setpoint": (heater.sample_setpoint, (0.0, 100.0)),
    "heater.vaporizer_setpoint": (heater.vaporizer_setpoint, (0.0, 100.0)),
}
for _name, (_p, _want) in _card.items():
    _got = _vr(_p)
    _chk(f"safeties:{_name}", _got == _want, f"validator {_got} vs card {_want}")

# 3. Base T holding, logfile live (mtime advancing)
try:
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
    _Ts, _Tv = T_sample(), T_vaporizer()
    _chk("base-T", 1.0 <= _Ts <= 1.4, f"T_sample={_Ts:.3f} K (want ~1.2-1.3)")
    _chk("vaporizer-tracking", abs(_Tv - _Ts) < 0.5, f"T_vaporizer={_Tv:.3f} K vs T_sample={_Ts:.3f} K")
except Exception as e:
    _chk("thermometry", False, repr(e))

# 4. Heaters off (both ranges 0), setpoints noted
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
_chk("heaters-off", _rs == 0 and _rv == 0,
     f"sample_range={_rs}, vaporizer_range={_rv}; setpoints {heater.sample_setpoint()} / {heater.vaporizer_setpoint()} K")

# 5. Contacts hardwired per device card (no mux this cooldown)
_want_wiring = {"source": "T_0", "drain": "B_3", "sr1+": "B_1", "sr1-": "B_2",
                "sr2+": "n.c.", "sr2-": "n.c.", "sr3+": "n.c.", "sr3-": "n.c."}
_chk("wiring-map", WIRING == _want_wiring, f"WIRING={WIRING}")
_chk("no-mux", globals().get("mux") is None, f"mux in namespace: {'mux' in globals()}")
_chk("meas-config", meas_config.get("sr1") == "B_1 - B_2" and meas_config.get("sr0_gain") == -1e6
     and meas_config.get("source") == "T_0" and meas_config.get("bias_channel") == "sr1",
     f"sr1={meas_config.get('sr1')}, sr0_gain={meas_config.get('sr0_gain')}, source={meas_config.get('source')}")

# 6. DC205 on +/-100 V range, output on, 0 V
_rng, _out, _Vsi = dc205.voltage_range(), dc205.output(), dc205.voltage()
_chk("dc205", int(_rng) == 2 and int(_out) == 1 and abs(_Vsi) < 0.01,
     f"range={_rng} (want 2), output={_out} (want 1), voltage={_Vsi} V")

# 7. Gates at 0 V
_Vtg, _Vbg = k_2400_tg.volt(), k_2400_bg.volt()
_chk("gates-zero", abs(_Vtg) < 1e-3 and abs(_Vbg) < 1e-3, f"V_tg={_Vtg} V, V_bg={_Vbg} V")

# Informational: lock-in / pacing state (operator-set; recorded, not gated)
for _s in (sr0, sr1):
    print(f"[info] {_s.name}: sens={_s.sensitivity()} V, tau={_s.time_constant()} s, slope={_s.filter_slope()} dB/oct")
print(f"[info] drive sr1.amplitude={sr1.amplitude()} V @ {sr1.frequency()} Hz -> I_bias={sr1.amplitude()/meas_config['bias_resistor']*1e9:.2f} nA")
print(f"[info] dc205.ramp_rate={dc205.ramp_rate} V/s, k_tg.volt.step={k_2400_tg.volt.step}, k_bg.volt.step={k_2400_bg.volt.step}")

print("VERIFY: ALL GREEN" if not _fails else f"VERIFY: FAIL {_fails[0]}")
