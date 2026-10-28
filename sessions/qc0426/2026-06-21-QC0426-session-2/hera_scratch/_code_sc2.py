import numpy as np
import time
import scipy.constants as cst

# ELECTRON side, n = +3.5e12 cm^-2, D = 0 (session calibration, run 1). Mirror of hole run 3.
VTG_T, VBG_T = +1.7337, +1.3243
n_target = 3.5e16
F_L = cst.h / (4 * cst.e) * n_target
B_LO, B_HI = 1.0, 7.95
dinvB = 1.0 / (3 * F_L)
N = int(np.ceil((1 / B_LO - 1 / B_HI) / dinvB)) + 1
Bvec = 1.0 / np.linspace(1 / B_LO, 1 / B_HI, N)   # ascending 1.0 -> 7.95 T (magnet already at 1.0)
print(f"F_L={F_L:.1f} T  N={N}  Bvec {Bvec[0]:.3f}..{Bvec[-1]:.3f} T  df={1/(1/B_LO-1/B_HI):.2f} T")

sr1.sensitivity(1e-4); sr2.sensitivity(1e-4); sr3.sensitivity(5e-5)

meas_config['comments'] = (f"sdh-spot-check ELECTRON n=+3.5e12 D=0 (Vtg={VTG_T},Vbg={VBG_T}); "
                           f"B {B_LO}->{B_HI}T uniform-1/B N={N} Nyquist/3 F_L={F_L:.1f}T; "
                           f"dwell2.5s; sr1/2=1e-4 sr3=5e-5; Si=0. Mirror of hole run3.")
for k, sr in [('sr0_sens', sr0), ('sr1_sens', sr1), ('sr2_sens', sr2), ('sr3_sens', sr3)]:
    meas_config[k] = sr.sensitivity()
meas_config['bias_voltage'] = sr1.amplitude(); meas_config['lockin_freq'] = sr1.frequency()
meas_config['sample_temperature:'] = heater.sample_temperature(); meas_config['Si (V)'] = k_si.volt()

print("T:", heater.sample_temperature(), "K  B:", magnet.field(), "T  Si:", k_si.volt(),
      "V  sens(1/2/3):", sr1.sensitivity(), sr2.sensitivity(), sr3.sensitivity())

# Set ELECTRON gates (from hole side -> sign flip), magnet already at ~1.0 T
dc205_volt(VTG_T); k_bg.volt(VBG_T); time.sleep(2)
magnet.field(B_LO)
print("start B =", magnet.field(), "T  Vtg,Vbg set:", VTG_T, VBG_T)

s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'ELECTRON n=+3.5e12 D=0 B{B_LO}-{B_HI}T invB N{N} dwell2.5 sens1e-4')
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(sr2.X).fp(sr2.P).fp(sr3.X).fp(sr3.P)
s.fp(k_bg.curr).fp(k_si.curr)
s.plot(magnet.field, sr1.X)
s.sweep(magnet.field, Bvec, delay=2.5)
print("electron spot check complete; B now", magnet.field(), "T")
