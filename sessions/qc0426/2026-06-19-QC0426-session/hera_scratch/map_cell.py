import numpy as np, time
# --- preconditions (state this map assumes but does not set) ---
T0 = heater.sample_temperature(); B0 = magnet.mag()
print('precond: T=%.3f K  B=%.4f T  BG=%.3f  Si=%.3f' % (T0, B0, k_2400.volt(), k_2410.volt()))
assert T0 < 2.0, 'T high'
assert abs(B0) < 0.05, 'B not zero'
assert abs(k_2410.volt()) < 1e-6, 'Si not 0'
# --- station (fresh comments) ---
meas_config['comments'] = ('0T TG-BG gatemap; BG rows slow / TG fast; Si=0 B=0; '
                           'CNP-line + clean-region survey; T_start=%.3f K' % T0)
s = async_station(meas_config)
s.add_comment('gatemap')
s.add_comment(meas_config['comments'])
# leakage monitors (Keithleys only; NOT Lakeshore -- rig quirk)
s.fp(k_2400.curr); s.fp(k_2410.curr)
# lock-ins: RAW X and P (gains live in metadata for hera-watch/analysis)
for sr in (sr0, sr1, sr2, sr3):
    s.fp(sr.X); s.fp(sr.P)
s.plot(dc205_volt, sr1.X)
# ramp to start of box
s.ramp(k_2400.volt, -4.5)     # BG slow start
s.ramp(dc205_volt, -6.0)      # TG fast start (blocking)
time.sleep(1)
bg_vec = spoints(-4.5, 4.5, 37)    # slow rows, 0.25 V
tg_vec = spoints(-6.0, 7.0, 131)   # fast, 0.10 V
s.megasweep(k_2400.volt, bg_vec, dc205_volt, tg_vec, slow_delay=2.0, fast_delay=1.0)
# park gates
s.ramp(dc205_volt, 0.0); s.ramp(k_2400.volt, 0.0)
print('gatemap done; T_end=%.3f K' % heater.sample_temperature())
