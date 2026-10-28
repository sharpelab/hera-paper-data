# Post-abort state re-read (read-only). Run 1 (gate map) died on an LS335 per-point
# VISA timeout; the cell's gate-park line did not execute, so gates are mid-position.
print("sample_T =", heater.sample_temperature(), "K")     # single read (safe; not per-point)
print("B =", magnet.mag(), "T   PS_on =", magnet.persistent_switch_on())
print("TG (dc205.voltage) =", dc205.voltage(), "V")
print("BG (k_2400.volt)   =", k_2400.volt(), "V")
print("Si (k_2410.volt)   =", k_2410.volt(), "V")
_I = sr0.X() / abs(meas_config["sr0_gain"])
print("I_meas =", _I*1e9, "nA   (contacts live if ~few nA)")
