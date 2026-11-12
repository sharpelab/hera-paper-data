# Closeout — restore instruments/device to session-start settings (operator request).
# Start state (from the bind probe, cell 30, and Gate C): bias 0.5 V; sens sr0=0.05,
# sr1=2e-5, sr2=2e-5, sr3=1e-4; tau=0.3/24dB (untouched); gates 0; B=0.
# Bias drive back to the 0.5 V / 5 nA default (was 2.0 V / 20 nA for high-|n| work)
sr1.amplitude(0.5)
# Lock-in sensitivities back to session-start
sr0.sensitivity(0.05)
sr1.sensitivity(2e-5)
sr2.sensitivity(2e-5)
sr3.sensitivity(1e-4)
# Re-assert gates parked at 0 (already there) and confirm field at 0 (PS on)
k_si.volt(0.0); k_2400.volt(0.0); dc205.ramp_voltage(0.0)

# --- confirm ---
print("bias sr1.amplitude =", sr1.amplitude(), "V  (~%.0f nA)" % (sr1.amplitude()/100e6*1e9))
for s in (sr0, sr1, sr2, sr3):
    print(f"  {s.name}: sens={s.sensitivity():.0e}  tau={s.time_constant()}  slope={s.filter_slope()}")
print("TG=%.3f BG=%.3f Si=%.3f V   B=%.4f T  PS_on=%s" % (
    dc205.voltage(), k_2400.volt(), k_2410.volt(), magnet.mag(), magnet.persistent_switch_on()))
print("sample_T =", heater.sample_temperature(), "K")
