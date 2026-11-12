"""F_L-tone origin, test (1): B-window split. FFT the low-B and high-B halves (in 1/B) of run 5 and of fan columns;
a breakdown / intermodulation tone strengthens with B relative to the fundamentals, a real pocket keeps its own
Dingle envelope. Also test (2): grid-change reproduction — run 5 is uniform-B, run 8 columns are uniform-1/B.
"""
import warnings
import numpy as np
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft, luttinger_frequency

def peaks(freqs, sp, fmin=2.5, nmax=6):
    pk = [(freqs[i], sp[i]) for i in range(2, len(sp) - 2) if freqs[i] > fmin and sp[i] > sp[i-1] and sp[i] > sp[i+1]]
    return sorted(pk, key=lambda t: -t[1])[:nmax]

def amp_near(freqs, sp, f0, w=2.5):
    m = (freqs > f0 - w) & (freqs < f0 + w)
    return sp[m].max() if m.any() else np.nan

def split_report(label, R, B, f_light, f_heavy, f_sum, windows):
    print(f"--- {label}: light {f_light:.1f}, heavy {f_heavy:.1f}, sum {f_sum:.1f} T")
    for (blo, bhi) in windows:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            freqs, spec = sdh_fft(R[:, None], B, b_range=(blo, bhi), bg_degree=3, nfft=4096, log=False)
        sp = spec[0]
        aL, aH, aS = amp_near(freqs, sp, f_light), amp_near(freqs, sp, f_heavy), amp_near(freqs, sp, f_sum)
        dF = 1 / (1 / blo - 1 / bhi)
        print(f"  B {blo:.1f}-{bhi:.1f} T (dF {dF:.1f} T): amp light {aL:.3g}, heavy {aH:.3g}, sum {aS:.3g} | sum/heavy {aS/aH:.2f}, sum/light {aS/aL:.2f} | peaks: " + ", ".join(f"{f:.1f}" for f, _ in peaks(freqs, sp)))

# run 5 (uniform-B spot check, n_act ~ 2.7-2.8)
r = open_run("data/5"); mc = r.meta["measurement_config"]
B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / float(mc["sr0_gain"]))
split_report("run 5 spot (uniform B)", R, B, 6.2, 21.8, 28.1, [(2.4, 10.0), (2.4, 4.2), (4.2, 10.0), (2.4, 3.6), (3.6, 6.0), (6.0, 10.0)])

# run 8 columns (uniform 1/B)
f = fan_grids(open_run("data/8")); rg = resistance_grids(f); Bf = f.slow; Rf = rg.R["sr1"]
o = np.argsort(Bf); Bf = Bf[o]; Rf = Rf[o]
C_TG, C_BG, N_OFF = 2.7961e-3, 2.0330e-3, -0.069; e = 1.602176634e-19
n_d = (C_TG * f.grid("k_2400_tg_volt")[0] + C_BG * f.grid("k_2400_bg_volt")[0]) / e * 1e-16 + N_OFF
for j in (0, 4, 10, 20, 30):
    n_act = 0.93 * n_d[j]; FL = luttinger_frequency(n_act * 1e16)
    split_report(f"run 8 column n_act {n_act:.2f} (uniform 1/B; F_L {FL:.1f} at scale 0.93)", Rf[:, j], Bf, 0.21 * FL, 0.77 * FL, FL, [(2.4, 10.0), (2.4, 4.2), (4.2, 10.0)])
