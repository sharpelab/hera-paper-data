# HERA — E1 kernel-binding probe. READ-ONLY: no instrument writes, no sets,
# no ramps, no sweeps. Confirms this execute landed in the operator's
# instrument-carrying kernel (the one that ran Setup + SAFETIES) and not a
# fresh or unrelated one. Must pass before VERIFY runs.
import os
import qcodes

print(f"pid              : {os.getpid()}")
print(f"cwd              : {os.getcwd()}")
try:
    print(f"sweep BASEDIR    : {getattr(sweep, 'BASEDIR', '<unset>')}")
except Exception as e:
    print(f"sweep BASEDIR    : <error {e!r}>")

_g = globals()
_need = [
    "magnet", "heater", "sr0", "sr1", "sr2", "sr3",
    "k_2400_tg", "k_2400_bg", "dc205", "k_tg", "k_bg", "k_si",
    "T_sample", "T_vaporizer", "state0", "cal", "meas_config", "WIRING",
    "tg_lims", "bg_lims", "B_SESSION_CAP", "T_SESSION_CAP",
]
_missing = [n for n in _need if n not in _g]
print(f"namespace missing: {_missing if _missing else 'none'}")

try:
    _live = sorted(qcodes.Instrument._all_instruments)
except Exception as e:
    _live = f"<error {e!r}>"
print(f"live instruments : {_live}")

try:
    print(f"state0           : {len(state0)} keys, V_tg={state0.get('V_tg')} "
          f"V_bg={state0.get('V_bg')} V_si={state0.get('V_si')}")
except Exception as e:
    print(f"state0           : <error {e!r}>")

print("PROBE: BOUND" if not _missing else f"PROBE: NOT BOUND — missing {_missing}")
