# KERNEL PROBE — read-only namespace check (first E1 act, pre-VERIFY).
# Confirms nb-collab execute-cell is bound to the operator's instrument-carrying
# kernel, not a fresh one. No instrument I/O beyond qcodes bookkeeping.
_need = ["magnet", "heater", "sr0", "sr1", "sr2", "sr3",
         "k_2400_tg", "k_2400_bg", "dc205", "k_tg", "k_bg", "k_si",
         "T_sample", "T_vaporizer", "cal", "meas_config", "WIRING"]
_missing = [n for n in _need if n not in globals()]
_live = sorted(qcodes.Instrument._all_instruments.keys())
print(f"bound instruments: {_live}")
print(f"missing names: {_missing if _missing else 'none'}")
if _missing:
    print("KERNEL PROBE: FAIL — not the instrument-carrying kernel")
else:
    print("KERNEL PROBE: OK — bound to the instrument-carrying kernel")
