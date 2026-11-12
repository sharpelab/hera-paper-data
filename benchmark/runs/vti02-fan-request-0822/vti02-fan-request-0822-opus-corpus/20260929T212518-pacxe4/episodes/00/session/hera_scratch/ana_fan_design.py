"""Step-4 fan design: dual model overlay (mandatory) + landau-fan step-1 design numbers.

Design authority for tone positions is the forward model's F(n) table, not the bare
0.72/0.28 ratios: hera/models/tetralayer_fs_count (ABAB SWMcC + ABCA 8-band) and
hera/models/trilayer_fs_count (ML+BL, the adjacent-N overlay the investigation's Verify
makes binding for any two-tone pair).
"""
import sys
import importlib

MODELS = "/home/hera/measurement_env/hera/models"
sys.path.insert(0, f"{MODELS}/tetralayer_fs_count")
M4 = importlib.import_module("fs_count_b0")
del sys.modules["fs_count_b0"]
sys.path.insert(0, f"{MODELS}/trilayer_fs_count")
M3 = importlib.import_module("fs_count_b0")

FL = lambda n12: abs(n12) * 1e16 * cst.h / (4 * cst.e)   # noqa: E731  n12 in 1e12 cm^-2
SCALE = (7.11 + 22.26) / FL(3.20)        # global density rescale pinned on run 6's whole pair

# --- fan window and grid (nominal run-5 calibration units)
N_LO, N_HI = 2.00, 3.20
B_LO, B_MAX = 0.60, 10.0
N_B, N_n = 157, 44

print(f"global density scale pinned on run 6 = {SCALE:.3f}\n")
print("=== dual overlay across the fan window (the trajectory is the discriminator) ===")
print("nom n | true n | F_L,nom | ABAB(4L):  f_l    f_h  ratio  frac_l | 3L ML+BL: f_s    f_b  ratio")
for nn in np.linspace(N_LO, N_HI, 7):
    n_si = SCALE * nn * 1e16
    f4 = sorted(x[0] for x in M4.abab_fs(n_si)[1])
    f3 = sorted(x[0] for x in M3.aba_fs(n_si)[1])
    print(f"{nn:5.2f} | {SCALE * nn:6.2f} | {FL(nn):7.2f} | "
          f"{f4[0]:9.2f} {f4[-1]:6.2f} {f4[-1] / f4[0]:6.2f} {f4[0] / sum(f4):7.3f} | "
          f"{f3[0]:8.2f} {f3[-1]:6.2f} {f3[-1] / f3[0]:6.2f}")
print("  harmonic-ladder null hypothesis: ratio == 3.00 at EVERY density, frac_l == 0.250")
print("  ABCA null hypothesis:            one tone at F_L, no partner")

# --- landau-fan step 1: both-axis Nyquist, resolution, period count
span = 1 / B_LO - 1 / B_MAX
dinvB = span / (N_B - 1)
dF = 1 / span
dn = (N_HI - N_LO) / (N_n - 1)
dn_ray = 4 * (cst.e / cst.h) * B_LO * 1e-16
f_h_meas = 22.26

print(f"\n=== grid Nyquist + resolution (B_lo = {B_LO} T, B_max = {B_MAX} T) ===")
print(f"B axis  : 1/B span {span:.4f} 1/T, N_B = {N_B} -> d(1/B) = {dinvB:.5f}, "
      f"F_Nyq = {1 / (2 * dinvB):.1f} T")
print(f"          must clear F_L(n_max) = {FL(N_HI):.1f} T AND 2*f_heavy = {2 * f_h_meas:.1f} T "
      f"(2nd harmonic folding) -> {'OK' if 1 / (2 * dinvB) > 2 * f_h_meas else 'FAIL'}")
print(f"n axis  : ray spacing at B_lo = {dn_ray:.4f}e12; N_n = {N_n} -> dn = {dn:.4f}e12 "
      f"= {dn_ray / dn:.2f} pts/ray ({'OK' if dn_ray / dn >= 2 else 'UNDER the >=2 floor'})")
print(f"resolution: delta_F = {dF:.3f} T")
print("partner-tone period count over the record (>=5 is the binding case, at n_lo):")
for nn in (N_LO, 2.4, 2.8, N_HI):
    f_l = 1.15 * sorted(x[0] for x in M4.abab_fs(SCALE * nn * 1e16)[1])[0]   # model x measured bias
    print(f"  nominal n = {nn:.2f}: expect f_l ~ {f_l:5.2f} T -> {f_l * span:5.2f} periods")

inv_mid = 0.5 * (1 / B_LO + 1 / B_MAX)
print(f"\nF_L-tone origin (mandatory): B-window split at the 1/B midpoint B = {1 / inv_mid:.2f} T, "
      f"each half delta_F = {1 / (1 / B_LO - inv_mid):.2f} T")
print(f"  heavy {f_h_meas} vs F_L-tone 29.37 separated by {29.37 - f_h_meas:.2f} T "
      f"> 2*delta_F_half = {2 / (1 / B_LO - inv_mid):.2f} T -> resolvable in both halves")

B_vec = 1.0 / np.linspace(1 / B_LO, 1 / B_MAX, N_B)
print(f"\nB rows: {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, dB {np.abs(np.diff(B_vec)).min() * 1e3:.1f} mT "
      f"(low B) .. {np.abs(np.diff(B_vec)).max():.3f} T (high B); "
      f"total field movement {np.abs(np.diff(B_vec)).sum():.2f} T")
