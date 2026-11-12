import numpy as np, pickle
from hera.analysis import GateCalibration
import scipy.constants as cst
c=pickle.load(open("hera_scratch/calib.pkl","rb"))
cal=GateCalibration.from_thicknesses(c['t_tg'],c['t_bg_eff'],0.0,n_offset=c['n_offset'],D_offset=c['D_offset'])
ratio=c['ratio']; vtgD0,bgD0=c['vtg_D0'],c['bg_D0']
h,e=cst.h,cst.e
def gates_for_n(n_cm2):  # on D=0 line: V_tg = vtgD0 + ratio*(V_bg-bgD0)
    # density linear in V_bg along D0; solve
    vb=np.linspace(-4.5,4.5,9001); vt=vtgD0+ratio*(vb-bgD0)
    inb=(vt>=-6)&(vt<=7)
    nn=cal.density(vt,vb)/1e16  # cm^-2 e0... actually m^-2/1e16 = 1e12 cm^-2 units? check
    # cal.density returns m^-2; /1e4 -> cm^-2 ; target n_cm2 in 1e12 cm^-2
    n_cm = cal.density(vt,vb)/1e4
    k=np.argmin(np.abs(n_cm - n_cm2*1e12))
    return vt[k],vb[k],n_cm[k],cal.displacement_field(vt[k],vb[k]), inb[k]
print("F_L = (h/4e)*n ; Nyquist dB to resolve down to B_lo (>=2-3 samp/period):")
for ncm in [-8,-10,-12,8,10,12]:
    vt,vb,n,D,ok=gates_for_n(ncm)
    F=h*abs(n)*1e4/(4*e)   # n in cm^-2 -> m^-2 (*1e4); F in Tesla
    # dB to get 3 samples/period at B_lo
    for B_lo in [1.2,1.5,2.0]:
        dB=B_lo**2/(3*F)
    dB_15=1.5**2/(3*F)
    print(f"  n={ncm:+d}e12: V_tg={vt:+.3f} V_bg={vb:+.3f} (in-range {ok})  n_meas={n/1e12:+.2f}e12  D={D:.1e}  F_L={F:.0f} T  dB@B_lo1.5={dB_15*1e3:.1f} mT")
# pricing a spot check: time ~ B_max/0.137[min] + N*(3s magnet dwell + delay)
print("\nspot-check pricing (B_max=6T, 3s magnet dwell/pt + 0.5s delay):")
for dB in [0.010,0.0125,0.015]:
    N=int(6/dB)+1
    t=6/0.137 + N*(3+0.5)/60
    print(f"  dB={dB*1e3:.1f} mT  N={N}  ~{t:.0f} min")
