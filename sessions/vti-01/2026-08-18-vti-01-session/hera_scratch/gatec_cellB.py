# === Gate C — Cell B: reset gate-current nplci ===
# Run only after every leg looked safe. Undo Cell A's nplci bump; rangei stays
# at 1e-9 (pA-resolution leakage watch is the session default). Validators were
# committed in SAFETIES — print to confirm, nothing re-committed.
k_tg.nplci(1)
k_bg.nplci(1)
print("k_tg.volt validator:", k_tg.volt.vals)
print("k_bg.volt validator:", k_bg.volt.vals)
print("nplci:", k_tg.nplci(), k_bg.nplci(), "| rangei:", k_tg.rangei(), k_bg.rangei())
