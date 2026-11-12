import numpy as np
from hera.analysis import GateCalibration
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
def nD(vt,vb): return cal.density(vt,vb)/1e15, cal.displacement_field(vt,vb)/1e9
n00,D00=nD(0,0); n10,D10=nD(1,0); n01,D01=nD(0,1)
A=np.array([[n10-n00,n01-n00],[D10-D00,D01-D00]]); Ainv=np.linalg.inv(A)
def gates(n11,Dnm): return Ainv@np.array([n11-n00,Dnm-D00])
TGL=(-7.0,6.0); BGL=(-4.0,4.2)

VT=[];VB=[];SEG=[];DL=[];NL=[]
# constant-D linecuts (in-box accessible D values bracketing the dip)
Ds=[-0.55,-0.60,-0.65]
n_vec=np.arange(-3.7,-6.2001,-0.05)
for D0 in Ds:
    vt=np.array([gates(n,D0)[0] for n in n_vec]); vb=np.array([gates(n,D0)[1] for n in n_vec])
    inb=(vt>=TGL[0])&(vt<=TGL[1])&(vb>=BGL[0])&(vb<=BGL[1])
    VT.append(vt[inb]); VB.append(vb[inb]); SEG.append([f"D={D0:+.2f}"]*inb.sum())
    DL.append(np.full(inb.sum(),D0)); NL.append(n_vec[inb])
    print(f"  D={D0:+.2f}: {inb.sum()} pts, n[{n_vec[inb].min():+.2f},{n_vec[inb].max():+.2f}]")
# edge sweep: BG pinned at +4.198 (just inside cap), TG swept over the candidate window
vt_e=np.arange(-4.0,-6.0001,-0.04); vb_e=np.full_like(vt_e,4.198)
ne,De=nD(vt_e,vb_e)
VT.append(vt_e); VB.append(vb_e); SEG.append(["edge"]*len(vt_e)); DL.append(De/1e9 if False else De); NL.append(ne)
print(f"  edge BG=+4.198: {len(vt_e)} pts, n[{(ne/1e15).min():+.2f},{(ne/1e15).max():+.2f}], D[{(De/1e9).min():+.3f},{(De/1e9).max():+.3f}]")
vtg=np.concatenate(VT); vbg=np.concatenate(VB); seg=np.concatenate(SEG)
np.savez("hera_scratch/confirm_vectors.npz", vtg=vtg, vbg=vbg, seg=seg)
print(f"saved {len(vtg)} pts; Vtg[{vtg.min():+.2f},{vtg.max():+.2f}] Vbg[{vbg.min():+.3f},{vbg.max():+.3f}]")
