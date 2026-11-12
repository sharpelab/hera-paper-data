# === HERA E1 preflight — read-only namespace + state probe (first E1 execute) ===
# Confirms this kernel is the operator's instrument-carrying kernel and
# snapshots the session-start VERIFY reads. READ-ONLY: no gate/field/mux writes.

# 1) Kernel binding — the instruments are live objects in THIS kernel
need = ['magnet','heater','sr0','sr1','sr2','sr3','k_bg','k_2410','k_tg','qsw','mux','dc205_volt']
missing = [n for n in need if n not in globals()]
assert not missing, f'KERNEL-BINDING FAIL: missing {missing}'
print('namespace OK:', {n: type(globals()[n]).__name__ for n in ['magnet','heater','qsw','mux']})

# 2) Magnet — set-vs-read (VERIFY 1) + committed field-cap validator (Gate B)
print('magnet.mag() [measured] =', magnet.mag(), 'T')
print('magnet._status() =', magnet._status())
print('magnet.mag.vals =', magnet.mag.vals)

# 3) Temperature (VERIFY 3)
print('sample_T =', heater.sample_temperature(), 'K | vaporizer_T =', heater.vaporizer_temperature(), 'K')

# 4) Gate setpoints + committed validators (Gate B readback).
#    dc205_volt has no get_cmd -> read k_tg.voltage() for the TG value.
print('TG k_tg.voltage =', k_tg.voltage(), 'V | val', k_tg.voltage.vals)
print('BG k_bg.volt    =', k_bg.volt(), 'V | val', k_bg.volt.vals)
print('Si k_2410.volt  =', k_2410.volt(), 'V | val', k_2410.volt.vals, '| ramp step', k_2410.volt.step, 'V')

# 5) Lock-in settling — record tau + filter_slope at bring-up
#    (rig card: kit does NOT set these; run metadata stores them as None,
#     so this print is the only on-disk record of tau this session)
for s_ in [sr0, sr1, sr2, sr3]:
    print(f'{s_.name}: tau={s_.time_constant()}s slope={s_.filter_slope()} '
          f'sens={s_.sensitivity()} f={s_.frequency()}Hz ampl={s_.amplitude()}V')

# 6) QSwitch identity (Si standing closures on lines 16/11 validated at bring-up
#    per device card; qsw.reset() is ALWAYS forbidden — would drop the Si gate)
print('qsw IDN:', qsw.IDN())
