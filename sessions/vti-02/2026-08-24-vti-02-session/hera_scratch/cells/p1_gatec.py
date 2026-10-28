# HERA — plan step P1 (Gate C): back-gate liveness sweep, B = 0, base T.
# ---------------------------------------------------------------- preconditions
# State this cell ASSUMES but does not set. Under E1 there is no operator glance
# before the run, so these are the go/no-go. Stop on mismatch, before hardware moves.
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"],
                        max_age=15, max_period=12)
_Ts = T_sample()
_B = magnet.field()                 # measured readback, never the last set
_Vsi = dc205.voltage()              # Si is a silent inherited axis this cell never touches
_out_tg, _out_bg = k_2400_tg.output(), k_2400_bg.output()
print(f"pre: T_sample = {_Ts:.3f} K          (expect 1.10-1.40)")
print(f"pre: B        = {_B:+.4f} T         (expect |B| <= 0.02; this cell does not move the magnet)")
print(f"pre: V_si     = {_Vsi:+.4f} V        (expect 0; this cell does not move Si)")
print(f"pre: outputs  = TG {_out_tg} / BG {_out_bg}   (both must be ON or gate sets are inert)")
assert 1.10 <= _Ts <= 1.40, f"T_sample {_Ts} K outside base window"
assert abs(_B) <= 0.02, f"B = {_B} T, expected ~0"
assert abs(_Vsi) <= 1e-3, f"V_si = {_Vsi} V, expected 0"
assert bool(_out_tg) and bool(_out_bg), "Keithley source output OFF — gate sets would be inert"

# ------------------------------------------------------------------ fixed axis
k_tg.volt(0.000)                    # this cell owns TG: park it (paced at volt.step = 5 mV)

# ------------------------------------------------------------------ the sweep
DATA_DIR = os.path.join(main_dir, "data")   # explicit: sweep.BASEDIR is a stale re-export
VBG = spoints(-1.30, 2.00, 133)             # 25 mV steps, full committed BG range
DELAY = 2.1                                 # 7*tau at tau = 0.3 s, 24 dB/oct — compliant, not bent

meas_config["comments"] = ("gatec-liveness — 1D V_bg over the full committed range at "
                           "V_tg = 0, locating the CNP from the two-terminal drain current")
meas_config["sample_temperature:"] = _Ts
meas_config["Si (V)"] = _Vsi

s = sweep.AsyncStation(meas_config, basedir=DATA_DIR)
s.fp(sr0.X).fp(sr0.Y).fp(sr1.X).fp(sr1.Y)      # raw volts: gain lives in measurement_config
s.fp(k_2400_tg.curr).fp(k_2400_bg.curr).fp(T_sample)
s.add_comment("gatec-liveness")
s.add_comment(
    "1D V_bg -1.300 -> +2.000 V, 133 pts @ 25 mV | V_tg = 0.000 V | V_si = 0.000 V | "
    "B = 0 T | T = base (~1.17 K) | delay 2.1 s = 7*tau (tau 0.3 s, 24 dB/oct) | "
    "I_bias 10.0 nA (1.0 V / 100 MOhm @ 13.777 Hz) | "
    "sr0 = drain current T_0 -> B_3, Ithaco gain -1e6 (VALID) | "
    "sr1 = Vxx B_1-B_2, sens 2 uV and RAILED at fs 1.01 — read sr0 this run | "
    "TG/BG leakage baseline at 0 V: -101 pA / +24 pA"
)
s.plot(k_bg.volt, [sr0.X, sr0.Y, sr1.X, sr1.Y,
                   k_2400_tg.curr, k_2400_bg.curr, T_sample])

res = s.sweep(k_bg.volt, VBG, delay=DELAY)
print(f"\nrun id = {res.id}   {res.datapath}")
print(f"post: V_bg = {k_bg.volt():+.4f} V   V_tg = {k_tg.volt():+.4f} V   "
      f"T_sample = {T_sample():.3f} K   B = {magnet.field():+.4f} T")
