# === Kernel-binding probe (read-only) ===
# First E1 act after the grant: confirms the nb-collab execute path lands on the
# operator's instrument-carrying kernel (the one that ran Setup + SAFETIES), not
# a fresh python3 kernel. Touches no instrument — namespace only.
import os
_need = ['magnet', 'heater', 'sr0', 'sr1', 'sr2', 'sr3', 'k_2400_tg', 'k_2400_bg',
         'dc205', 'k_tg', 'k_bg', 'k_si', 'T_sample', 'T_vaporizer', 'meas_config',
         'WIRING', 'state0', 'cal', 'B_SESSION_CAP', 'T_SESSION_CAP', 'tg_lims', 'bg_lims']
_missing = [n for n in _need if n not in globals()]
print(f"pid {os.getpid()} | main_dir {main_dir if 'main_dir' in globals() else '<unset>'}")
print(f"present: {len(_need) - len(_missing)}/{len(_need)} | missing: {_missing}")
print("KERNEL PROBE:", "BOUND" if not _missing else "UNBOUND")
