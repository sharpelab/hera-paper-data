# === Session close-out: return-to-initial (brief's ask; session-closeout + VTI variant) ===
# Field endpoint per the ask = session-start field (0 T; VERIFY read 0.006 T).
# restore = state0 (bring-up capture): drive 4 mV, sensitivities, taus, NPLC, gates.
# Heaters: LS335 ranges off (VTI delta; already off after the ladder — idempotent).
# Si park through the ramped parameter (VTI delta) — k_si is in state0 (V_si = 0).
# No mux this cooldown (hardwired) — mux= omitted. PS/output untouched (operator-only).

_T = T_sample()
print(f"pre-closeout: B={magnet.field():+.3f} T, T={_T:.3f} K (recooling from ladder), "
      f"Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f}, Vsi={dc205.voltage():+.2f}")

from sharpelab_nb.closeout import close_out
close_out(
    (magnet.field, 0.0),
    restore=state0,
    heaters=[("LS335 ranges off", lambda: heater.off("both"))],
    gates=[(k_tg.volt, 0.0), (k_bg.volt, 0.0), (dc205.smart_voltage, 0.0)],
    extra_readback={"T_sample": T_sample, "T_vaporizer": T_vaporizer},
)
