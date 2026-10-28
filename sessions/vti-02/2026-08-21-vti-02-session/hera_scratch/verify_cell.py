# HERA — VERIFY (read-only by construction: every call below is a get; no
# instrument writes). The LAST printed line is the machine-readable verdict
# the E1 grant keys on: 'VERIFY: ALL GREEN' or 'VERIFY: FAIL <items>'.
from qcodes import validators as _v
_fails = []
def _chk(name, ok, detail):
    print(f"[{'ok  ' if ok else 'FAIL'}] {name}: {detail}")
    if not ok:
        _fails.append(name)

# 1. Magnet at 0 T (measured readback, both paths), output + PS heater on
_st = magnet._status(); _Bf = magnet.field()
_chk("magnet_zero", abs(_Bf) < 0.02 and abs(_st['field']) < 0.02,
     f"field()={_Bf:.4f} T, _status field={_st['field']:.4f} T (|B| < 20 mT)")
_chk("magnet_output", bool(_st['output_enabled']) and bool(_st['persistent_switch_on']),
     f"output_enabled={_st['output_enabled']}, persistent_switch_on={_st['persistent_switch_on']}")

# 2. SAFETIES committed == device-card operating limits (numbers, not eyeball)
def _lims(p):
    v = p.vals
    return (float(v._min_value), float(v._max_value)) if isinstance(v, _v.Numbers) else None
_exp = {"k_2400_tg.volt": (-0.3, 1.0), "k_2400_bg.volt": (-1.3, 2.0),
        "dc205.smart_voltage": (-25.0, 25.0), "dc205.voltage": (-25.0, 25.0),
        "magnet.field": (-10.0, 10.0),
        "heater.sample_setpoint": (0.0, 100.0), "heater.vaporizer_setpoint": (0.0, 100.0)}
_params = {"k_2400_tg.volt": k_2400_tg.volt, "k_2400_bg.volt": k_2400_bg.volt,
           "dc205.smart_voltage": dc205.smart_voltage, "dc205.voltage": dc205.voltage,
           "magnet.field": magnet.field,
           "heater.sample_setpoint": heater.sample_setpoint, "heater.vaporizer_setpoint": heater.vaporizer_setpoint}
for _k, _e in _exp.items():
    _got = _lims(_params[_k])
    _chk(f"safeties:{_k}", _got == _e, f"committed={_got}, card={_e}")

# 3. Thermometry worker live (logfile mtime advancing) + base T holding
try:
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
    _chk("thermometry_live", True, "both logfiles advancing")
except Exception as _ex:
    _chk("thermometry_live", False, f"{type(_ex).__name__}: {_ex}")
_Ts, _Tv = T_sample(), T_vaporizer()
_chk("base_T", 1.05 <= _Ts <= 1.45, f"T_sample={_Ts:.3f} K (band 1.05-1.45 K — heuristic around the card's 1.2-1.3 K)")
_chk("vaporizer_at_base", _Tv < 1.6, f"T_vaporizer={_Tv:.3f} K (tracking base, < 1.6 K)")

# 4. Heaters off (both LS335 ranges 0)
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
_chk("heaters_off", _rs == 0 and _rv == 0, f"sample_range={_rs}, vaporizer_range={_rv}")

# 5. Contacts hardwired per the device card's provided configuration; no mux bound
_exp_w = {"source": "T_0", "drain": "B_3", "sr1+": "B_1", "sr1-": "B_2", "sr2": "n.c.", "sr3": "n.c."}
_chk("contacts_hardwired", WIRING == _exp_w and 'mux' not in globals(),
     f"WIRING matches card={WIRING == _exp_w}, mux bound={'mux' in globals()}")

# 6. DC205 (Si): ±100 V range (RNGE 2), output on, 0 V
_rng, _out, _vsi = dc205.voltage_range(), dc205.output(), dc205.voltage()
_chk("dc205", _rng == 2 and _out == 1 and abs(_vsi) < 0.01,
     f"range={_rng} (need 2), output={_out} (need 1), V={_vsi:.4f} (need 0)")
_chk("dc205_ramp_rate", dc205.ramp_rate == 0.5, f"ramp_rate={dc205.ramp_rate} V/s (setup value 0.5; consent-gated)")

# 7. Keithley gates at 0 V (state0 capture said 0/0)
_vtg, _vbg = k_2400_tg.volt(), k_2400_bg.volt()
_chk("gates_zero", abs(_vtg) < 0.005 and abs(_vbg) < 0.005, f"V_tg={_vtg:.4f} V, V_bg={_vbg:.4f} V")

# 8. Lock-ins reading (informational — gate A 'lock-ins reading')
print(f"[info] sr0 X={sr0.X():.3e} V sens={sr0.sensitivity()} tau={sr0.time_constant()} | "
      f"sr1 X={sr1.X():.3e} V sens={sr1.sensitivity()} tau={sr1.time_constant()} | "
      f"drive {sr1.amplitude()} V @ {sr1.frequency()} Hz -> I_bias={sr1.amplitude()/meas_config['bias_resistor']*1e9:.1f} nA")
# He budget: operator-attested (AMI 1700 is not bound in this kernel) — recorded in the markdown above.

print("VERIFY: ALL GREEN" if not _fails else "VERIFY: FAIL " + ",".join(_fails))
