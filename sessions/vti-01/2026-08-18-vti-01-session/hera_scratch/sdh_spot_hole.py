# === SdH spot check, hole side: n = -1.8e12, D = 0, B 0.8 -> 9 T (E1 auto) ===
# Design (investigation step 2/3): F_L = 18.6 T; Nyquist(1/3) d(1/B) = 1.79e-2 /T;
# blocking magnet => uniform-B, dB = d(1/B)*B_lo^2 = 11 mT @ B_lo = 0.8 T.
# Expected onset 1-2 T (T_e ~ 8 K); B_lo sits below it and reads it directly.

# --- preconditions ---
_B, _T, _amp = magnet.field(), T_sample(), sr1.amplitude()
print(f"preconditions: B={_B:+.4f} T (~0, map endpoint), T={_T:.3f} K, "
      f"drive={_amp*1e3:.0f} mV (100), Vsi={dc205.voltage():+.2f} (~0)")
assert abs(_B) < 0.05 and _T < 1.5, "B/T precondition failed — stop"
assert abs(_amp - 0.100) < 0.005 and abs(dc205.voltage()) < 0.05, "drive/Si precondition failed — stop"

# gate point from the committed calibration
n_h, D_h = -1.8, 0.0                      # 1e12 cm^-2, V/nm
Vtg_h, Vbg_h = calc_gate_voltages(n_h, D_h, c_tg_cal, c_bg_cal, n_offset=n_off_e12)
print(f"target: n={n_h}e12, D=0 -> Vtg={Vtg_h:+.4f}, Vbg={Vbg_h:+.4f}")
assert abs(Vtg_h) <= 0.8 and abs(Vbg_h) <= 5.0

# sensitivities for the field axis (headroom over precision — QH peaks grow with B):
# sr1/sr3 200 uV fs (~218 kOhm soft-clip at ~1 nA), sr2 50 uV (weak pair), sr0 10 mV.
sr1.sensitivity(200e-6); sr3.sensitivity(200e-6); sr2.sensitivity(50e-6)
print(f"sens: sr1/sr3 200 uV, sr2 50 uV, sr0 {sr0.sensitivity()} V; tau 0.1 s, delay 1 s (10 tau)")

B_vec = np.linspace(0.8, 9.0, 746)        # dB = 11.0 mT
mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": (f"sdh-spot-check hole side: n={n_h}e12 cm^-2, D=0 "
                   f"(Vtg={Vtg_h:+.4f}, Vbg={Vbg_h:+.4f}), B 0.8->9.0 T uniform-B "
                   f"dB=11 mT (Nyquist/3 on F_L=18.6 T at B_lo=0.8), delay 1 s, "
                   f"drive 100 mV; Rxx normalize by sr0 current per point; "
                   f"sens sr1/sr3 200uV sr2 50uV.")}
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'hole side: n = {n_h}e12, D = 0, (Vtg, Vbg) = ({Vtg_h:+.4f}, {Vbg_h:+.4f})')

s.ramp(k_tg.volt, Vtg_h)
s.ramp(k_bg.volt, Vbg_h)
interruptible_sleep(5)

xp = magnet.field
s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(T_sample)
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
s.plot(xp, T_sample)
for lia in [sr0, sr1, sr2, sr3]:
    s.fp(lia.X).fp(lia.P)
    s.plot(xp, lia.X)
    s.plot(xp, lia.P)

# position (blocking ramp is the settle), then sweep up; magnet HOLDS at 9 T
# for the electron-side spot check to ride back down — no re-traverse.
s.ramp(magnet.field, 0.8)
s.sweep(magnet.field, B_vec, delay=1)
print(f"hole spot check done; B holds at {magnet.field():+.3f} T, gates at hole point")
