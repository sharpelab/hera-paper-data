import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG=(-0.3,1.0); BG=(-1.3,2.0)
ns=np.linspace(-1.6,3.6,5201)
vt,vb=calc_gate_voltages(ns,np.zeros_like(ns),CAL["c_tg"],CAL["c_bg"],CAL["n_offset"],CAL["D_offset"])
ok=(vt>=TG[0])&(vt<=TG[1])&(vb>=BG[0])&(vb<=BG[1])
print("D=0 window n:",ns[ok].min(),ns[ok].max())
for n_lo,n_hi,dn in [(-1.2,3.25,0.045),(-1.2,3.25,0.05)]:
    N=int(round((n_hi-n_lo)/dn))+1; n=np.linspace(n_lo,n_hi,N)
    t,b=calc_gate_voltages(n,np.zeros_like(n),CAL["c_tg"],CAL["c_bg"],CAL["n_offset"],CAL["D_offset"])
    print(f"n {n_lo}..{n_hi} N={N} dn={n[1]-n[0]:.4f}: Vtg {t[0]:+.4f}..{t[-1]:+.4f}, Vbg {b[0]:+.4f}..{b[-1]:+.4f}, dVtg {abs(t[1]-t[0])*1e3:.1f} mV dVbg {abs(b[1]-b[0])*1e3:.1f} mV")
h,e=4.135667696e-15,1
print("F_L(3.25e12)=",3.25e16*h/4,"T  F_L(-1.2)=",1.2e16*h/4)
# B grid: 1/B-uniform 0.6->3 T at d(1/B)=0.0125, then uniform 0.1 T 3->9 T
for blo,bmid,bhi,dinv,dB in [(0.6,3.0,9.0,0.0125,0.1),(0.7,3.0,9.0,0.0125,0.1),(0.6,3.0,8.0,0.0125,0.1),(0.6,3.0,9.0,0.0125,0.125)]:
    nA=int(round((1/blo-1/bmid)/dinv))+1
    BA=field_invB(blo,bmid,nA)
    BB=np.round(np.arange(bmid+dB,bhi+1e-9,dB),4)
    Bv=np.hstack((BA,BB))
    for Nf in (91,99):
        per_pt=1.13; flyback=3.6; settle=3.0; sd=3.0
        ramp=(Bv[-1]-0.0)/0.137*60
        rows=len(Bv)
        t=rows*(Nf*per_pt+flyback+settle+sd+1.0)+ramp
        print(f"B {blo}->{bmid} invB({nA}, d={ (1/blo-1/bmid)/(nA-1):.4f}) + {bmid}->{bhi} @{dB} ({len(BB)}) = {rows} rows; Nf={Nf}: {t/3600:.2f} h (ramp {ramp/60:.0f} min); max dB in A {np.diff(BA).max():.3f}")
