# --- SdH spot check 2/2: electron side n=+6e12, D=0, B 8->1 T uniform-B --- slug: sdh-spot-check
B0, Ts = magnet.field(), T_sample()
print(f"pre: B={B0:+.3f} T (expect ~8, SC1 endpoint) | T={Ts:.3f} K")
assert 7.9 < B0 < 8.05 and 1.0 < Ts < 1.5, "precondition mismatch"
assert abs(k_si()) < 0.01, "Si gate not at 0"
assert abs(k_tg.volt()) < 0.01 and abs(k_bg.volt()) < 0.01, "gates not parked"
print(f"drive {sr1.amplitude()} V @ {sr1.frequency():.2f} Hz (expect 2 V); "
      f"sens sr1 {sr1.sensitivity()}, sr2 {sr2.sensitivity()}, sr3 {sr3.sensitivity()}")
assert abs(sr1.amplitude() - 2.0) < 1e-2

VTG, VBG = +2.8342, +2.2075   # n=+6e12, D=0 (run-4 calibration)
B_vec = np.linspace(8.0, 1.0, 1303)   # descending; dB = 5.38 mT

settle_saved = magnet.settle_s
magnet.settle_s = 1.2
mc = dict(meas_config)
mc["comments"] = ("SdH spot check electron side: n=+6e12 cm^-2, D=0 (Vtg +2.8342, Vbg +2.2075), "
                  "B 8->1 T descending, 1303 pts dB=5.38mT, 20nA@13Hz, T~1.17K")
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment('electron side; F_L=62.0 T nominal; rides SC1 endpoint 8 T down to 1 T for the fan')
s.ramp(k_tg.volt, VTG); s.ramp(k_bg.volt, VBG)
interruptible_sleep(10)
s.fp(T_sample)
s.fp(k_tg.curr).fp(k_bg.curr)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(magnet.field, lia.X)
s.plot(magnet.field, k_tg.curr)
s.plot('time', T_sample)

try:
    s.sweep(magnet.field, B_vec, delay=0)
finally:
    magnet.settle_s = settle_saved
    k_tg.volt(0); k_bg.volt(0)
    print(f"end: B={magnet.field():+.3f} T (fan starts near here), gates parked, settle_s={magnet.settle_s}")
