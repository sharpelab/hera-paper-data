# HERA — close-out: return-to-initial, per the session brief.
# Field to 0, all three gates to 0 V at their committed pacing, both heater ranges off,
# then a readback of field, gates and temperatures for the session log.
print("=== close-out: return-to-initial ===")
print(f"start: B = {magnet.field():+.4f} T | V_tg = {k_tg.volt():+.4f} V | "
      f"V_bg = {k_bg.volt():+.4f} V | V_si = {dc205.voltage():+.4f} V")
print(f"       T_sample = {T_sample():.3f} K | T_vaporizer = {T_vaporizer():.3f} K | "
      f"heater ranges {heater.sample_range()}/{heater.vaporizer_range()}")

# --- heaters off FIRST so the sample starts cooling while everything else ramps ---
heater.off("both")
print(f"heaters off -> ranges {heater.sample_range()}/{heater.vaporizer_range()}")

# --- gates to 0 V, each at its own committed pacing -------------------------------
# Keithleys sub-step at volt.step = 5 mV; the DC205 ramps at ramp_rate = 0.5 V/s.
# Si is already at 0 and its ramp is consent-gated, so it is only set if it has moved.
k_tg.volt(0.0)
k_bg.volt(0.0)
print(f"gates: V_tg = {k_tg.volt():+.4f} V | V_bg = {k_bg.volt():+.4f} V")
_vsi = dc205.voltage()
if abs(_vsi) > 1e-3:
    print(f"Si is at {_vsi:+.4f} V — NOT ramping it here (the DC205 ramp is consent-gated); "
          f"flagging for the operator")
else:
    print(f"Si: {_vsi:+.4f} V — already at zero, untouched all session")

# --- field to zero (blocking; the magnet has no abort, only a new setpoint) --------
_B = magnet.field()
if abs(_B) > 0.02:
    print(f"ramping B {_B:+.4f} -> 0.000 T (blocking, ~{abs(_B)/0.137:.1f} min) ...")
    magnet.field(0.0)

# --- final readback ---------------------------------------------------------------
print("\n=== final state ===")
print(f"B            = {magnet.field():+.5f} T   (measured readback)")
print(f"magnet       : psw={magnet.persistent_switch_on()} output={magnet.output_enabled()}")
print(f"V_tg         = {k_tg.volt():+.5f} V")
print(f"V_bg         = {k_bg.volt():+.5f} V")
print(f"V_si         = {dc205.voltage():+.5f} V")
print(f"gate leakage : TG {k_2400_tg.curr()*1e12:+.1f} pA | BG {k_2400_bg.curr()*1e12:+.1f} pA")
print(f"T_sample     = {T_sample():.3f} K")
print(f"T_vaporizer  = {T_vaporizer():.3f} K")
print(f"heater ranges= {heater.sample_range()} (sample) / {heater.vaporizer_range()} (vaporizer)")
print(f"sr0          : sens {sr0.sensitivity():.3g} V, tau {sr0.time_constant():g} s, "
      f"slope {sr0.filter_slope():g} dB/oct")
print(f"sr1          : sens {sr1.sensitivity():.3g} V, tau {sr1.time_constant():g} s, "
      f"slope {sr1.filter_slope():g} dB/oct")
print(f"drive        : {sr1.amplitude()} V @ {sr1.frequency()} Hz")
print("\nNOTE: sr1 sensitivity (2 uV -> 1 mV) and sr0/sr1 tau (0.3 -> 0.1 s) were changed "
      "this session with operator authorisation; they are NOT restored to state0, since the "
      "session-start values were wrong for this device (sr1 was railed at 2 uV).")
print("close-out complete — the sample is left cooling toward base with all gates and the "
      "field at zero.")
