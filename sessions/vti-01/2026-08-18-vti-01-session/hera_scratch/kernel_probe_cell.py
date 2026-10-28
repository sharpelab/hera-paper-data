# E1 kernel-binding probe — read-only namespace check, no instrument I/O.
# Confirms the nb-collab execute path is bound to the operator's
# instrument-carrying kernel (brief [VERIFY], kernel-binding item).
_need = ["magnet", "heater", "sr0", "sr1", "sr2", "sr3",
         "k_2400_tg", "k_2400_bg", "dc205", "k_tg", "k_bg", "k_si",
         "T_sample", "T_vaporizer", "cal", "meas_config", "WIRING", "state0",
         "tg_lims", "bg_lims", "B_SESSION_CAP", "T_SESSION_CAP"]
_missing = [n for n in _need if n not in globals()]
print("cwd:", os.getcwd())
print("qcodes instruments:", sorted(qcodes.Instrument._all_instruments))
print("missing names:", _missing)
print("KERNEL-BINDING:", "OK" if not _missing else f"FAIL {_missing}")
