# HERA — plan step P4: Landau fan at fixed D = 0, base T.
# Density (co-swept V_tg, V_bg along the measured D = 0 line) is the fast axis;
# field is the slow axis on a 1/B-uniform grid so sdh_fft needs no resample.
# ---------------------------------------------------------------- preconditions
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"],
                        max_age=15, max_period=12)
_Ts = T_sample()
_B = magnet.field()
_Vsi = dc205.voltage()
_psw, _outp = magnet.persistent_switch_on(), magnet.output_enabled()
_out_tg, _out_bg = k_2400_tg.output(), k_2400_bg.output()
print(f"pre: T_sample = {_Ts:.3f} K     (expect 1.10-1.40)")
print(f"pre: B        = {_B:+.4f} T    (measured readback; this cell ramps the magnet)")
print(f"pre: psw={_psw} output={_outp}  (field() raises if either is off)")
print(f"pre: V_si     = {_Vsi:+.4f} V   (expect 0; this cell does not move Si)")
print(f"pre: outputs  = TG {_out_tg} / BG {_out_bg}")
print(f"pre: sr0 tau={sr0.time_constant():g}s sens={sr0.sensitivity():.3g}V | "
      f"sr1 tau={sr1.time_constant():g}s sens={sr1.sensitivity():.3g}V")
assert 1.10 <= _Ts <= 1.40, f"T_sample {_Ts} K outside base window"
assert abs(_B) <= 0.05, f"B = {_B} T, expected ~0 at the start of the fan"
assert bool(_psw) and bool(_outp), "persistent switch or output off — magnet cannot ramp"
assert abs(_Vsi) <= 1e-3, f"V_si = {_Vsi} V, expected 0"
assert bool(_out_tg) and bool(_out_bg), "Keithley source output OFF — gate sets would be inert"
assert sr0.time_constant() == 0.1 and sr1.time_constant() == 0.1, "tau is not 0.1 s"
assert sr1.sensitivity() == 1e-3, "sr1 sensitivity is not 1 mV"

# --------------------------------------- the D = 0 line, from THIS session's map
# run 3 CNP-line fit (a4_symmetry): V_tg = -0.7851*V_bg - 0.0060
#   => measured c_tg/c_bg = 1.2737 +/- 0.0470   (geometry prior was 1.1579)
# D = 0  <=>  c_tg*V_tg = c_bg*V_bg  <=>  V_bg = 1.2737 * V_tg
RATIO = 1.2737                      # measured this session, NOT the geometry prior
VTG = spoints(-0.30, 0.60, 46)      # 20 mV steps along the D = 0 line
VBG = RATIO * VTG                   # co-swept partner
# n = 2*c_tg*(V_tg + 0.003)/e  along this line  ->  -1.04e12 .. +2.10e12 cm^-2
assert VTG.min() >= -0.3 and VTG.max() <= 1.0, "fast V_tg outside the TG operating limit"
assert VBG.min() >= -1.3 and VBG.max() <= 2.0, "fast V_bg outside the BG operating limit"

BVEC = field_invB(0.75, 6.0, 40)    # uniform in 1/B, ascending
assert BVEC.max() <= 10.0, "field vector exceeds the session cap"

DATA_DIR = os.path.join(main_dir, "data")
meas_config["comments"] = ("landau-fan — Rxx(n, B) at fixed D = 0 on the session-measured "
                           "CNP line; LL degeneracy + SdH tone count + the first ABSOLUTE "
                           "density calibration (everything so far rests on the geometry prior)")
meas_config["sample_temperature:"] = _Ts
meas_config["Si (V)"] = _Vsi

s = sweep.AsyncStation(meas_config, basedir=DATA_DIR)
s.fp(sr0.X).fp(sr0.Y).fp(sr1.X).fp(sr1.Y)
s.fp(k_2400_tg.curr).fp(k_2400_bg.curr).fp(T_sample).fp(magnet.field)
s.add_comment("landau-fan")
s.add_comment(
    "2D multimegasweep | slow magnet.field 0.750 -> 6.000 T, 40 rows UNIFORM IN 1/B "
    "(hera.analysis.field_invB, so sdh_fft needs no resample) | "
    "fast co-swept (V_tg, V_bg) along D = 0: V_tg -0.300 -> +0.600 V, 46 pts @ 20 mV, "
    "V_bg = 1.2737*V_tg | n = -1.04e12 .. +2.10e12 cm^-2, CNP at V_tg = -0.003 | "
    "1840 pts | V_si = 0.000 V | T = base (~1.17 K) | "
    "fast_delay 0.7 s = 7*tau (tau 0.1 s, 24 dB/oct), slow_delay 1.0 s after each field ramp | "
    "I_bias 10.0 nA | sr0 = drain current T_0 -> B_3, Ithaco -1e6, sens 20 mV | "
    "sr1 = Vxx B_1-B_2, sens 1 mV | magnet.field followed per point (the setpoint is NOT "
    "the field on this supply) | ratio 1.2737 is the c_tg/c_bg MEASURED from run 3's CNP "
    "line, not the geometry prior 1.1579"
)
s.plot(k_tg.volt, [sr0.X, sr0.Y, sr1.X, sr1.Y,
                   k_2400_tg.curr, k_2400_bg.curr, T_sample, magnet.field])
# no 2D live plot — it killed run 2 (see the P2 re-run cell)

res = s.multimegasweep([magnet.field], [BVEC], [k_tg.volt, k_bg.volt], [VTG, VBG],
                       slow_delay=1.0, fast_delay=0.7, init_delay=True)
print(f"\nrun id = {res.id}   {res.datapath}")
print(f"post: B = {magnet.field():+.4f} T   V_tg = {k_tg.volt():+.4f} V   "
      f"V_bg = {k_bg.volt():+.4f} V   T_sample = {T_sample():.3f} K")
