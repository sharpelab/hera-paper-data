import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG=(-0.3,1.0); BG=(-1.3,2.0)
NFAST=141
n_vec = np.linspace(-1.20, 3.20, NFAST)
Vtg, Vbg = calc_gate_voltages(n_vec, 0.0, **CAL)
print(f'n {n_vec[0]:+.3f} .. {n_vec[-1]:+.3f} e12, dn = {np.diff(n_vec)[0]*1e12:.3e} cm^-2')
print(f'Vtg {Vtg[0]:+.5f} .. {Vtg[-1]:+.5f}  (limits {TG}; margin lo {Vtg.min()-TG[0]*1:+.4f}, hi {TG[1]-Vtg.max():+.4f} V)')
print(f'Vbg {Vbg[0]:+.5f} .. {Vbg[-1]:+.5f}  (limits {BG}; margin lo {Vbg.min()-BG[0]:+.4f}, hi {BG[1]-Vbg.max():+.4f} V)')
print(f'step dVtg {np.diff(Vtg)[0]*1e3:.2f} mV ({np.ceil(np.diff(Vtg)[0]/0.005):.0f} keithley writes), dVbg {np.diff(Vbg)[0]*1e3:.2f} mV ({np.ceil(np.diff(Vbg)[0]/0.005):.0f} writes)')
nn, DD = calc_nD(Vtg, Vbg, **CAL); print(f'roundtrip D: {DD.min():+.2e} .. {DD.max():+.2e} V/nm (must be ~0)')
print(f'endpoints match spot checks: run6 (+0.9836,+1.1661) vs {Vtg[-1]:+.4f},{Vbg[-1]:+.4f}; run7 (-0.2770,-0.4650) vs {Vtg[0]:+.4f},{Vbg[0]:+.4f}')

B_vec = np.round(np.arange(1.0, 10.0001, 0.1), 4)
NROW=len(B_vec)
FAST_DELAY=0.7; OVH=0.13
fly = (abs(Vtg[-1]-Vtg[0])/0.005 + abs(Vbg[-1]-Vbg[0])/0.005)*0.006
rowmeas = NFAST*(FAST_DELAY+OVH)
ramp = 0.1/0.137*60
row = rowmeas + fly + 3 + 3 + ramp
print(f'\nrows {NROW} ({B_vec[0]}..{B_vec[-1]} T, 0.1 T); pts {NROW*NFAST}')
print(f'  per-row: meas {rowmeas:.0f}s + flyback {fly:.1f}s + slow_delay 3 + magnet settle 3 + ramp {ramp:.0f}s = {row:.0f}s')
print(f'  total {NROW*row/3600:.2f} h  (+10% realism -> {NROW*row/3600*1.1:.2f} h)')
print(f'  ramp floor alone {(B_vec[-1]-B_vec[0])/0.137/60:.2f} h')
# resolution checks
h,e=6.62607015e-34,1.602176634e-19
for B in (1.0,2.0,4.0,7.0,10.0):
    dn_nu = e*B/h*1e-4    # cm^-2 per filling factor
    print(f'  B={B:4.1f} T: 1 nu = {dn_nu:.3e} cm^-2 = {dn_nu/(np.diff(n_vec)[0]*1e12):5.2f} fast pts; '
          f'nu span over map = {(n_vec[-1]-n_vec[0])*1e12/dn_nu:6.1f}; nu(n=+3.2e12) = {3.2e12/dn_nu:6.1f}')
