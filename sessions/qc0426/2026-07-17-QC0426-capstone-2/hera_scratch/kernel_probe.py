# HERA — kernel-binding probe (read-only, namespace-only): confirm the
# nb-collab execute path is bound to the operator's instrument-carrying kernel.
_expected = ["magnet", "heater", "sr0", "sr1", "sr2", "sr3",
             "k_2400_tg", "k_2400_bg", "dc205", "k_tg", "k_bg", "k_si",
             "T_sample", "T_vaporizer", "cal", "meas_config", "WIRING"]
_missing = [n for n in _expected if n not in globals()]
print("bound instruments:", [n for n in _expected if n not in _missing])
print("main_dir:", main_dir)
print("KERNEL PROBE: OK" if not _missing else f"KERNEL PROBE: MISSING {_missing}")
