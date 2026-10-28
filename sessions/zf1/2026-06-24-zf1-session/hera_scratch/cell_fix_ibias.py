# === Fix stale I_bias in meas_config (drive amplitude set AFTER config cell) ===
# meas_config['bias_voltage_1'] was captured before the AC drive was set, so
# metadata carried I_bias = residual ~4 mV / 100 MOhm = 40 pA, while the true
# device current is ~1 nA (0.1 V across 100 MOhm). Set the drive explicitly,
# then refresh the config so every downstream run records the correct I_bias.
sr830_1.amplitude(0.1)           # 0.1 V -> 1 nA through the 100 MOhm bias resistor
meas_config["bias_voltage_1"] = sr830_1.amplitude()
meas_config["lockin_freq_1"]  = sr830_1.frequency()

I_bias = meas_config["bias_voltage_1"] / meas_config["bias_resistor"]
print("drive amplitude :", sr830_1.amplitude(), "V")
print("bias_resistor   :", meas_config["bias_resistor"], "Ohm")
print("=> I_bias        :", I_bias, "A   (expect ~1e-9)")
assert abs(I_bias - 1e-9) < 2e-10, "I_bias not ~1 nA -- check drive amplitude"

# --- lock-in diagnostics (to size the gate-map fast_delay + sensitivity) ---
for nm, lia in [("sr830_1", sr830_1), ("sr830_2", sr830_2), ("sr830_3", sr830_3)]:
    print(f"{nm}: TC={lia.time_constant()} s  sens={lia.sensitivity()} V  "
          f"freq={lia.frequency()} Hz  phase={lia.phase()} deg")
print("gates now: k_tg.volt", k_tg.volt(), " k_bg.volt", k_bg.volt())
print("field:", magnet.field(), "T")
