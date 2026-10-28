# === Session shutdown (operator request) ===
# 1) excitation back to standing 5 nA; 2) ground the device contacts, Si untouched.
sr1.amplitude(0.5)                      # 0.5 V / 100 MOhm = 5 nA (standing excitation)
print('excitation:', sr1.amplitude(), 'V =', sr1.amplitude()/1e8*1e9, 'nA')

# mux.park() grounds every MANAGED contact line; Si lines 16/11 are excluded from the
# managed set, so they stay closed (Si gate preserved). This is NOT qsw.reset().
mux.park()
print('mux parked: managed contact lines grounded; routing now', mux._routing)

# state readback for the hand-back record
print('B =', round(magnet.mag(), 3), 'T | TG(k_tg) =', k_tg.voltage(), 'V | BG =',
      k_bg.volt(), 'V | Si(k_2410) =', k_2410.volt(), 'V | T =', heater.sample_temperature(), 'K')
