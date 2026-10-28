import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN,TG_MAX,BG_MIN,BG_MAX = -0.3,1.0,-1.3,2.0
n_vec = np.round(np.arange(-1.20, 3.2001, 0.05), 4)
Vtg,Vbg = calc_gate_voltages(n_vec, np.zeros_like(n_vec), CAL["c_tg"],CAL["c_bg"],CAL["n_offset"],CAL["D_offset"])
print(f"n: {len(n_vec)} pts {n_vec[0]:+.2f}..{n_vec[-1]:+.2f}")
print(f"Vtg {Vtg[0]:+.4f}..{Vtg[-1]:+.4f} margins ({Vtg.min()-TG_MIN:+.4f},{TG_MAX-Vtg.max():+.4f})")
print(f"Vbg {Vbg[0]:+.4f}..{Vbg[-1]:+.4f} margins ({Vbg.min()-BG_MIN:+.4f},{BG_MAX-Vbg.max():+.4f})")
nr,Dr = calc_nD(Vtg,Vbg,CAL["c_tg"],CAL["c_bg"],CAL["n_offset"],CAL["D_offset"])
print(f"roundtrip max|dn| {np.abs(nr-n_vec).max():.2e}, max|D| {np.abs(Dr).max():.2e} V/nm")
print("edge columns match spots:", np.allclose([Vtg[0],Vbg[0]],[-0.2770,-0.4650],atol=2e-4), np.allclose([Vtg[-1],Vbg[-1]],[0.9836,1.1661],atol=2e-4))

B_lo = np.array([0.30,0.45,0.60,0.80,0.95,1.10])
B_hi = field_invB(1.2,10.0,71)
B_vec = np.unique(np.round(np.concatenate([B_lo,B_hi]),4))
print(f"\nB: {len(B_vec)} rows {B_vec[0]}..{B_vec[-1]}; monotonic {np.all(np.diff(B_vec)>0)}")
print("first 12:", np.round(B_vec[:12],3)); print("last 8:", np.round(B_vec[-8:],3))
d=np.diff(B_vec); print(f"dB min {d.min()*1e3:.1f} mT max {d.max()*1e3:.0f} mT; max row ramp {d.max()/0.137:.1f} min")
inv=1/B_hi; print(f"uniform block: d(1/B)={np.abs(np.diff(inv)).mean():.5f} -> F_Nyq {1/(2*np.abs(np.diff(inv)).mean()):.1f} T; dF {1/(1/1.2-1/10):.2f} T")
rows2=(B_vec<2).sum(); rows4=(B_vec<4).sum()
per=len(n_vec)*1.12+6.5
print(f"\nper-row {per:.0f}s; rows {len(B_vec)}; gates {len(B_vec)*per/3600:.2f} h; magnet {(B_vec[-1]-0)/0.137/60:.2f} h")
tot=len(B_vec)*per+(B_vec[-1]/0.137)*60
print(f"TOTAL {tot/3600:.2f} h (+10% -> {tot*1.1/3600:.2f} h = {int(tot*1.1//3600)}h{int((tot*1.1%3600)//60)}m)")
for Bc in (2.0,4.0):
    i=(B_vec<Bc).sum(); t=i*per+(Bc/0.137)*60
    print(f"  checkpoint B={Bc}: row {i}, t={t/3600:.2f} h; dF over [1.2,{Bc}] = {1/(1/1.2-1/Bc):.2f} T")
print("\nF_L: n=+3.20 ->", round(float(luttinger_frequency(3.20e16)),1), "T ; n=-1.20 ->", round(float(luttinger_frequency(1.20e16)),1),"T")
print("nu at B=10: n=+3.20 ->", round(3.20e16*6.626e-34/(1.602e-19*10),1))
