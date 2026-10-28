import numpy as np
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

# --- calibration from cnp_fit.py (file_id 18, sr1 anchor) ---
c_tg = stack_capacitance([(15.6, 3)])
ratio = 1.3136                      # data-fitted c_bg/c_tg (sr1)
c_bg = ratio * c_tg
n_off = -0.225                      # 10^12 cm^-2
D_off = 0.0
TG = (-6.0, 7.0); BG = (-4.5, 4.5)  # validators
print(f"c_tg={c_tg:.4e} c_bg={c_bg:.4e} ratio={ratio} n_off={n_off} (1e12 cm^-2)")

# --- D envelope at validator corners ---
print("\nD envelope at validator corners (n,D):")
for vtg in TG:
    for vbg in BG:
        n, D = calc_nD(vtg, vbg, c_tg, c_bg, n_off, D_off)
        print(f"  Vtg={vtg:+.1f} Vbg={vbg:+.1f} -> n={n:+.3f}  D={D:+.4f} V/nm")

# --- design constant-D lines; clip by DROPPING out-of-range points ---
def inrange(vtg, vbg):
    return (TG[0] <= vtg) & (vtg <= TG[1]) & (BG[0] <= vbg) & (vbg <= BG[1])

n_req = np.linspace(-4.0, 4.0, 401)   # requested n sweep (1e12 cm^-2)
print("\nrealized n-window per constant-D line (clip-by-drop):")
print(f"{'D[V/nm]':>8} {'n_lo':>7} {'n_hi':>7} {'npts':>5}  notes")
for D0 in [-0.5, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.5]:
    vtg, vbg = calc_gate_voltages(n_req, np.full_like(n_req, D0), c_tg, c_bg, n_off, D_off)
    keep = inrange(vtg, vbg)
    if keep.sum() == 0:
        print(f"{D0:>8.2f} {'--':>7} {'--':>7} {0:>5}  EMPTY (outside box)")
        continue
    nk = n_req[keep]
    print(f"{D0:>8.2f} {nk.min():>7.2f} {nk.max():>7.2f} {keep.sum():>5}  "
          f"Vtg[{vtg[keep].min():+.2f},{vtg[keep].max():+.2f}] Vbg[{vbg[keep].min():+.2f},{vbg[keep].max():+.2f}]")

# n=0 (CNP) vs D line: how much D-range is reachable at the CNP?
print("\nCNP (n=0) vs D reachable range:")
D_scan = np.linspace(-1.0, 1.0, 401)
vtg, vbg = calc_gate_voltages(np.zeros_like(D_scan), D_scan, c_tg, c_bg, n_off, D_off)
keep = inrange(vtg, vbg)
print(f"  D in [{D_scan[keep].min():+.3f}, {D_scan[keep].max():+.3f}] V/nm at n=0 (within box)")
