import numpy as np, inspect
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB, luttinger_frequency
print(inspect.signature(calc_gate_voltages)); print(inspect.signature(calc_nD))
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG_MIN,TG_MAX,BG_MIN,BG_MAX = -0.3,1.0,-1.3,2.0

# --- fast axis: n along D = 0 ---
for lo,hi,step in [(-1.10,3.35,0.05)]:
    ns = np.round(np.arange(lo,hi+1e-9,step),4)
    Vt,Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"],CAL["c_bg"],CAL["n_offset"],CAL["D_offset"])
    ok = (Vt>=TG_MIN)&(Vt<=TG_MAX)&(Vb>=BG_MIN)&(Vb<=BG_MAX)
    print(f"n {lo}..{hi} step {step}: {len(ns)} pts, inside={ok.sum()}")
    print(f"  Vtg {Vt.min():+.4f}..{Vt.max():+.4f} (lim {TG_MIN},{TG_MAX}); Vbg {Vb.min():+.4f}..{Vb.max():+.4f} (lim {BG_MIN},{BG_MAX})")
    print(f"  margin: TG lo {Vt.min()-TG_MIN:+.4f}, TG hi {TG_MAX-Vt.max():+.4f}; BG lo {Vb.min()-BG_MIN:+.4f}, BG hi {BG_MAX-Vb.max():+.4f}")
    print(f"  dVtg/dn = {(Vt[-1]-Vt[0])/(ns[-1]-ns[0]):.4f} V per 1e12 ; step dVtg = {np.diff(Vt)[0]*1e3:.1f} mV, dVbg = {np.diff(Vb)[0]*1e3:.1f} mV")
    span_tg, span_bg = Vt.max()-Vt.min(), Vb.max()-Vb.min()
    print(f"  flyback: TG {span_tg:.3f} V /5mV*6ms = {span_tg/0.005*0.006:.2f} s ; BG {span_bg:.3f} V = {span_bg/0.005*0.006:.2f} s")

# --- slow axis: B uniform in 1/B ---
for N in (61,71,81):
    B = field_invB(1.2,10.0,N)
    d = np.diff(1/B)
    print(f"\nN={N}: B {B[0]:.3f}..{B[-1]:.3f}, d(1/B)={-d.mean():.5f} -> F_Nyq={1/(2*abs(d.mean())):.1f} T, dF={1/(1/B[0]-1/B[-1]):.2f} T")
    dB = np.diff(B); print(f"  dB: min {dB.min()*1e3:.1f} mT, max {dB.max()*1e3:.0f} mT; rows<2T {(B<2).sum()}, <4T {(B<4).sum()}, >5T {(B>5).sum()}")
    print(f"  max row ramp {dB.max()/0.137:.1f} min; total traverse {(B[-1]-B[0])/0.137:.0f} min")

# --- price ---
NF=90
for N in (61,71,81):
    B=field_invB(1.2,10.0,N)
    row_pts = NF*1.085
    turn = 3.0 + 1.51 + 1.96
    gates = N*(row_pts+turn)
    mag = (B[-1]-B[0])/0.137*60 + 1.2/0.137*60
    tot = gates+mag
    print(f"N={N}: gates {gates/3600:.2f} h + magnet {mag/3600:.2f} h = {tot/3600:.2f} h  (+10% -> {tot*1.1/3600:.2f} h)")
    # partial at 4 T
    i=(B<4).sum(); 
    print(f"   by B=4T: {i} rows, {(i*(row_pts+turn) + (4-1.2)/0.137*60 + 1.2/0.137*60)/3600:.2f} h")
# nu coverage
for Bv in (1.2,2,4,10):
    print(f"B={Bv}: e B/h = {1.602e-19*Bv/6.626e-34*1e-16:.4f} e12 per nu ; nu at n=3.35e12 -> {3.35e16*6.626e-34/(1.602e-19*Bv):.1f}; 4-fold period in n = {4*1.602e-19*Bv/6.626e-34*1e-16:.3f} e12 ({4*1.602e-19*Bv/6.626e-34*1e-16/0.05:.1f} pts)")
print("F_L at n=3.35e12:", luttinger_frequency(3.35e16), "T ; at 1e12:", luttinger_frequency(1e16))
