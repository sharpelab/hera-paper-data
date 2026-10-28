import numpy as np
EPS0=8.8541878128e-12; E=1.602176634e-19
kap=3.0; t_tg=23.6e-9; t_bg=20e-9
c_tg=EPS0*kap/t_tg; c_bg=EPS0*kap/t_bg
b_int=0.0259                       # CNP BG-intercept at TG=0 (fitted)
n_offset=-c_bg*b_int/E             # m^-2
TG_MIN,TG_MAX=-7.0,6.0; BG_MIN,BG_MAX=-4.0,4.2
print(f"n_offset={n_offset:.3e} m^-2 ({n_offset*1e-4:.2e} cm^-2)")

def gates_for(n_cm, D_vnm):
    n=np.asarray(n_cm)*1e4; D=D_vnm*1e9        # to SI
    a=(n-n_offset)*E
    bb=D*2*EPS0
    return (a+bb)/(2*c_tg), (a-bb)/(2*c_bg)    # Vtg, Vbg

for D in (-0.45,-0.60,-0.75):
    n_req=np.linspace(0.5e11,-8e11,200)        # cm^-2
    Vtg,Vbg=gates_for(n_req,D)
    ok=(Vtg>=TG_MIN)&(Vtg<=TG_MAX)&(Vbg>=BG_MIN)&(Vbg<=BG_MAX)
    if ok.sum()==0: print(f"D={D:+.2f}: none"); continue
    nn=n_req[ok]
    print(f"D={D:+.2f} V/nm: realized n [{nn.max()/1e11:+.2f},{nn.min()/1e11:+.2f}]e11  "
          f"{ok.sum()}/200 pts  Vtg[{Vtg[ok].min():.2f},{Vtg[ok].max():.2f}] "
          f"Vbg[{Vbg[ok].min():.2f},{Vbg[ok].max():.2f}]")
