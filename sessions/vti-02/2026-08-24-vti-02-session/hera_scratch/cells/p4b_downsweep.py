# HERA — P4b: SdH trace on the way DOWN. The activation ladder needs B = 0, so the
# 6 T -> 0 ramp is unavoidable; measuring through it costs ~13 min over a bare ramp and
# yields the session's finest-resolution SdH data (100 field points uniform in 1/B at 5
# fixed densities) for the Fermi-pocket count.
# ---------------------------------------------------------------- preconditions
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"],
                        max_age=15, max_period=12)
_Ts = T_sample()
_B = magnet.field()
_Vsi = dc205.voltage()
_psw, _outp = magnet.persistent_switch_on(), magnet.output_enabled()
print(f"pre: T_sample = {_Ts:.3f} K     (expect base, 1.10-1.40)")
print(f"pre: B        = {_B:+.4f} T    (measured; expect ~6 T where the fan ended)")
print(f"pre: psw={_psw} output={_outp}")
print(f"pre: V_si     = {_Vsi:+.4f} V")
print(f"pre: sr1 tau={sr1.time_constant():g}s sens={sr1.sensitivity():.3g}V")
assert 1.10 <= _Ts <= 1.40, f"T_sample {_Ts} K outside base window"
assert 5.5 <= _B <= 6.5, f"B = {_B} T — expected the fan to have left the magnet near 6 T"
assert bool(_psw) and bool(_outp), "persistent switch or output off — magnet cannot ramp"
assert abs(_Vsi) <= 1e-3, f"V_si = {_Vsi} V, expected 0"
assert sr0.time_constant() == 0.1 and sr1.time_constant() == 0.1, "tau is not 0.1 s"
assert sr1.sensitivity() == 1e-3, "sr1 sensitivity is not 1 mV"

# ---- fixed densities on the measured D = 0 line -----------------------------
# n [e12 cm^-2] = 3.49*(V_tg + 0.003) along V_bg = 1.2737*V_tg
RATIO = 1.2737
N_TARGETS = np.array([-0.80, 0.50, 1.00, 1.50, 2.00])   # e12 cm^-2
VTG_N = N_TARGETS / 3.49 - 0.003
VBG_N = RATIO * VTG_N
assert VTG_N.min() >= -0.3 and VTG_N.max() <= 1.0, "V_tg outside the operating limit"
assert VBG_N.min() >= -1.3 and VBG_N.max() <= 2.0, "V_bg outside the operating limit"

BVEC = field_invB(6.0, 0.5, 100)     # DESCENDING, uniform in 1/B -> sdh_fft needs no resample
assert BVEC.max() <= 10.0, "field vector exceeds the session cap"
# FFT: d(1/B) = 1.833 /T -> resolution 0.55 T; Nyquist 27 T vs max Onsager 20.7 T at n=2e12

DATA_DIR = os.path.join(main_dir, "data")
meas_config["comments"] = ("sdh-downsweep — Rxx(B) at 5 fixed densities on the D = 0 line, "
                           "6 -> 0.5 T uniform in 1/B; Fermi-pocket count from the SdH tone "
                           "structure, measured through the ramp the T-ladder requires anyway")
meas_config["sample_temperature:"] = _Ts
meas_config["Si (V)"] = _Vsi

s = sweep.AsyncStation(meas_config, basedir=DATA_DIR)
s.fp(sr0.X).fp(sr0.Y).fp(sr1.X).fp(sr1.Y)
s.fp(k_2400_tg.curr).fp(k_2400_bg.curr).fp(T_sample).fp(magnet.field)
s.add_comment("sdh-downsweep")
s.add_comment(
    "2D multimegasweep | slow magnet.field 6.000 -> 0.500 T DESCENDING, 100 rows uniform "
    "in 1/B (field_invB) | fast co-swept (V_tg, V_bg) at 5 fixed densities on the measured "
    f"D = 0 line: n = {list(N_TARGETS)} e12 cm^-2, V_tg = {list(np.round(VTG_N, 4))}, "
    f"V_bg = 1.2737*V_tg | 500 pts | T = base | V_si = 0.000 V | "
    "fast_delay 0.7 s = 7*tau, slow_delay 0.5 s (the magnet's own settle_s=3 already "
    "gates each field setpoint) | I_bias 10.0 nA | sr1 sens 1 mV | "
    "magnet.field followed per point (setpoint is NOT field on this supply) | "
    "d(1/B) = 1.833 /T -> FFT resolution 0.55 T, Nyquist 27 T vs 20.7 T Onsager at n=2e12 | "
    "ends at 0.5 T; a short bare ramp then takes the magnet to 0 for the T-ladder"
)
s.plot(k_tg.volt, [sr0.X, sr0.Y, sr1.X, sr1.Y,
                   k_2400_tg.curr, k_2400_bg.curr, T_sample, magnet.field])

res = s.multimegasweep([magnet.field], [BVEC], [k_tg.volt, k_bg.volt], [VTG_N, VBG_N],
                       slow_delay=0.5, fast_delay=0.7, init_delay=True)
print(f"\nrun id = {res.id}   {res.datapath}")
print(f"post: B = {magnet.field():+.4f} T   T_sample = {T_sample():.3f} K")
