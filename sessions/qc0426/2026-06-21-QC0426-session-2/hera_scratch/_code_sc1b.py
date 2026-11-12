import numpy as np
import time
import scipy.constants as cst

# Same target as run 2 (HOLE, n=-3.5e12, D=0) — gates already there; clean-sens RE-RUN
VTG_T, VBG_T = -1.5597, -1.1914
n_target = 3.5e16
F_L = cst.h / (4 * cst.e) * n_target
B_HI, B_LO = 7.95, 1.0
dinvB = 1.0 / (3 * F_L)
N = int(np.ceil((1 / B_LO - 1 / B_HI) / dinvB)) + 1
Bvec = 1.0 / np.linspace(1 / B_HI, 1 / B_LO, N)   # descending 7.95 -> 1.0 T (ride home)
print(f"F_L={F_L:.1f} T  N={N}  Bvec {Bvec[0]:.3f}..{Bvec[-1]:.3f} T  df={1/(1/B_LO-1/B_HI):.2f} T")

# Corrected sensitivities for strong MR (run 2 clipped at 1e-5)
sr1.sensitivity(1e-4); sr2.sensitivity(1e-4); sr3.sensitivity(5e-5)

meas_config['comments'] = (f"sdh-spot-check HOLE n=-3.5e12 D=0 RERUN clean-sens (Vtg={VTG_T},Vbg={VBG_T}); "
                           f"B {B_HI}->{B_LO}T ride-home uniform-1/B N={N} Nyquist/3 F_L={F_L:.1f}T; "
                           f"dwell2.5s; sr1/2=1e-4 sr3=5e-5 (run2 clipped >4T at 1e-5); Si=0.")
for k, sr in [('sr0_sens', sr0), ('sr1_sens', sr1), ('sr2_sens', sr2), ('sr3_sens', sr3)]:
    meas_config[k] = sr.sensitivity()
meas_config['bias_voltage'] = sr1.amplitude(); meas_config['lockin_freq'] = sr1.frequency()
meas_config['sample_temperature:'] = heater.sample_temperature(); meas_config['Si (V)'] = k_si.volt()

print("T:", heater.sample_temperature(), "K  B:", magnet.field(), "T  Si:", k_si.volt(),
      "V  sens(1/2/3):", sr1.sensitivity(), sr2.sensitivity(), sr3.sensitivity())

# Re-assert gates (already at target), magnet already at ~8 T
dc205_volt(VTG_T); k_bg.volt(VBG_T); time.sleep(2)
magnet.field(B_HI)
print("start B =", magnet.field(), "T")

s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment(f'HOLE n=-3.5e12 D=0 RERUN B{B_HI}-{B_LO}T invB N{N} dwell2.5 sens1e-4')
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(sr2.X).fp(sr2.P).fp(sr3.X).fp(sr3.P)
s.fp(k_bg.curr).fp(k_si.curr)
s.plot(magnet.field, sr1.X)
s.sweep(magnet.field, Bvec, delay=2.5)
print("rerun complete; B now", magnet.field(), "T")
