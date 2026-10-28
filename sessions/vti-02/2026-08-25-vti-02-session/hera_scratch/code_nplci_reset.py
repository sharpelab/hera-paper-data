# HERA — gate-current-sanity-check Cell B: reset gate-current nplci.
# Validators were committed in SAFETIES (cell 18) — nothing to re-commit here.
# Run only after every leg looked safe.
k_tg.nplci(1)
k_bg.nplci(1)
print(f"nplci reset: k_tg={k_tg.nplci()}, k_bg={k_bg.nplci()}")
print("k_tg.volt validator:", k_tg.volt.vals)
print("k_bg.volt validator:", k_bg.volt.vals)
print("dc205.smart_voltage validator:", dc205.smart_voltage.vals)
print("magnet.field validator:", magnet.field.vals)
print(f"gates: V_tg={k_tg.volt():+.4f} V, V_bg={k_bg.volt():+.4f} V, V_si={dc205.voltage():+.4f} V")
print(f"currents: I_tg={k_tg.curr():.3e} A, I_bg={k_bg.curr():.3e} A")
print(f"B={magnet.field():+.4f} T, T_sample={T_sample():.3f} K")
