import sys, importlib.util, numpy as np
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
m4 = load("m4", "/home/hera/measurement_env/hera/models/tetralayer_fs_count/fs_count_b0.py")
m3 = load("m3", "/home/hera/measurement_env/hera/models/trilayer_fs_count/fs_count_b0.py")
print(" n12   F_L   ABAB F (m*)                      part   | ABCA F m*   | tri-ABA F")
for n12 in [1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6]:
    n = n12 * 1e16; FL = n12 * 1e16 * 4.1357e-15 / 4
    fs = sorted(m4.abab_fs(n)[1]); ms = m4.abab_mstar(n)
    Fa, ma = m4.abca_mstar(n)
    try: f3 = sorted(m3.aba_fs(n)[1]); f3s = [round(F, 2) for F, *_ in f3]
    except Exception as e: f3s = str(e)[:30]
    Fs = [F for F, _ in fs]
    print(f"{n12:4.1f} {FL:6.2f}  {[round(F,2) for F in Fs]} {[round(x,3) for _, x in ms]}  {max(Fs)/sum(Fs):.3f} | {Fa:5.1f} {ma:.3f} | {f3s}")
