"""Fan design numbers: model F(n) table (electron side), run-6 onset on the properly sampled record, R(n,B=0) on D=0."""
import sys, json, warnings
from pathlib import Path
import numpy as np
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, fan_grids, resistance_grids
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M
from sharpelab_nb.gates import calc_nD
D = Path(__file__).resolve().parent.parent / "data"
print("n12   F_L    ABAB(F,m*)                      ratio  3*light  ABCA F m*")
for n12 in [1.2, 1.5, 1.8, 2.0, 2.2, 2.5, 2.8, 3.0, 3.25, 3.65]:
    abm = M.abab_mstar(n12 * 1e16); ac = M.abca_mstar(n12 * 1e16)
    FL = float(luttinger_frequency(n12 * 1e16))
    Fs = [F for F, m in abm]
    print(f"{n12:4.2f} {FL:6.2f}  {[(round(F,2), round(m,3)) for F,m in abm]}  {Fs[-1]/Fs[0]:5.2f}  {3*Fs[0]:6.2f}  {float(ac[0]):6.2f} {float(ac[1]):.3f}")
r = open_run(D / "6"); B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)
for blo in (1.0, 1.2):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, r_full_scale=5000, b_lo=blo)
    print(f"--- run 6 onset, b_lo {blo}"); print(on.summary()); [print("  warn:", x.message) for x in w]
# B-window split on run 6
for br in [(1.2, 3.0), (3.0, 10.0), (1.2, 10.0), (2.0, 10.0)]:
    f, s = sdh_fft(R[:, None], B, b_range=br, bg_degree=5, nfft=16384, log=False); s = s[0]
    from scipy.signal import find_peaks
    pk, _ = find_peaks(s, prominence=0.08 * s.max()); top = sorted(pk, key=lambda p: -s[p])[:6]
    print(f"run 6 FFT B {br}: dF_rec {1/(1/br[0]-1/br[1]):.2f} T; peaks", sorted((round(float(f[p]),1), round(float(s[p]/s.max()),2)) for p in top if f[p] > 2))
# R(n, B=0) along D = 0 from run 5 (region-A cal)
cal = json.load(open(Path(__file__).parent / "cal_run5.json"))
g = fan_grids(str(D / "5")); rg = resistance_grids(g); R5 = np.abs(rg.R["sr1"])
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0] if isinstance(fs[0], list) else fs); Vbg = g.slow
N, Dd = calc_nD(Vtg[None, :], Vbg[:, None], cal["c_tg"], cal["c_bg"], cal["n_offset"], cal["D_offset"])
for n12 in [1.0, 1.5, 1.8, 2.0, 2.5, 3.0, 3.2]:
    m = (np.abs(N - n12) < 0.12) & (np.abs(Dd) < 0.02)
    print(f"R(n={n12}, D~0, B=0) = {np.median(R5[m]):.0f} Ohm ({m.sum()} px)")
