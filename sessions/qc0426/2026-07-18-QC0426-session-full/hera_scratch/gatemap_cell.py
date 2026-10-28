# === Step 1 — B=0 gate map: TG fast [-3,+3]x101, BG slow [-4.5,+4.5]x101 ===
# recipes: measurements/gatemap.md -> device-init/cnp-and-dline-calibration.md
# (trilayer-stacking-fs-count Step 1)

# --- preconditions (state this cell assumes but does not set) ---
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_np_tg, _np_bg = k_2400_tg.nplci(), k_2400_bg.nplci()
print(f"preconditions: T_sample={_Ts:.3f} K (expect 1.0-1.5), B={_B:+.4f} T (expect ~0), "
      f"V_si={_Vsi:+.3f} V (expect 0), nplci tg/bg={_np_tg}/{_np_bg} (expect 1/1)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert abs(_B) <= 0.02, f"field not at zero: {_B:+.4f} T"
assert abs(_Vsi) <= 0.05, f"Si gate not parked: {_Vsi:+.3f} V"
assert _np_tg == 1 and _np_bg == 1, "nplci not reset to 1 — run the Gate C reset cell"

# --- sensitivities for the map (stated in the proposal md) ---
sr1.sensitivity(5e-5)   # headroom to R ~ 10 kOhm (gapped CNP at finite D)
sr2.sensitivity(5e-5)
sr3.sensitivity(2e-5)   # Hall, ~0 at B=0
sr0.sensitivity(1e-2)

tg_fast = np.linspace(-3.0, 3.0, 101)    # 60 mV steps
bg_slow = np.linspace(-4.5, 4.5, 101)    # 90 mV steps

meas_config["comments"] = ("gatemap: B=0, base T, Si=0; TG fast [-3,+3]x101, BG slow [-4.5,+4.5]x101, "
                           "fast_delay=1, slow_delay=3, I_bias=5 nA, sens sr1/sr2=5e-5 sr3=2e-5")
s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('first map of cooldown: full validator window, raw gate voltages (no (n,D) cal yet); '
              'input to cnp-and-dline-calibration; CNP expected near (0,0) from runs 0-3')

s.ramp(k_tg.volt, tg_fast[0])
s.ramp(k_bg.volt, bg_slow[0])
interruptible_sleep(10)

xp = k_tg.volt
s.fp(T_sample).fp(T_vaporizer)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.fp(_l.X).fp(_l.P)
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.plot(xp, _l.X)
    s.plot(xp, _l.P)
s.plot('time', T_sample)
s.plot('time', T_vaporizer)

try:
    s.megasweep(k_bg.volt, bg_slow, k_tg.volt, tg_fast,
                slow_delay=3, fast_delay=1)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
print("gatemap complete; gates parked at 0")
