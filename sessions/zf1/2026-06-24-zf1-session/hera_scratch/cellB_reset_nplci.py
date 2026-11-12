# === Reset gate-current nplci (run ONLY if every leg looked safe) ===
# Undo Cell A's nplci bump; print the live validators to confirm they're intact.
k_tg.nplci(1)
k_bg.nplci(1)
print("k_tg.volt validator:", k_tg.volt.vals)
print("k_bg.volt validator:", k_bg.volt.vals)
