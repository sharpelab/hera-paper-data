# === Session close-out (`session-closeout` + VTI variant): ask = return-to-initial ===
# Replay state0 (bring-up capture), heaters off via the labeled callable (LS335 ranges),
# gates to 0 through their ramped params, field explicitly to 0 T (session-start field; VERIFY read +0.006 T).
# No mux this cooldown (hardwired) -> mux omitted. Excitation parks at the standing value via state0.
from sharpelab_nb.closeout import close_out

_T0 = T_sample()
print(f"pre-closeout: T_sample {_T0:.2f} K, B {magnet.field():+.3f} T, heaters {heater.sample_range()}/{heater.vaporizer_range()}, "
      f"Vtg {k_tg.volt():+.3f}, Vbg {k_bg.volt():+.3f}, Vsi {k_si():+.3f}")

close_out(
    (magnet.field, 0.0),                       # return-to-initial: session-start field (VERIFY: +0.006 T readback offset)
    restore=state0,                            # bring-up acquisition + gate state (drive 1 V, taus, sens, gates 0)
    heaters=[("LS335 ranges off", lambda: heater.off("both"))],
    gates=[(k_tg.volt, 0.0), (k_bg.volt, 0.0), (k_si, 0.0)],   # Si through the ramped parameter (never raw voltage)
    extra_readback={"T_sample": T_sample, "T_vaporizer": T_vaporizer},
)
