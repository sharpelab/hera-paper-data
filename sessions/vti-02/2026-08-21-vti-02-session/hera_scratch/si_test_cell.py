# === Si-gate test of the TG-only series segment, at B = 10 T: TG scan at V_bg = 0 with Si = 0, then Si = +25 V ===
# Precondition reads (assumed, not set)
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
print(f"pre: T_sample={_Ts:.3f} K | B={_B:+.4f} T (want ~10) | Si={_Vsi:+.3f} V (want 0) | heater ranges={_rs},{_rv} | gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f})")
assert 1.05 <= _Ts <= 1.45 and abs(_B - 10.0) < 0.05 and abs(_Vsi) < 0.01 and _rs == 0 and _rv == 0
SI_TEST = 25.0
assert SI_MIN <= SI_TEST <= SI_MAX and dc205.ramp_rate == 0.5   # pacing unchanged (consent-gated)
from sharpelab_nb.autorange import autorange_sr830s
vtg_down = np.linspace(TG_MAX, TG_MIN, 66)   # start where the gates sit (+0.88 -> +1.0 is a 0.12 V move)
vtg_up = vtg_down[::-1]

mc = dict(meas_config)
mc["comments"] = f"gate-axis TG scan at B = 10 T, Vbg = 0: Si = 0 then Si = {SI_TEST:+g} V — does Si dope the TG-only series segment (CNP at Vtg ~ -0.2 V, run 4)?"
s = sweep.AsyncStation(mc)
s.add_comment('gatemap')   # 1D gate-axis cut; the map recipe's slug for a V_tg line (no dedicated linecut recipe on this rig)
s.add_comment(f'TG linecut at Vbg = 0, B = 10 T, I = 10 nA; two runs on one station: Si = 0 V (Vtg {TG_MAX:+g} -> {TG_MIN:+g}), then Si = {SI_TEST:+g} V (Vtg {TG_MIN:+g} -> {TG_MAX:+g}); purpose: Si response of the Vbg-independent Rxx maximum at Vtg ~ -0.2 V (TG-only-gated series segment)')
s.register_run_before(autorange_sr830s, (sr0, [sr1]))
s.fp(T_sample).fp(k_bg.volt).fp(k_si)
s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X); s.plot(k_tg.volt, k_tg.curr); s.plot('time', k_bg.curr)

s.ramp(k_bg.volt, 0.0); s.ramp(k_tg.volt, vtg_down[0])
interruptible_sleep(5)
s.sweep(k_tg.volt, vtg_down, delay=0.7)                      # Si = 0
mc["Si (V)"] = SI_TEST
s.ramp(k_si, SI_TEST)                                         # DC205 ramped set at 0.5 V/s (~50 s), validators fence it
interruptible_sleep(30)
print(f"Si readback {dc205.voltage():+.3f} V")
s.sweep(k_tg.volt, vtg_up, delay=0.7)                        # Si = +25
s.ramp(k_si, 0.0)                                             # back to the spot-check / fan conditions (Si = 0)
interruptible_sleep(5)
print(f"done; Si left at {dc205.voltage():+.3f} V, gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}), B {magnet.field():+.3f} T")
