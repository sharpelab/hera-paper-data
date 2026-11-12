# HERA — session close-out. Ask: return-to-initial (session brief).
# recipe: utils/session-closeout.md + session-closeout-vti.md
#   - field endpoint = the session-start field (VERIFY read +0.0063 T -> 0.0)
#   - restore = state0, the bring-up capture (drive back to 1.0 V, lock-in
#     sens/tau/slope back to bring-up values, gates to 0)
#   - heaters off via the labelled callable (closed-loop LS335, VTI variant)
#   - Si parks through k_si / smart_voltage, never raw voltage (VTI variant)
#   - no mux= : hardwired breakout this cooldown
#   - persistent switch / output are operator-only; close-out never touches them
from sharpelab_nb.closeout import close_out

print(f"pre-closeout: B={magnet.field():+.4f} T, V_tg={k_tg.volt():+.4f}, "
      f"V_bg={k_bg.volt():+.4f}, V_si={dc205.voltage():+.4f}, "
      f"T_sample={T_sample():.3f} K, T_vap={T_vaporizer():.3f} K")
print(f"ramp home from {magnet.field():+.3f} T at 0.137 T/min ~ "
      f"{abs(magnet.field())/0.137:.0f} min")

close_out(
    (magnet.field, 0.0),
    restore=state0,
    heaters=[("LS335 ranges off", lambda: heater.off("both"))],
    gates=[(k_tg.volt, 0.0), (k_bg.volt, 0.0), (k_si, 0.0)],
    extra_readback={
        "T_sample": T_sample, "T_vaporizer": T_vaporizer,
        "I_tg": k_tg.curr, "I_bg": k_bg.curr,
        "sample_range": heater.sample_range, "vaporizer_range": heater.vaporizer_range,
    },
)
