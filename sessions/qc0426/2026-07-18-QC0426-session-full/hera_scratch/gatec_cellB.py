# === Gate C reset — restore standard gate-current nplci ===
# Run ONLY after all four legs read clean from disk (HERA executes post-verification).
k_2400_tg.nplci(1)
k_2400_bg.nplci(1)
print("k_tg.volt validator:", k_2400_tg.volt.vals)
print("k_bg.volt validator:", k_2400_bg.volt.vals)
print("nplci reset to 1 on both Keithleys")
