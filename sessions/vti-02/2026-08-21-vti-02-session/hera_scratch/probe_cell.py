# HERA — E1 kernel-binding probe (read-only). Confirms an nb-collab execute
# lands in the operator's instrument-carrying kernel, not a fresh python3.
import os as _os
_expected = ['magnet', 'heater', 'sr0', 'sr1', 'sr2', 'sr3', 'k_2400_tg', 'k_2400_bg',
             'dc205', 'k_tg', 'k_bg', 'k_si', 'T_sample', 'T_vaporizer', 'cal',
             'meas_config', 'WIRING', 'state0', 'main_dir', 'tg_lims', 'bg_lims']
_missing = [n for n in _expected if n not in globals()]
print("cwd:     ", _os.getcwd())
print("main_dir:", globals().get('main_dir'))
print("missing names:", _missing or "none")
_bound = False
if not _missing:
    print(f"magnet={type(magnet).__name__}  heater={type(heater).__name__}  dc205={type(dc205).__name__}  k_tg is k_2400_tg={k_tg is k_2400_tg}")
    print(f"sr1 drive {sr1.amplitude()} V @ {sr1.frequency()} Hz | T_sample {T_sample():.3f} K | magnet.field {magnet.field():.4f} T")
    _bound = _os.path.samefile(_os.getcwd(), main_dir)
print("PROBE:", "BOUND" if _bound else "FAIL " + (",".join(_missing) or "cwd!=main_dir"))
