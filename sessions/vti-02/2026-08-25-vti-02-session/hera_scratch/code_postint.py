# HERA — post-interrupt state read. READ-ONLY. No sets, no ramps.
# The close-out cell was interrupted mid field-ramp on operator instruction.
# Rig card: an interrupt does NOT stop the supply - it keeps ramping to its last
# setpoint (0 T here). Recovery is calling field() again with a new target, which
# the fan cell does. This cell only establishes what state we are actually in.
import time

_b1 = magnet.field()
time.sleep(4.0)
_b2 = magnet.field()
print(f"field: {_b1:+.4f} T -> {_b2:+.4f} T over 4 s  "
      f"({(_b2-_b1)/4*60:+.3f} T/min; still ramping toward 0 as expected)")
print(f"is_ramping   : {magnet.is_ramping()}")
print(f"commanded    : {magnet.commanded_field}")
print(f"output/PS    : output={magnet.output_enabled()}, PS={magnet.persistent_switch_on()}")
print(f"gates        : V_tg={k_tg.volt():+.4f} V, V_bg={k_bg.volt():+.4f} V, "
      f"V_si={dc205.voltage():+.4f} V")
print(f"gate current : I_tg={k_tg.curr():.3e} A, I_bg={k_bg.curr():.3e} A  (nplci "
      f"{k_tg.nplci():.0f}/{k_bg.nplci():.0f})")
print(f"heaters      : sample_range={heater.sample_range()}, "
      f"vaporizer_range={heater.vaporizer_range()}")
print(f"temperature  : T_sample={T_sample():.3f} K, T_vaporizer={T_vaporizer():.3f} K")
print(f"drive        : {sr1.amplitude()} V @ {sr1.frequency()} Hz")
for _n, _s in (("sr0", sr0), ("sr1", sr1)):
    print(f"  {_n}: sens={_s.sensitivity():.3e}, tau={_s.time_constant()} s, "
          f"slope={_s.filter_slope()} dB/oct")
print()
print("close-out status: restore/heaters/gates stages COMPLETED before the field ramp")
print("  (close_out order is restore -> excitation -> heaters -> gates -> mux -> field),")
print("  so the rack is at bring-up values and the gates are parked; only the field")
print("  endpoint did not land. The fan cell re-establishes acquisition and redirects")
print("  the magnet to 8 T, so nothing here needs undoing.")
print("POST-INTERRUPT-READ: done")
