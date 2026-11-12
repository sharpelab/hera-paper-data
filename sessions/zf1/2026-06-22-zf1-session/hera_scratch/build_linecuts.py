import numpy as np
from hera.analysis import GateCalibration
cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)

# Build the linear inverse (n,D)->(Vtg,Vbg) from the confirmed calibration.
# n,D are affine in gates: evaluate at 3 points to get the 2x2 + offset.
def nD(vt, vb):
    return cal.density(vt, vb)/1e15, cal.displacement_field(vt, vb)/1e9   # 1e11 cm^-2, V/nm
n00,D00 = nD(0,0); n10,D10 = nD(1,0); n01,D01 = nD(0,1)
A = np.array([[n10-n00, n01-n00],[D10-D00, D01-D00]])   # d(n,D)/d(Vtg,Vbg)
Ainv = np.linalg.inv(A)
def gates(n11, Dnm):                                      # (n in 1e11, D in V/nm) -> Vtg,Vbg
    rhs = np.array([n11-n00, Dnm-D00])
    return Ainv @ rhs

TGL=(-7.0,6.0); BGL=(-4.0,4.2)
Ds = [-0.35,-0.45,-0.55,-0.65]
n_vec = np.arange(-1.5, -9.0001, -0.075)                 # 101 pts, fine (arc ~0.5e11)
print(f"n: {n_vec[0]:+.2f} -> {n_vec[-1]:+.2f} e11, {len(n_vec)} pts, step {abs(n_vec[1]-n_vec[0]):.3f}e11")
print("D-line in-box coverage:")
all_in = True
for D0 in Ds:
    vt = np.array([gates(n, D0)[0] for n in n_vec])
    vb = np.array([gates(n, D0)[1] for n in n_vec])
    inb = (vt>=TGL[0])&(vt<=TGL[1])&(vb>=BGL[0])&(vb<=BGL[1])
    print(f"  D={D0:+.2f}: Vtg[{vt.min():+.2f},{vt.max():+.2f}] Vbg[{vb.min():+.2f},{vb.max():+.2f}]  in-box {inb.sum()}/{len(vt)}")
    if inb.sum()<len(vt): all_in=False
print("ALL in-box" if all_in else "SOME OUT OF BOX -> trim n-range")
# roundtrip check
vt,vb = gates(-5.0,-0.5); nb,Db = nD(vt,vb)
print(f"roundtrip (n=-5,D=-0.5)->Vtg={vt:+.3f} Vbg={vb:+.3f}->n={nb:+.3f} D={Db:+.3f}")
