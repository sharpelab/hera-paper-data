# HERA — E1 kernel-binding probe (read-only namespace check, no hardware traffic)
import os
print("cwd            :", os.getcwd())
names = ["magnet", "heater", "sr0", "sr1", "sr2", "sr3",
         "k_2400_tg", "k_2400_bg", "dc205", "k_tg", "k_bg", "k_si",
         "T_sample", "T_vaporizer", "meas_config", "WIRING", "cal"]
missing = [n for n in names if n not in globals()]
print("namespace      :", "all bound" if not missing else f"MISSING: {missing}")
assert not missing, f"not the instrument-carrying kernel: missing {missing}"
print("k_tg -> %s | k_bg -> %s | k_si -> %s" % (k_tg.name, k_bg.name, k_si.full_name))
print("T_sample (file):", T_sample(), "K")
print("\nkernel-binding probe: PASS")
