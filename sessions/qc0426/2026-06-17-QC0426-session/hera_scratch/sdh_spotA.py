# === SdH spot check A — electron n=+8e12, D=0, B 0->8T (sdh-spot-check.md) ===
# Investigation step 3: pin onset, tone content vs F_L=82.7T, and which side is
# cleaner. Device R ~30 ohm at this n -> boost AC drive to 50 nA for SNR; sens 20uV
# (Rxx) / 50uV (Hall, R_xy up to ~630 ohm at 8T); dwell 2.5s (~8 tau, weak-tone
# settling floor); B-step 12.5 mT (Nyquist on F_L to ~1.7 T).

Vtg_op, Vbg_op = 3.838, 2.952   # calibration: n=+8e12, D=0

# --- preconditions ---
B0 = magnet.mag(); T0 = heater.sample_temperature()
assert abs(B0) < 0.05, f'field not ~0 at start: {B0} T'
assert T0 < 1.5,       f'T not base: {T0} K'
assert abs(k_2410.volt()) < 1e-6, f'Si not 0: {k_2410.volt()} V'
print(f'pre: B={B0:.4f}T T={T0:.3f}K Si={k_2410.volt()}V')

# routing + drive + sens
mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4",
            "sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
sr1.amplitude(5.0)                  # 5 V / 100 MOhm = 50 nA current bias
sr1.sensitivity(20e-6); sr2.sensitivity(20e-6); sr3.sensitivity(50e-6)

# ramp gates to operating point (within validators; TG+3.84<7, BG+2.95<4.5)
k_bg.volt(Vbg_op)
dc205_volt(Vtg_op)
time.sleep(3)
print(f'gates set: TG(k_tg)={k_tg.voltage():.3f} BG={k_bg.volt():.3f} ; Ibias={sr1.amplitude()/1e8*1e9:.0f} nA')

meas_config["sr0"]="drain I B7 (Ithaco x-1e6)"; meas_config["sr1"]="Rxx T3-T4"
meas_config["sr2"]="Rxx B4-B5"; meas_config["sr3"]="Rxy T5-B6"
meas_config["bias_voltage"]=sr1.amplitude(); meas_config["lockin_freq"]=sr1.frequency()
meas_config["sr0_sens"]=sr0.sensitivity(); meas_config["sr1_sens"]=sr1.sensitivity()
meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
meas_config["sample_temperature:"]=heater.sample_temperature(); meas_config["Si (V)"]=k_2410.volt()
meas_config["comments"]=("SdH spot A: n=+8e12 e D=0 (Vtg+3.84/Vbg+2.95), B 0->8T, "
                         "dB 12.5mT, 50nA bias, sens 20uV(Rxx)/50uV(Rxy), dwell 2.5s")

s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('electron n=+8e12 D=0; B 0->8T 12.5mT; 50nA; FS-count step 3')

# B already at 0; magnet.mag blocks per step (no pre-sleep; never s.ramp it).
s.fp(k_bg.curr); s.fp(k_2410.curr)
for lia in (sr0, sr1, sr2, sr3): s.fp(lia.X).fp(lia.P)
s.plot(magnet.mag, sr1.X); s.plot(magnet.mag, sr2.X)

s.sweep(magnet.mag, spoints(0.0, 8.0, 641), delay=2.5)
print('SdH spot A done; field at', magnet.mag(), 'T (left at 8T for descending spot B)')
