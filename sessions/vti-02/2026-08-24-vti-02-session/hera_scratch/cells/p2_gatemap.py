# HERA — plan step P2: coarse (n, D) gate map, B = 0, base T.
# The primary stacking discriminator: R at the CNP as a function of displacement field.
# ---------------------------------------------------------------- preconditions
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"],
                        max_age=15, max_period=12)
_Ts = T_sample()
_B = magnet.field()
_Vsi = dc205.voltage()
_Vtg, _Vbg = k_tg.volt(), k_bg.volt()
_out_tg, _out_bg = k_2400_tg.output(), k_2400_bg.output()
print(f"pre: T_sample = {_Ts:.3f} K          (expect 1.10-1.40)")
print(f"pre: B        = {_B:+.4f} T         (expect |B| <= 0.02; this cell does not move the magnet)")
print(f"pre: V_si     = {_Vsi:+.4f} V        (expect 0; this cell does not move Si)")
print(f"pre: V_tg     = {_Vtg:+.4f} V        (expect 0.000)")
print(f"pre: V_bg     = {_Vbg:+.4f} V        (expect -1.300, where run 1 ended = this map's first row)")
print(f"pre: outputs  = TG {_out_tg} / BG {_out_bg}")
print(f"pre: sr0 tau={sr0.time_constant():g}s sens={sr0.sensitivity():.3g}V | "
      f"sr1 tau={sr1.time_constant():g}s sens={sr1.sensitivity():.3g}V")
assert 1.10 <= _Ts <= 1.40, f"T_sample {_Ts} K outside base window"
assert abs(_B) <= 0.02, f"B = {_B} T, expected ~0"
assert abs(_Vsi) <= 1e-3, f"V_si = {_Vsi} V, expected 0"
assert bool(_out_tg) and bool(_out_bg), "Keithley source output OFF — gate sets would be inert"
# the dwell below is 7*tau; if tau drifted back up, the dwell would silently be non-compliant
assert sr0.time_constant() == 0.1 and sr1.time_constant() == 0.1, "tau is not 0.1 s — dwell would be wrong"
assert sr1.sensitivity() == 1e-3, "sr1 sensitivity is not 1 mV — Rxx range would be wrong"

# ------------------------------------------------------------------ the map
DATA_DIR = os.path.join(main_dir, "data")
VTG = spoints(-0.30, 1.00, 66)    # fast, 20 mV steps  (small span -> cheap flyback)
VBG = spoints(-1.30, 0.40, 35)    # slow, 50 mV steps  (starts where run 1 ended)
FAST_DELAY = 0.7                  # 7*tau at tau = 0.1 s — compliant
SLOW_DELAY = 0.7

# sanity: every point of this grid must sit inside the committed validators
assert VTG.min() >= -0.3 and VTG.max() <= 1.0, "fast axis outside the TG operating limit"
assert VBG.min() >= -1.3 and VBG.max() <= 2.0, "slow axis outside the BG operating limit"

meas_config["comments"] = ("gate-map — coarse (n, D) map at B = 0, base T; the CNP line runs "
                           "diagonally across this window and R_CNP(D) is the primary "
                           "ABAB / ABCA / ABCB discriminator")
meas_config["sample_temperature:"] = _Ts
meas_config["Si (V)"] = _Vsi

s = sweep.AsyncStation(meas_config, basedir=DATA_DIR)
s.fp(sr0.X).fp(sr0.Y).fp(sr1.X).fp(sr1.Y)
s.fp(k_2400_tg.curr).fp(k_2400_bg.curr).fp(T_sample)
s.add_comment("gate-map")
s.add_comment(
    "2D megasweep | slow V_bg -1.300 -> +0.400 V, 35 rows @ 50 mV | "
    "fast V_tg -0.300 -> +1.000 V, 66 pts @ 20 mV | 2310 pts | "
    "V_si = 0.000 V | B = 0 T | T = base (~1.17 K) | "
    "fast_delay 0.7 s = 7*tau (tau 0.1 s, 24 dB/oct), slow_delay 0.7 s | "
    "I_bias 10.0 nA (1.0 V / 100 MOhm @ 13.777 Hz) | "
    "sr0 = drain current T_0 -> B_3, Ithaco -1e6, sens 20 mV | "
    "sr1 = Vxx B_1-B_2, sens 1 mV | "
    "window chosen so the CNP line is inside it: from run 1 the CNP sits at "
    "V_bg = -0.250 V when V_tg = 0, so the line is V_bg = -1.158*V_tg - 0.250 and it "
    "leaves the TG box at V_bg = +0.097 — rows above ~+0.1 V never cross the CNP, "
    "which is why the slow axis stops at +0.400 instead of +2.000 (that upper half "
    "is pure electron doping and would have cost ~25 min for no stacking information)"
)
s.plot(k_tg.volt, [sr0.X, sr0.Y, sr1.X, sr1.Y,
                   k_2400_tg.curr, k_2400_bg.curr, T_sample])
s.plot(k_tg.volt, sr1.X, k_bg.volt)      # the map itself, live

res = s.megasweep(k_bg.volt, VBG, k_tg.volt, VTG,
                  slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY, init_delay=True)
print(f"\nrun id = {res.id}   {res.datapath}")
print(f"post: V_bg = {k_bg.volt():+.4f} V   V_tg = {k_tg.volt():+.4f} V   "
      f"T_sample = {T_sample():.3f} K   B = {magnet.field():+.4f} T")
