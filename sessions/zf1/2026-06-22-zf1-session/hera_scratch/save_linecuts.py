import numpy as np
from hera.analysis import GateCalibration
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
def nD(vt,vb): return cal.density(vt,vb)/1e15, cal.displacement_field(vt,vb)/1e9
n00,D00=nD(0,0); n10,D10=nD(1,0); n01,D01=nD(0,1)
A=np.array([[n10-n00,n01-n00],[D10-D00,D01-D00]]); Ainv=np.linalg.inv(A)
def gates(n11,Dnm): return Ainv@np.array([n11-n00,Dnm-D00])

TGL=(-7.0,6.0); BGL=(-4.0,4.2)
Ds=[-0.35,-0.45,-0.55,-0.65]
n_vec=np.arange(-1.5,-9.0001,-0.075)
VT=[]; VB=[]; DL=[]; NL=[]
for D0 in Ds:
    vt=np.array([gates(n,D0)[0] for n in n_vec]); vb=np.array([gates(n,D0)[1] for n in n_vec])
    inb=(vt>=TGL[0])&(vt<=TGL[1])&(vb>=BGL[0])&(vb<=BGL[1])      # drop out-of-box (clip-by-dropping)
    VT.append(vt[inb]); VB.append(vb[inb]); DL.append(np.full(inb.sum(),D0)); NL.append(n_vec[inb])
vtg_vec=np.concatenate(VT); vbg_vec=np.concatenate(VB)
D_lbl=np.concatenate(DL); n_lbl=np.concatenate(NL)
np.savez("hera_scratch/linecut_vectors.npz", vtg=vtg_vec, vbg=vbg_vec, D=D_lbl, n=n_lbl, Ds=np.array(Ds))
print(f"saved {len(vtg_vec)} pts across {len(Ds)} D-lines: D={Ds}")
print(f"Vtg span [{vtg_vec.min():+.3f},{vtg_vec.max():+.3f}]  Vbg span [{vbg_vec.min():+.3f},{vbg_vec.max():+.3f}]")
for D0 in Ds:
    m=D_lbl==D0; print(f"  D={D0:+.2f}: {m.sum()} pts, n[{n_lbl[m].min():+.2f},{n_lbl[m].max():+.2f}]e11")
