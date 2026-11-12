"""Model F(n) / m*(n) table over the realized D = 0 window (n = -1.27 .. +3.27e12) for the fan design:
ABAB pair, ABCA singleton, F_L; plus the fan design numbers (Nyquist, delta-F, ray spacing) at candidate windows."""
import sys, numpy as np
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
from fs_count_b0 import abab_fs, abca_fs, abab_mstar, abca_mstar
from hera.analysis import luttinger_frequency
h_e = 4.135667696e-15  # T m^2
print(f"{'n(e12)':>7} {'F_L':>6} | ABAB tones (T) [m*/me]                | ABCA F (T) topo m*")
for n in [-1.27, -1.0, -0.8, -0.6, -0.4, 0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0, 3.27]:
    FL = float(luttinger_frequency(n * 1e16))
    ef, orb = abab_fs(n*1e16); ms = abab_mstar(n*1e16)
    ef2, topo, nc, nf, Ft = abca_fs(n*1e16); Fa, ma = abca_mstar(n*1e16)
    tones = " ".join(f"{f:5.1f}[{m:.3f}]" for (f, k), (_, m) in zip(orb, ms))
    print(f"{n:>7.2f} {FL:>6.1f} | {tones:<38} | {Ft:6.1f} {topo:<8} {ma:.3f}")

print("\n--- fan design arithmetic (electron side, D=0) ---")
for n_max in [3.2, 3.0]:
    FL = float(luttinger_frequency(n_max * 1e16))
    d_invB = 1 / (3 * FL)   # prefer 1/3
    for B_lo in [2.0, 2.5, 3.0]:
        for B_hi in [8.0, 10.0]:
            N_invB = int(np.ceil((1 / B_lo - 1 / B_hi) / d_invB)) + 1
            dB_unif = d_invB * B_lo ** 2
            N_unif = int(np.ceil((B_hi - B_lo) / dB_unif)) + 1
            dF = 1 / (1 / B_lo - 1 / B_hi)
            print(f"n_max {n_max}: F_L {FL:.1f} T, d(1/B) {d_invB*1e3:.2f} mT^-1 | B [{B_lo},{B_hi}]: N_1/B {N_invB}, uniform-B dB {dB_unif*1e3:.0f} mT N {N_unif}; dF {dF:.2f} T")
print("\n--- n-axis ray Nyquist: dn = 4 e B / h per LL at B_lo ---")
for B_lo in [2.0, 2.5, 3.0]:
    dn = 4 * B_lo / h_e * 1e-4 * 1e-12   # e/h in 1/(T m^2) -> per cm^2 -> e12
    print(f"B_lo {B_lo} T: ray spacing {dn:.3f}e12 -> >=2 pts/period over a 2.7e12 span needs N_n >= {int(np.ceil(2*2.7/dn))}, 3/period {int(np.ceil(3*2.7/dn))}")
