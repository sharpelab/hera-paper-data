# === SdH spot check, electron side: n = +1.7e12, D = 0, B 9 -> 0.8 T (E1 auto) ===
# Rides the magnet home from the hole check's 9 T endpoint — no re-traverse.
# F_L = 17.6 T; inherits the hole grid dB = 11 mT (Nyquist/3 holds: needs <= 12.1 mT).

# --- preconditions (magnet holding at 9 T from run 8; gates at the hole point) ---
_B, _T, _amp = magnet.field(), T_sample(), sr1.amplitude()
print(f"preconditions: B={_B:+.3f} T (expect ~9), T={_T:.3f} K, drive={_amp*1e3:.0f} mV, "
      f"Vtg={k_tg.volt():+.4f}, Vbg={k_bg.volt():+.4f} (hole point), Vsi={dc205.voltage():+.2f}")
assert abs(_B - 9.0) < 0.05, f"B={_B:+.3f}, expected 9 T hold — stop"
assert _T < 1.6 and abs(_amp - 0.100) < 0.005, "T/drive precondition failed — stop"

n_e, D_e = +1.7, 0.0
Vtg_e, Vbg_e = calc_gate_voltages(n_e, D_e, c_tg_cal, c_bg_cal, n_offset=n_off_e12)
print(f"target: n={n_e:+}e12, D=0 -> Vtg={Vtg_e:+.4f}, Vbg={Vbg_e:+.4f}")
assert abs(Vtg_e) <= 0.8 and abs(Vbg_e) <= 5.0

B_vec = np.linspace(9.0, 0.8, 746)        # dB = 11.0 mT, descending
mc = {**meas_config,
      "sample_temperature:": T_sample(),
      "Si (V)": 0.0,
      "comments": (f"sdh-spot-check electron side: n={n_e:+}e12 cm^-2, D=0 "
                   f"(Vtg={Vtg_e:+.4f}, Vbg={Vbg_e:+.4f}), B 9.0->0.8 T uniform-B "
                   f"dB=11 mT (Nyquist/3 on F_L=17.6 T at B_lo=0.8), delay 1 s, "
                   f"drive 100 mV; Rxx normalize by sr0 current per point; "
                   f"sens sr1/sr3 200uV sr2 50uV. Pairs with run 8 (hole side).")}
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron side: n = {n_e:+}e12, D = 0, (Vtg, Vbg) = ({Vtg_e:+.4f}, {Vbg_e:+.4f})')

# gate move at 9 T crosses the CNP — routine; leakage watched live below
s.ramp(k_tg.volt, Vtg_e)
s.ramp(k_bg.volt, Vbg_e)
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

try:
    s.sweep(magnet.field, B_vec, delay=1)
finally:
    print(f"electron spot check done; B at {magnet.field():+.3f} T (0.8 hold — "
          f"cheap onset extension or fan start decided from the reads)")
