import numpy as np
from scipy.ndimage import gaussian_filter1d
from sharpelab_nb.gates import stack_capacitance, calc_nD

d = np.load('hera_scratch/map1_reformed.npz')
V_tg, V_bg, R4, R2 = d['V_tg'], d['V_bg'], d['R4'], d['R2']
NT, NB = R4.shape

# --- CNP ridge from 4T (sr3), per TG row, with robust linear fit ---
Vbg_cnp = np.full(NT, np.nan); strength = np.zeros(NT)
for i in range(NT):
    prof = gaussian_filter1d(np.clip(R4[i], 1, None), 1.0)
    j = int(np.argmax(prof))
    Vbg_cnp[i] = V_bg[j]
    strength[i] = prof[j] / (np.median(prof) + 1e-9)   # peak prominence

# keep rows with a real peak not at the BG edge
ok = (strength > 3) & (Vbg_cnp > V_bg[1]) & (Vbg_cnp < V_bg[-2])
# iterative 2-sigma rejection on V_bg_cnp = m*V_tg + b
idx = np.where(ok)[0]
for _ in range(5):
    m, b = np.polyfit(V_tg[idx], Vbg_cnp[idx], 1)
    res = Vbg_cnp[idx] - (m*V_tg[idx] + b)
    keep = np.abs(res) < 2.5*np.std(res)
    if keep.all(): break
    idx = idx[keep]
rms = np.std(Vbg_cnp[idx] - (m*V_tg[idx]+b))
ratio = -1.0/m
print(f"CNP fit (4T): V_bg_cnp = {m:.4f}*V_tg + {b:+.4f}   rms {rms:.3f} V   ({len(idx)}/{NT} rows)")
print(f"CAP RATIO c_bg/c_tg = -1/m = {ratio:.3f}   (prior 1.18)")

# --- capacitances: anchor c_tg at geometry, set c_bg from fitted ratio ---
c_tg = stack_capacitance([(23.6, 3.0)])
c_bg_geo = stack_capacitance([(20.0, 3.0)])
c_bg = ratio * c_tg
print(f"c_tg(geo)={c_tg:.4e}  c_bg(geo)={c_bg_geo:.4e}  c_bg(fit)={c_bg:.4e} F/m^2")

# n_offset so CNP -> n=0 (use line point at V_tg=0 -> V_bg=b)
n_at_cnp, _ = calc_nD(0.0, b, c_tg, c_bg)
n_off = -n_at_cnp
n0, D0 = calc_nD(V_tg[:,None]*np.ones((1,NB)), np.ones((NT,1))*V_bg[None,:], c_tg, c_bg, n_offset=n_off)
print(f"n units sample: n range [{n0.min():.3e}, {n0.max():.3e}]   D range [{D0.min():.3f}, {D0.max():.3f}]")
# convert n to 1e11 cm^-2 for readout if SI m^-2
n_cm = n0/1e4/1e11   # m^-2 -> cm^-2 -> 1e11 cm^-2  (if n0 in m^-2)
print(f"n in 1e11 cm^-2: [{n_cm.min():.2f}, {n_cm.max():.2f}]")

# --- candidate region: n in [-6,-4] 1e11/cm2, |D|>=0.5 ; report 4T R there ---
cand = (n_cm <= -4) & (n_cm >= -6) & (np.abs(D0) >= 0.5)
print(f"\ncandidate band cells in window: {cand.sum()}")
if cand.any():
    it, ib = np.where(cand)
    print(f"  V_tg [{V_tg[it].min():+.2f},{V_tg[it].max():+.2f}]  V_bg [{V_bg[ib].min():+.2f},{V_bg[ib].max():+.2f}]")
    print(f"  D sign(s): {np.unique(np.sign(D0[cand]))}   |D| up to {np.abs(D0[cand]).max():.2f}")
    print(f"  4T R in band: min {R4[cand].min():.1f}  med {np.median(R4[cand]):.1f}  Ohm")
# both hole-side large-|D| corners (D sign convention unsure)
for sgn,lab in ((-1,'D<0'),(+1,'D>0')):
    msk = (n_cm<=-3)&(n_cm>=-7)&(np.sign(D0)==sgn)&(np.abs(D0)>=0.5)
    if msk.any():
        print(f"  hole-side {lab}: {msk.sum()} cells, |D|<= {np.abs(D0[msk]).max():.2f}, 4T R min {R4[msk].min():.1f}")

np.savez('hera_scratch/map1_nD.npz', V_tg=V_tg, V_bg=V_bg, R4=R4, n=n0, D=D0,
         n_cm=n_cm, m=m, b=b, ratio=ratio, c_tg=c_tg, c_bg=c_bg, n_off=n_off,
         cnp_idx=idx, Vbg_cnp=Vbg_cnp)
print("saved hera_scratch/map1_nD.npz")
