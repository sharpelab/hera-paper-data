# === SdH spot A v2 — electron n=+8e12, D=0, B 0->8T (sens corrected) ===
# Run 3 (v1) aborted: sr0 monitor overloaded at 0.01V sens (50nA*1e6=50mV). Diagnostic
# (cell 38) confirmed bias = 50 nA (linear in amplitude). Corrections: sr0 sens 0.1V;
# sr1/sr2 10uV (FS 200 ohm; Rxx ~13-30 ohm so far, ample headroom); sr3 50uV (Rxy to
# ~630 ohm at 8T). Gate-current fp dropped (gates static in a field sweep). dB 12.5mT,
# dwell 2.5s (~8 tau), B 0->8T. F_L=82.7 T.

Vtg_op, Vbg_op = 3.838, 2.952   # n=+8e12, D=0

# preconditions (field sits at ~0.74 T from the abort; sweep's first point ramps to 0)
T0 = heater.sample_temperature()
assert T0 < 1.5, f'T not base: {T0} K'
assert abs(k_2410.volt()) < 1e-6, f'Si not 0: {k_2410.volt()} V'
print(f'pre: B={magnet.mag():.3f}T (will ramp to 0 at first point) T={T0:.3f}K Si={k_2410.volt()}V '
      f'TG(k_tg)={k_tg.voltage():.3f} BG={k_bg.volt():.3f}')

mux.select({"source":"T2","drain":"B7","sr1+":"T3","sr1-":"T4",
            "sr2+":"B4","sr2-":"B5","sr3+":"T5","sr3-":"B6"})
sr1.amplitude(5.0)                                   # 50 nA bias
sr0.sensitivity(0.1); sr1.sensitivity(10e-6); sr2.sensitivity(10e-6); sr3.sensitivity(50e-6)

# gates already at operating point from v1; re-assert for reproducibility
k_bg.volt(Vbg_op); dc205_volt(Vtg_op); time.sleep(3)

meas_config["sr0"]="drain I B7 (Ithaco x-1e6)"; meas_config["sr1"]="Rxx T3-T4"
meas_config["sr2"]="Rxx B4-B5"; meas_config["sr3"]="Rxy T5-B6"
meas_config["bias_voltage"]=sr1.amplitude(); meas_config["lockin_freq"]=sr1.frequency()
meas_config["sr0_sens"]=sr0.sensitivity(); meas_config["sr1_sens"]=sr1.sensitivity()
meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
meas_config["sample_temperature:"]=heater.sample_temperature(); meas_config["Si (V)"]=k_2410.volt()
meas_config["comments"]=("SdH spot A v2: n=+8e12 e D=0 (Vtg+3.84/Vbg+2.95), B 0->8T, "
                         "dB 12.5mT, 50nA, sens sr0 0.1V/Rxx 10uV/Rxy 50uV, dwell 2.5s")

s = async_station(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('electron n=+8e12 D=0; B 0->8T 12.5mT; 50nA; FS-count step 3 (v2)')

for lia in (sr0, sr1, sr2, sr3): s.fp(lia.X).fp(lia.P)   # no gate-current reads
s.plot(magnet.mag, sr1.X); s.plot(magnet.mag, sr2.X)

s.sweep(magnet.mag, spoints(0.0, 8.0, 641), delay=2.5)
print('SdH spot A v2 done; field at', round(magnet.mag(),3), 'T (left high for descending spot B)')
