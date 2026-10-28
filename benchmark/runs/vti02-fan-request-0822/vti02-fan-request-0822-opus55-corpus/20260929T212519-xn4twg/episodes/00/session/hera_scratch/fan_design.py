import sys, numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count"); import fs_count_b0 as m
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
N_HI, N_LO, N_N = 3.2, 2.0, 25
ns = np.linspace(N_HI, N_LO, N_N); dn = (N_HI - N_LO) / (N_N - 1)
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"n {N_HI}->{N_LO}, {N_N} pts, dn {dn:.4f}; Vtg {Vt.max():+.4f}..{Vt.min():+.4f}, Vbg {Vb.max():+.4f}..{Vb.min():+.4f}; step dVtg {abs(np.diff(Vt)).max()*1e3:.1f} mV dVbg {abs(np.diff(Vb)).max()*1e3:.1f} mV")
# B grid: 0.70-1.25 T at d(1/B)=~0.03 (light tone only alive), 1.25-10 T at 0.01
seg1 = np.linspace(1/0.70, 1/1.25, 22)[:-1]; seg2 = np.linspace(1/1.25, 1/10.0, 71)
invB = np.hstack((seg1, seg2)); B = np.round(1/invB, 4); B = np.minimum(B, 10.0)
print(f"B rows {len(B)}: {B[0]}->{B[-1]}; d(1/B) seg1 {np.diff(seg1).mean():.4f} seg2 {np.diff(seg2).mean():.4f}; max dB {np.diff(B).max():.3f} T; monotonic {np.all(np.diff(B)>0)}")
eh = 2.418e14  # e/h per T per m^2
# B-axis Nyquist
for lab, F, d in [("F_L(3.2) scale1", 33.1, 0.01), ("F_L region B (n+0.43)", 37.5, 0.01), ("light 7.5 T*1.13 (region B) seg1", 8.5, 0.0299), ("heavy/2f1 ~16 T seg1 (dead <1.25T)", 16.0, 0.0299)]:
    print(f"  B-Nyquist {lab}: {1/(F*d):.2f} pts/period")
# n-axis: per-tone period along n = B / (dF/dn)
for lab, dFdn, Bread in [("F_L-slope comps (29.9 T tone)", 10.34, 1.76), ("heavy (22.3 T)", 7.3, 1.40), ("light (7.5 T)", 3.1, 0.70), ("total ray spacing @ B_lo (recipe crude)", 10.34, 0.70), ("ray @ 3 T (Streda read)", 10.34, 3.0)]:
    per = Bread / dFdn
    print(f"  n-Nyquist {lab} @ {Bread} T: period {per:.3f}e12 -> {per/dn:.2f} pts")
# resolution
for lab, blo in [("heavy", 1.40), ("F_L tone", 1.76), ("light", 0.70)]:
    print(f"  dF {lab}: [{blo},10] {1/(1/blo-0.1):.2f} T ; [{blo},5.5] {1/(1/blo-1/5.5):.2f} T")
for n in [2.0, 2.2, 2.5, 2.8, 3.2]:
    ab = m.abab_fs(n*1e16)[1]; FL = 41.36*n/4
    for s in (0.9, 1.0):
        l, h = ab[0][0]*s, ab[1][0]*s
        print(f"  n={n}: s={s}: light {l:.2f} T -> periods [0.7,10] {l*(1/0.7-0.1):.1f}, [1.0,10] {l*0.9:.1f}; heavy {h:.1f} vs F_L {FL*s:.1f} (sep {FL*s-h:.1f} T); comb 3f1(n) {3*7.5*n/3.2:.1f}, f1 {7.5*n/3.2:.1f}")
# price
t_pt = 2.4 + 0.08 + 0.04
ramp = (B[-1] - B[0]) / (0.137/60); pos = B[0] / (0.137/60)
turn = len(B) * (3.09 + 1.0 + 3.0)
grid = len(B) * N_N * t_pt
tot = ramp + pos + turn + grid + 30
print(f"price: position {pos/60:.1f} min, traverse {ramp/60:.1f} min, turnaround {turn/60:.1f} min, grid {grid/60:.1f} min -> {tot/3600:.2f} h (+7% realism {tot*1.07/3600:.2f} h)")
# cumulative time to checkpoints
cum = pos + 30; tl = []
prevB = B[0]
for i, b in enumerate(B):
    cum += (b - prevB)/(0.137/60) + 7.09 + N_N*t_pt; prevB = b; tl.append(cum)
for bb in (0.75, 1.25, 2.5, 5.0, 10.0):
    k = np.searchsorted(B, bb - 1e-6); k = min(k, len(B)-1)
    print(f"  reach B={B[k]:.2f} (row {k+1}/{len(B)}) at +{tl[k]/60:.0f} min")
