# E1 kernel-binding probe (read-only). First autonomous execute: confirm this
# execution path is bound to the operator's instrument-carrying kernel before
# any measure cell runs. No hardware writes.
need = ['magnet', 'heater', 'sr0', 'sr1', 'sr2', 'sr3',
        'k_2400', 'k_2410', 'dc205', 'qsw', 'mux', 'meas_config']
g = set(globals())
missing = [n for n in need if n not in g]
print("namespace missing:", missing if missing else "none")
print("kernel pid       :", os.getpid())
print("magnet obj id    :", id(magnet))
print("sample T (live)  :", heater.sample_temperature(), "K")
print("magnet B (live)  :", magnet.field(), "T")
print("Si gate (live)   :", k_2410.volt(), "V")
