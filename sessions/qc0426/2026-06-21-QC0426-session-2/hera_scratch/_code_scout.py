import numpy as np
import time

# Step-6 scout: QH-viability n-sweep at fixed B=7.95 T, electron D=0 low-n (n=0.2-1.5e12).
Vtgs = np.array([0.1811, 0.1915, 0.2018, 0.2122, 0.2226, 0.2329, 0.2433, 0.2537, 0.264, 0.2744,
                 0.2848, 0.2951, 0.3055, 0.3159, 0.3262, 0.3366, 0.347, 0.3573, 0.3677, 0.3781,
                 0.3884, 0.3988, 0.4092, 0.4195, 0.4299, 0.4403, 0.4506, 0.461, 0.4714, 0.4817,
                 0.4921, 0.5025, 0.5128, 0.5232, 0.5336, 0.5439, 0.5543, 0.5647, 0.575, 0.5854,
                 0.5957, 0.6061, 0.6165, 0.6268, 0.6372, 0.6476, 0.6579, 0.6683, 0.6787, 0.689,
                 0.6994, 0.7098, 0.7201, 0.7305, 0.7409, 0.7512, 0.7616, 0.772, 0.7823, 0.7927])
Vbgs = np.array([0.1383, 0.1463, 0.1542, 0.1621, 0.17, 0.1779, 0.1858, 0.1938, 0.2017, 0.2096,
                 0.2175, 0.2254, 0.2334, 0.2413, 0.2492, 0.2571, 0.265, 0.273, 0.2809, 0.2888,
                 0.2967, 0.3046, 0.3125, 0.3205, 0.3284, 0.3363, 0.3442, 0.3521, 0.3601, 0.368,
                 0.3759, 0.3838, 0.3917, 0.3997, 0.4076, 0.4155, 0.4234, 0.4313, 0.4392, 0.4472,
                 0.4551, 0.463, 0.4709, 0.4788, 0.4868, 0.4947, 0.5026, 0.5105, 0.5184, 0.5264,
                 0.5343, 0.5422, 0.5501, 0.558, 0.5659, 0.5739, 0.5818, 0.5897, 0.5976, 0.6055])
B_FIXED = 7.95

# QH-appropriate sensitivities (run-5 corner clipped at 1e-4 / 5e-5)
sr1.sensitivity(5e-4); sr2.sensitivity(5e-4); sr3.sensitivity(2e-3)

meas_config['comments'] = ("step6-scout QH-viability: n-sweep D=0 ELECTRON n=0.2-1.5e12 "
                           "(nu 1.0-7.8) at FIXED B=7.95T; sr1/2=5e-4 sr3=2e-3; dwell2.5; Si=0. "
                           "Does clean QH develop (Rxx minima / Rxy plateaus)? gates: gatemap-in-field form.")
for k, sr in [('sr0_sens', sr0), ('sr1_sens', sr1), ('sr2_sens', sr2), ('sr3_sens', sr3)]:
    meas_config[k] = sr.sensitivity()
meas_config['bias_voltage'] = sr1.amplitude(); meas_config['lockin_freq'] = sr1.frequency()
meas_config['sample_temperature:'] = heater.sample_temperature(); meas_config['Si (V)'] = k_si.volt()

print("T:", heater.sample_temperature(), "K  B:", magnet.field(), "T  Si:", k_si.volt(),
      "V  sens(1/2/3):", sr1.sensitivity(), sr2.sensitivity(), sr3.sensitivity())

# Gates to n-start, then ramp magnet 1.0 -> 7.95 T (blocks ~51 min)
dc205_volt(Vtgs[0]); k_bg.volt(Vbgs[0]); time.sleep(2)
print("ramping magnet to", B_FIXED, "T (~51 min from 1 T) ...")
magnet.field(B_FIXED)
print("at B =", magnet.field(), "T")

s = async_station(meas_config)
s.add_comment('field-sweep-1d')   # base recipe for the call surface; scout intent in structured comment
s.add_comment(f'step6-scout n[0.2-1.5]e12 D=0 @B={B_FIXED}T sens5e-4')
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P).fp(sr2.X).fp(sr2.P).fp(sr3.X).fp(sr3.P)
s.fp(k_bg.curr).fp(k_si.curr)
s.plot(dc205_volt, sr1.X)
s.multisweep([dc205_volt, k_bg.volt], [Vtgs, Vbgs], delay=2.5)
print("scout complete; B now", magnet.field(), "T")
