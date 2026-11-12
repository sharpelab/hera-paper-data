# === Close-out: return-to-initial (session-closeout + VTI variant) ===
# Preconditions: nothing sweeping; heaters may still be lifting from the ladder (off below, first).
from sharpelab_nb.closeout import close_out
_st = magnet._status()
print(f"pre: B {magnet.field():+.3f} T | T_s {T_sample():.3f} T_v {T_vaporizer():.3f} K | heater ranges {heater.sample_range()},{heater.vaporizer_range()} | gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}, Si {dc205.voltage():+.3f}) | output {_st['output_enabled']} PS {_st['persistent_switch_on']}")
assert _st['output_enabled'] and _st['persistent_switch_on']

# Ask: return-to-initial -> replay state0 (drive 1.0 V @ 13.777 Hz, sr sens/tau as at bring-up, NPLC 1, gates 0, Si 0),
# LS335 ranges off (VTI variant: labelled callable), gates to 0 through their own ramped parameters, field to the
# session-start value 0 T (bring-up read 0.006 T). The field ramp blocks (~73 min from 10 T). No mux this cooldown.
# Persistent switch / output: operator-only, untouched.
close_out(
    (magnet.field, 0.0),
    restore=state0,
    heaters=[("LS335 ranges off", lambda: heater.off("both"))],
    gates=[(k_tg.volt, 0.0), (k_bg.volt, 0.0), (k_si, 0.0)],
    extra_readback={"T_sample": T_sample, "T_vaporizer": T_vaporizer,
                    "sample_range": heater.sample_range, "vaporizer_range": heater.vaporizer_range,
                    "sr1_sens": sr1.sensitivity, "sr1_tau": sr1.time_constant, "sr0_sens": sr0.sensitivity, "sr0_tau": sr0.time_constant,
                    "Si_V": dc205.voltage, "dc205_range": dc205.voltage_range, "dc205_output": dc205.output},
)
