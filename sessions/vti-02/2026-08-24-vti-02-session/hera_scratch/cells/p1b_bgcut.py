# HERA — P1b: acquisition re-range (operator-authorized), then the back-gate cut
# re-run with an unclipped Rxx. Supersedes run 0 for every Rxx number.
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
print(f"pre: V_tg     = {_Vtg:+.4f} V        (expect 0.000, parked by run 0)")
print(f"pre: V_bg     = {_Vbg:+.4f} V        (expect +2.000, where run 0 ended)")
print(f"pre: outputs  = TG {_out_tg} / BG {_out_bg}")
assert 1.10 <= _Ts <= 1.40, f"T_sample {_Ts} K outside base window"
assert abs(_B) <= 0.02, f"B = {_B} T, expected ~0"
assert abs(_Vsi) <= 1e-3, f"V_si = {_Vsi} V, expected 0"
assert abs(_Vtg) <= 1e-3, f"V_tg = {_Vtg} V, expected 0"
assert bool(_out_tg) and bool(_out_bg), "Keithley source output OFF — gate sets would be inert"

# ------------------------------------------------- acquisition re-range
# Operator-authorized (Zack, this session): set sr1 sensitivity + time constant
# from the notebook, values at my discretion. Rationale on the markdown cell.
# NOT a safety surface — no validator, limit or cap is touched here.
sr1.sensitivity(1e-3)        # 2 uV -> 1 mV : 100 kOhm of Rxx headroom at 10 nA
sr0.time_constant(0.1)       # 0.3 s -> 0.1 s (dwell is gated by the SLOWEST channel)
sr1.time_constant(0.1)
for _n, _srN in (("sr0", sr0), ("sr1", sr1)):
    print(f"post-set {_n}: sens={_srN.sensitivity():.3g} V  tau={_srN.time_constant():g} s  "
          f"slope={_srN.filter_slope():g} dB/oct")
assert sr1.sensitivity() == 1e-3 and sr0.time_constant() == 0.1 and sr1.time_constant() == 0.1, \
    "lock-in re-range did not read back as commanded"
interruptible_sleep(5)       # let the new filters settle before the first point
print(f"live at V_bg={_Vbg:+.3f}: sr1 X = {sr1.X() * 1e6:+.4f} uV "
      f"(fs {abs(sr1.R()) / sr1.sensitivity():.4f})   sr0 X = {sr0.X():+.6f} V")

# ------------------------------------------------------------------ the sweep
DATA_DIR = os.path.join(main_dir, "data")
VBG = spoints(2.00, -1.30, 133)   # REVERSE of run 0: starts where the gate sits, and
                                  # gives a hysteresis check against run 0 for free
DELAY = 0.7                       # 7*tau at the new tau = 0.1 s — compliant, not bent

meas_config["comments"] = ("bg-cut — back-gate cut at V_tg = 0 with sr1 re-ranged to 1 mV; "
                           "locates the CNP in Rxx and sets the Rxx scale for the gate map")
meas_config["sample_temperature:"] = _Ts
meas_config["Si (V)"] = _Vsi

s = sweep.AsyncStation(meas_config, basedir=DATA_DIR)
s.fp(sr0.X).fp(sr0.Y).fp(sr1.X).fp(sr1.Y)
s.fp(k_2400_tg.curr).fp(k_2400_bg.curr).fp(T_sample)
s.add_comment("bg-cut")
s.add_comment(
    "1D V_bg +2.000 -> -1.300 V (reverse of run 0), 133 pts @ 25 mV | V_tg = 0.000 V | "
    "V_si = 0.000 V | B = 0 T | T = base (~1.17 K) | delay 0.7 s = 7*tau (tau 0.1 s, 24 dB/oct) | "
    "I_bias 10.0 nA (1.0 V / 100 MOhm @ 13.777 Hz) | "
    "sr0 = drain current T_0 -> B_3, Ithaco gain -1e6, sens 20 mV | "
    "sr1 = Vxx B_1-B_2, sens NOW 1 mV (was 2 uV and clipped above 218 ohm in run 0) | "
    "run 0 put the CNP at V_bg = -0.200 V from the drain-current dip; this run measures "
    "the Rxx peak there without clipping"
)
s.plot(k_bg.volt, [sr0.X, sr0.Y, sr1.X, sr1.Y,
                   k_2400_tg.curr, k_2400_bg.curr, T_sample])

res = s.sweep(k_bg.volt, VBG, delay=DELAY)
print(f"\nrun id = {res.id}   {res.datapath}")
print(f"post: V_bg = {k_bg.volt():+.4f} V   V_tg = {k_tg.volt():+.4f} V   "
      f"T_sample = {T_sample():.3f} K   B = {magnet.field():+.4f} T")
