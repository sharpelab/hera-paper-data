# HERA — E1 kernel-binding probe. READ-ONLY BY CONSTRUCTION: no instrument
# gets, no VISA/TCP traffic, no writes. Namespace inspection only.
import os

import qcodes

_g = globals()
_expected = [
    "main_dir", "magnet", "heater", "sr0", "sr1", "sr2", "sr3",
    "k_2400_tg", "k_2400_bg", "dc205", "k_tg", "k_bg", "k_si",
    "T_sample", "T_vaporizer", "cal", "meas_config", "WIRING", "state0",
    "TG_MIN", "TG_MAX", "BG_MIN", "BG_MAX", "SI_MIN", "SI_MAX",
    "B_SESSION_CAP", "T_SESSION_CAP", "sanitize_tg_bg", "spoints",
]
_missing = [n for n in _expected if n not in _g]

print(f"pid                   : {os.getpid()}")
print(f"cwd                   : {os.getcwd()}")
print(f"main_dir              : {_g.get('main_dir')}")
try:
    print(f"sweep basedir         : {sweep.get_basedir()}")
except Exception as _e:
    print(f"sweep basedir         : (not readable: {type(_e).__name__})")
print(f"qcodes instruments    : {sorted(qcodes.Instrument._all_instruments)}")
print(f"id(magnet)            : {id(_g.get('magnet'))}")
print(f"id(dc205)             : {id(_g.get('dc205'))}")
print(f"missing globals       : {_missing if _missing else 'none'}")

print()
print("PROBE: BOUND" if not _missing else f"PROBE: NOT BOUND (missing {_missing})")
