# HERA — E1 kernel-binding probe (read-only): confirms nb-collab execute lands
# on the operator's instrument-carrying kernel before any autonomous measure cell.
import qcodes
print("instruments:", sorted(qcodes.Instrument._all_instruments.keys()))
print(f"magnet.field = {magnet.field():+.4f} T | T_sample = {T_sample():.3f} K | "
      f"Vtg = {k_tg.volt():+.3f} V | Vbg = {k_bg.volt():+.3f} V | Vsi = {dc205.voltage():+.3f} V")
print("sweep basedir:", sweep.get_basedir() if hasattr(sweep, "get_basedir") else main_dir)
print("binding OK")
