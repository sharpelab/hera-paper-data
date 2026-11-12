# --- Gate C close-out: reset gate-current nplci (run only if all four legs clean) ---
k_tg.nplci(1); k_bg.nplci(1)
print("k_tg.volt validator:", k_tg.volt.vals)
print("k_bg.volt validator:", k_bg.volt.vals)
print("gates parked:", k_tg.volt(), k_bg.volt(), k_si())
