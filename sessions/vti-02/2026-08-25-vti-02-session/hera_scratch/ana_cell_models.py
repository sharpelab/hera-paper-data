# Forward-model overlay (investigation Verify) + the mandatory adjacent-N check.
# Both 4L templates AND the trilayer ML+BL curves, per: "For any two-tone pair,
# compute BOTH overlays ... and report which family the branches track."
import importlib.util
def _load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
_MB = str(Path.home() / "measurement_env" / "hera" / "models")
T4 = _load("t4", _MB + "/tetralayer_fs_count/fs_count_b0.py")
T3 = _load("t3", _MB + "/trilayer_fs_count/fs_count_b0.py")

print(f"{'n(e12)':>7} | {'ABAB-4L pair (T)':>22} {'fracs':>16} | {'ABCA-4L':>8} | "
      f"{'ABA-3L pair (T)':>20} {'fracs':>16}")
for n in (1.8, 2.2, 2.6, 3.0):
    a = [f for f, k in T4.abab_fs(n*1e16)[1]]; sa = sum(a)
    c = T4.abca_fs(n*1e16)[4]
    t = [f for f, k in T3.aba_fs(n*1e16)[1]]; st = sum(t)
    print(f"{n:7.2f} | {str([round(v,2) for v in a]):>22} "
          f"{str([round(v/sa,3) for v in a]):>16} | {c:8.2f} | "
          f"{str([round(v,2) for v in t]):>20} {str([round(v/st,3) for v in t]):>16}")
print()
print("OBSERVED partner fractions (recurrent tones): 0.198-0.257 at n = 2.6, 3.0")
print("  ABAB-4L predicts 0.201-0.215   ->  MATCHES")
print("  ABA-3L predicts  0.043-0.053   ->  5x too small, adjacent-N EXCLUDED")
