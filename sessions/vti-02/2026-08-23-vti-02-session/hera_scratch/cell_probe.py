# HERA — kernel-binding probe (read-only). First E1 execute: confirms this
# execute path is bound to the operator's instrument-carrying kernel.
import os
_expect = ["magnet", "heater", "sr0", "sr1", "sr2", "sr3", "k_2400_tg", "k_2400_bg",
           "dc205", "k_tg", "k_bg", "k_si", "T_sample", "T_vaporizer", "cal",
           "meas_config", "WIRING", "state0", "main_dir"]
_missing = [n for n in _expect if n not in globals()]
print(f"pid={os.getpid()} cwd={os.getcwd()}")
print(f"main_dir={main_dir!r}" if "main_dir" in globals() else "main_dir: MISSING")
print("missing names:", _missing or "none")
print("magnet.field validator:", magnet.field.vals if "magnet" in globals() else "n/a")
print("KERNEL-BIND:", "OK" if not _missing else "FAIL")
