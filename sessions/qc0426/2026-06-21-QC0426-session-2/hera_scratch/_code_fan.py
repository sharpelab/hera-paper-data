import numpy as np
import time
import scipy.constants as cst

# ELECTRON-side D=0 Landau fan (clean SdH side, run 4). FS-count fan: per-column SdH FFT.
# n-line gates from session calibration (run 1), gates_for(n, D=0), computed offline.
Vtgs = np.array([0.3222, 0.3584, 0.3946, 0.4308, 0.467, 0.5032, 0.5394, 0.5756, 0.6118,
                 0.6479, 0.6841, 0.7203, 0.7565, 0.7927, 0.8289, 0.8651, 0.9013, 0.9375,
                 0.9737, 1.0099, 1.046, 1.0822, 1.1184, 1.1546, 1.1908, 1.227, 1.2632,
                 1.2994, 1.3356, 1.3718, 1.4079, 1.4441, 1.4803, 1.5165, 1.5527, 1.5889,
                 1.6251, 1.6613, 1.6975, 1.7337])
Vbgs = np.array([0.2462, 0.2738, 0.3014, 0.3291, 0.3567, 0.3844, 0.412, 0.4397, 0.4673,
                 0.495, 0.5226, 0.5502, 0.5779, 0.6055, 0.6332, 0.6608, 0.6885, 0.7161,
                 0.7438, 0.7714, 0.7991, 0.8267, 0.8543, 0.882, 0.9096, 0.9373, 0.9649,
                 0.9926, 1.0202, 1.0479, 1.0755, 1.1032, 1.1308, 1.1584, 1.1861, 1.2137,
                 1.2414, 1.269, 1.2967, 1.3243])  # n = 0.5..3.5e12 cm^-2, D=0
n_vec = np.linspace(0.5e16, 3.5e16, 40)

F_Lmax = cst.h / (4 * cst.e) * 3.5e16          # 36.2 T (highest-n column sets Nyquist)
dinvB = 1.0 / (3 * F_Lmax)
NB = int(np.ceil((1 / 1.0 - 1 / 7.95) / dinvB)) + 1
Bvec = 1.0 / np.linspace(1 / 7.95, 1 / 1.0, NB)  # descending 7.95 -> 1.0 T (ride home from run 4)
print(f"fan grid {len(Vtgs)} n x {NB} B = {len(Vtgs)*NB} pts; F_Lmax={F_Lmax:.1f}T; B {Bvec[0]:.2f}->{Bvec[-1]:.2f}T")

# clean metallic sensitivities (no clip at ~kohm high-field MR)
sr1.sensitivity(1e-4); sr2.sensitivity(1e-4); sr3.sensitivity(5e-5)

meas_config['comments'] = ("landau-fan-vti ELECTRON D=0 FS-count: n[0.5-3.5]e12 (40 fast), "
                           "B[7.95-1.0]T uniform-1/B (96 slow, Nyquist/3 F_L=36T); dwell fast2.5 "
                           "slow2; sr1/2=1e-4 sr3=5e-5; Si=0. Side=electron (cleaner SdH run4; "
                           "hole resolution-limited run3). Per-column SdH FFT -> F(n) vs F_L.")
for k, sr in [('sr0_sens', sr0), ('sr1_sens', sr1), ('sr2_sens', sr2), ('sr3_sens', sr3)]:
    meas_config[k] = sr.sensitivity()
meas_config['bias_voltage'] = sr1.amplitude(); meas_config['lockin_freq'] = sr1.frequency()
meas_config['sample_temperature:'] = heater.sample_temperature(); meas_config['Si (V)'] = k_si.volt()

print("T:", heater.sample_temperature(), "K  B:", magnet.field(), "T  Si:", k_si.volt(),
      "V  sens:", sr1.sensitivity(), sr2.sensitivity(), sr3.sensitivity())

# Start: gates to n-line start, magnet to B start (7.95, already there from run 4)
dc205_volt(Vtgs[0]); k_bg.volt(Vbgs[0]); time.sleep(2)
magnet.field(Bvec[0])
print("start B =", magnet.field(), "T  Vtg0,Vbg0 =", Vtgs[0], Vbgs[0])

s = async_station(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment(f'ELECTRON D=0 n[0.5-3.5]e12x40 B[7.95-1.0]Tx{NB} invB dwell f2.5 s2 sens1e-4')
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(sr2.X).fp(sr2.P).fp(sr3.X).fp(sr3.P)
s.fp(k_bg.curr).fp(k_si.curr)
s.plot(magnet.field, sr1.X)
# B slow, n-line (dc205_volt=k_tg, k_bg.volt) fast
s.multimegasweep([magnet.field], [Bvec], [dc205_volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=2, fast_delay=2.5)
print("fan complete; B now", magnet.field(), "T")
