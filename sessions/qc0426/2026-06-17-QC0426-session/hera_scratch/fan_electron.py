# === Landau fan — electron side, D=0 (landau-fan-vti.md + fs-count step 4/5) ===
# F(n) partition-robustness test to firm the ABA call (spot checks gave the two-tone
# pair at n=+8e12; this tracks f_ML(n)+f_BL(n)=F_L(n) across density). Cleaner
# electron side. B (slow) x n-line (fast, paired gates at D=0).
#   n-line: 33 cols, n=[2,10]e12 cm^-2 (D=0). B: 1.5->8T @20mT (326 rows; resolves the
#   17/70T tones above ~2T - spot checks remain the 12.5mT anchor). 50nA; sens 20uV Rxx
#   (electron sr1 ~218 ohm@8T = 54% of 400 FS, no overload), 50uV Rxy. fast_delay 1.5s.
# Parks quiescent (gates 0, B 0) at the end for unattended hand-back.

import scipy.constants as cst
# --- D=0 gate line from the CNP calibration (run 2; ana cell 13) ---
n_off = -1.571e15                     # m^-2  (n_offset, CNP calibration)
ns_cm = np.linspace(2e12, 10e12, 33)  # electron density columns (cm^-2)
ns_m  = ns_cm * 1e4
Vbgs = (ns_m - n_off) * cst.e / (2 * c_bg)   # along D=0: c_tg*Vtg = c_bg*Vbg
Vtgs = (c_bg / c_tg) * Vbgs
assert Vtgs.max() < 7.0 and Vtgs.min() > -6.0, f'TG out of range: {Vtgs.min():.2f}..{Vtgs.max():.2f}'
assert Vbgs.max() < 4.5 and Vbgs.min() > -4.5, f'BG out of range: {Vbgs.min():.2f}..{Vbgs.max():.2f}'
B_vec = spoints(1.5, 8.0, 326)        # 20 mT step
print(f'fan grid: {len(B_vec)} B-rows x {len(ns_cm)} n-cols | n {ns_cm.min():.1e}..{ns_cm.max():.1e} '
      f'| TG {Vtgs.min():.2f}..{Vtgs.max():.2f} BG {Vbgs.min():.2f}..{Vbgs.max():.2f} | B {B_vec.min()}..{B_vec.max()}T')

# --- preconditions ---
T0 = heater.sample_temperature()
assert T0 < 1.5, f'T not base: {T0} K'
assert abs(k_2410.volt()) < 1e-6, f'Si not 0: {k_2410.volt()} V'
assert abs(magnet.mag()) < 0.05, f'expected magnet ~0 (home), got {magnet.mag()}'
print(f'pre: B={magnet.mag():.3f}T T={T0:.3f}K Si={k_2410.volt()}V')

mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4",
            "sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
sr1.amplitude(5.0)                                                    # 50 nA
sr0.sensitivity(0.1); sr1.sensitivity(20e-6); sr2.sensitivity(20e-6); sr3.sensitivity(50e-6)

meas_config["sr0"]="drain I B7 (Ithaco x-1e6)"; meas_config["sr1"]="Rxx T3-T4"
meas_config["sr2"]="Rxx B4-B5"; meas_config["sr3"]="Rxy T5-B6"
meas_config["bias_voltage"]=sr1.amplitude(); meas_config["lockin_freq"]=sr1.frequency()
meas_config["sr0_sens"]=sr0.sensitivity(); meas_config["sr1_sens"]=sr1.sensitivity()
meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
meas_config["sample_temperature:"]=heater.sample_temperature(); meas_config["Si (V)"]=k_2410.volt()
meas_config["comments"]=("landau fan electron D=0: n=[2,10]e12 x33 (fast, paired gates) x "
                         "B 1.5-8T @20mT x326 (slow), 50nA, sens 20uV Rxx/50uV Rxy, fast_delay 1.5s")

s = async_station(meas_config)
s.add_comment('landau-fan')
s.add_comment('landau-fan-vti')
s.add_comment('electron D=0 fan; n=2-10e12; B 1.5-8T; FS-count F(n) partition test')

# field starts at 0; first slow point ramps to 1.5T (blocking). gates set by fast axis.
for lia in (sr0, sr1, sr2, sr3): s.fp(lia.X).fp(lia.P)
s.plot(magnet.mag, sr1.X); s.plot(dc205_volt, sr1.X)

try:
    s.multimegasweep([magnet.mag], [B_vec],
                     [dc205_volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=2.0, fast_delay=1.5)
finally:
    # quiescent hand-back: park gates, ramp field home
    dc205_volt(0.0); k_bg.volt(0.0)
    magnet.mag(0.0)
print('FAN done. Parked: TG=0, BG=0, B=', round(magnet.mag(),3), 'T')
