# === SdH spot B — hole n=-8e12, D=0, B 8->0T descending (sdh-spot-check.md) ===
# Investigation step 3, hole side (ML/BL often more balanced -> clearer f_ML).
# Magnet sits at 8T from spot A -> descend (no wasted traverse; doubles as the
# magnet-home leg). Sens corrected for the climbing MR: 20uV Rxx (FS 400 ohm vs the
# ~220 ohm electron-side max), 50uV Rxy. 50 nA, dB 12.5mT, dwell 2.5s. F_L=82.7T.

Vtg_op, Vbg_op = -3.690, -2.838   # calibration: n=-8e12, D=0

# preconditions (magnet at ~8T; gates currently at electron point -> will be set)
T0 = heater.sample_temperature()
assert T0 < 1.5, f'T not base: {T0} K'
assert abs(k_2410.volt()) < 1e-6, f'Si not 0: {k_2410.volt()} V'
assert 7.5 < magnet.mag() < 8.05, f'expected magnet ~8T, got {magnet.mag()}'
print(f'pre: B={magnet.mag():.3f}T T={T0:.3f}K Si={k_2410.volt()}V')

mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4",
            "sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
sr1.amplitude(5.0)                                                   # 50 nA
sr0.sensitivity(0.1); sr1.sensitivity(20e-6); sr2.sensitivity(20e-6); sr3.sensitivity(50e-6)

# ramp gates from electron (+3.84/+2.95) to hole point (-3.69/-2.84) at B=8T.
# Both legal in validators. dc205_volt internal ramp 2V/s; k_bg via step.
k_bg.volt(Vbg_op); dc205_volt(Vtg_op); time.sleep(3)
print(f'gates set: TG(k_tg)={k_tg.voltage():.3f} BG={k_bg.volt():.3f}')

meas_config["sr0"]="drain I B7 (Ithaco x-1e6)"; meas_config["sr1"]="Rxx T3-T4"
meas_config["sr2"]="Rxx B4-B5"; meas_config["sr3"]="Rxy T5-B6"
meas_config["bias_voltage"]=sr1.amplitude(); meas_config["lockin_freq"]=sr1.frequency()
meas_config["sr0_sens"]=sr0.sensitivity(); meas_config["sr1_sens"]=sr1.sensitivity()
meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
meas_config["sample_temperature:"]=heater.sample_temperature(); meas_config["Si (V)"]=k_2410.volt()
meas_config["comments"]=("SdH spot B: n=-8e12 h D=0 (Vtg-3.69/Vbg-2.84), B 8->0T descending, "
                         "dB 12.5mT, 50nA, sens sr0 0.1V/Rxx 20uV/Rxy 50uV, dwell 2.5s")

s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('hole n=-8e12 D=0; B 8->0T descending 12.5mT; 50nA; FS-count step 3')

for lia in (sr0, sr1, sr2, sr3): s.fp(lia.X).fp(lia.P)
s.plot(magnet.mag, sr1.X); s.plot(magnet.mag, sr2.X)

s.sweep(magnet.mag, spoints(8.0, 0.0, 641), delay=2.5)   # descending
print('SdH spot B done; field at', round(magnet.mag(),3), 'T (home)')
