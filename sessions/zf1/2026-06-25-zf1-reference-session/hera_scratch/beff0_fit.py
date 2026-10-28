"""Step 0 — stitch the two one-sided field-kill halves (runs 1,2) and fit B_eff0."""
import numpy as np
from hera.analysis import open_run

def load(i):
    g = open_run(f"data/{i}")
    B = g.col_at(g.col_indices('magnet_field')[0]) * 1e3   # mT
    R = (g.col_at(g.col_indices('sr830_3_X')[0]) / 100) / 1e-9  # 4T Rxx, Ohm
    return B, R, g

B1, R1, g1 = load(1)   # +5 -> 0
B2, R2, g2 = load(2)   # -5 -> 0
B = np.concatenate([B2, B1]); R = np.concatenate([R2, R1])
o = np.argsort(B); B, R = B[o], R[o]
print(f"stitched {len(B)} pts, B in [{B.min():.2f}, {B.max():.2f}] mT")
print(f"T(run1)={g1.col('T').mean()*1e3:.1f} mK  T(run2)={g2.col('T').mean()*1e3:.1f} mK")

# normal-state R (flanks, |B|>3.5 mT)
Rn = np.median(R[np.abs(B) > 3.5])
print(f"normal-state Rxx ~ {Rn:.1f} Ohm")

# Method 1: half-normal threshold-crossing midpoint (robust to flat bottom)
thr = 0.5 * Rn
def cross(Bs, Rs):
    # first crossing of thr going outward from min
    idx = np.where(Rs > thr)[0]
    return idx
# left flank: B<0 ascending |B|; find where R rises through thr on each side
left = B < 0; right = B > 0
def flank_cross(side_B, side_R, sign):
    # walk from |B|=0 outward, find interpolated B where R crosses thr
    order = np.argsort(sign*side_B)  # increasing |B|
    bb, rr = side_B[order], side_R[order]
    for k in range(1, len(rr)):
        if rr[k-1] < thr <= rr[k]:
            f = (thr - rr[k-1]) / (rr[k] - rr[k-1])
            return bb[k-1] + f*(bb[k]-bb[k-1])
    return np.nan
Bc_minus = flank_cross(B[left], R[left], -1)
Bc_plus  = flank_cross(B[right], R[right], +1)
B0_thr = 0.5*(Bc_minus + Bc_plus)
print(f"half-normal crossings: B-={Bc_minus:.3f}  B+={Bc_plus:.3f} mT")
print(f"  -> B_eff0 (midpoint) = {B0_thr:.3f} mT ; B_c half-width = {0.5*(Bc_plus-Bc_minus):.3f} mT")

# Method 2: parabola fit to the dip bottom (|B-B0_thr|<1.5 mT)
near = np.abs(B - B0_thr) < 1.5
c = np.polyfit(B[near], R[near], 2)
B0_par = -c[1]/(2*c[0])
print(f"parabola-bottom B_eff0 = {B0_par:.3f} mT  ({near.sum()} pts in fit)")
print(f"FINAL B_eff0 ~ {0.5*(B0_thr+B0_par):.3f} mT  (use {0.5*(B0_thr+B0_par):.4f}e-3 T)")
