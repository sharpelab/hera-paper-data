import numpy as np
import time
import scipy.constants as cst

# Target: HOLE side, n = -3.5e12 cm^-2, D = 0 (session calibration, run 1)
VTG_T, VBG_T = -1.5597, -1.1914     # gates_for(-3.5e12, 0); n, D verified exact
n_target = 3.5e16                    # m^-2
F_L = cst.h / (4 * cst.e) * n_target # g=4 Luttinger freq (T)
B_LO, B_HI = 0.20, 7.95
dinvB = 1.0 / (3 * F_L)              # Nyquist/3 on F_L
N = int(np.ceil((1 / B_LO - 1 / B_HI) / dinvB)) + 1
Bvec = 1.0 / np.linspace(1 / B_LO, 1 / B_HI, N)   # uniform in 1/B, 0.20 -> 7.95 T
print(f"F_L={F_L:.1f} T  d(1/B)={dinvB:.2e}  N={N}  Bvec {Bvec[0]:.3f}..{Bvec[-1]:.3f} T")

# Lock-in sensitivities for high-|n| metallic SdH (NOT touching tau/filter_slope)
sr1.sensitivity(1e-5); sr2.sensitivity(1e-5); sr3.sensitivity(5e-5)

meas_config['comments'] = (f"sdh-spot-check HOLE n=-3.5e12 D=0 (Vtg={VTG_T},Vbg={VBG_T}); "
                           f"B {B_LO}->{B_HI}T uniform-1/B N={N} (Nyquist/3 F_L={F_L:.1f}T); "
                           f"dwell 2.5s (8tau@24dB); sr1/2=1e-5 sr3=5e-5; Si=0.")
for k, sr in [('sr0_sens', sr0), ('sr1_sens', sr1), ('sr2_sens', sr2), ('sr3_sens', sr3)]:
    meas_config[k] = sr.sensitivity()
meas_config['bias_voltage'] = sr1.amplitude(); meas_config['lockin_freq'] = sr1.frequency()
meas_config['sample_temperature:'] = heater.sample_temperature(); meas_config['Si (V)'] = k_si.volt()

# Preflight
print("T:", heater.sample_temperature(), "K  B:", magnet.field(), "T  Si:", k_si.volt(),
      "V  drive:", sr1.amplitude(), "V  sens(1/2/3):", sr1.sensitivity(), sr2.sensitivity(), sr3.sensitivity())

# Ramp gates to (n, D=0), then magnet to B_lo (blocks until reached)
dc205_volt(VTG_T); k_bg.volt(VBG_T); time.sleep(3)
magnet.field(B_LO)
print("at start B =", magnet.field(), "T")

s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'HOLE n=-3.5e12 D=0 B{B_LO}-{B_HI}T invB N{N} dwell2.5')
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(sr2.X).fp(sr2.P).fp(sr3.X).fp(sr3.P)
s.fp(k_bg.curr).fp(k_si.curr)
s.plot(magnet.field, sr1.X)
s.sweep(magnet.field, Bvec, delay=2.5)
print("spot check complete; B now", magnet.field(), "T")
