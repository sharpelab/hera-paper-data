# HERA — plan step P5: temperature ladder at B = 0. Activation gap Delta(D) at the CNP.
# One CNP-line patch per temperature; each temperature writes its own run dir.
# ---------------------------------------------------------------- preconditions
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"],
                        max_age=15, max_period=12)
_Ts = T_sample()
_B = magnet.field()
_Vsi = dc205.voltage()
print(f"pre: T_sample = {_Ts:.3f} K     (expect base, 1.10-1.40)")
print(f"pre: B        = {_B:+.4f} T    (expect ~0.5 T, where the down-sweep ended)")
print(f"pre: V_si     = {_Vsi:+.4f} V")
print(f"pre: heater ranges sample={heater.sample_range()} vaporizer={heater.vaporizer_range()}")
print(f"pre: sr0 tau={sr0.time_constant():g}s | sr1 tau={sr1.time_constant():g}s "
      f"sens={sr1.sensitivity():.3g}V")
assert 1.10 <= _Ts <= 1.40, f"T_sample {_Ts} K — ladder must start from base"
assert _B <= 1.0, f"B = {_B} T — expected the down-sweep to have left the magnet near 0.5 T"
assert abs(_Vsi) <= 1e-3, f"V_si = {_Vsi} V, expected 0"
assert bool(k_2400_tg.output()) and bool(k_2400_bg.output()), "Keithley output OFF"
assert sr0.time_constant() == 0.1 and sr1.time_constant() == 0.1, "tau is not 0.1 s"
assert sr1.sensitivity() == 1e-3, "sr1 sensitivity is not 1 mV"

# ---------------------------------------- field to zero FIRST
# Activation must be measured at B = 0: a Landau gap at finite field would contaminate
# Delta. The down-sweep ended at 0.5 T, so this cell owns the last leg to zero.
# magnet.field() BLOCKS through the ramp (~4 min at the fixed 0.137 T/min).
if abs(_B) > 0.02:
    print(f"ramping {_B:+.4f} -> 0.000 T (blocking, ~{abs(_B)/0.137:.1f} min) ...")
    magnet.field(0.0)
_B0 = magnet.field()
print(f"field now {_B0:+.4f} T (measured readback)")
assert abs(_B0) <= 0.05, f"B = {_B0} T after ramp — activation needs zero field"

# ---------------------------------------- the CNP-line patch (measured, run 3)
# CNP line: V_tg = -0.7851*V_bg - 0.0060  =>  V_bg = -1.2737*V_tg - 0.00764
# One co-swept 1D path that walks the line five times, each at a different
# perpendicular offset on V_bg, concatenated into a single multisweep. (V_bg cannot
# be both a megasweep slow axis and half of the co-swept fast axis, so the "2D" patch
# is folded into one path and reshaped to (5, 49) in analysis.)
RATIO = 1.2737
VTG_L = spoints(-0.30, 0.90, 49)                  # 25 mV along the line
VBG_L = -RATIO * VTG_L - 0.00764
OFFS = np.array([-0.10, -0.05, 0.0, 0.05, 0.10])  # perpendicular offsets on V_bg
VTG_ALL = np.tile(VTG_L, len(OFFS))
VBG_ALL = np.concatenate([VBG_L + d for d in OFFS])
assert len(VTG_ALL) == len(VBG_ALL) == len(OFFS) * len(VTG_L)
assert VTG_ALL.min() >= -0.3 and VTG_ALL.max() <= 1.0, "V_tg outside the operating limit"
assert VBG_ALL.min() >= -1.3 and VBG_ALL.max() <= 2.0, "V_bg outside the operating limit"
# D/eps0 along the line ~ 0.3158*V_tg + 0.001  ->  -0.094 .. +0.285 V/nm

T_TARGETS = [None, 8.0, 12.0, 17.0, 23.0, 30.0, 40.0]   # None = base, heaters off
assert max(t for t in T_TARGETS if t) <= 100.0, "target above the session T cap"

DATA_DIR = os.path.join(main_dir, "data")


def hover(target, max_wait=600, poll=20, window=5, stab=0.05):
    """Rig-card hover acceptance: accept on STABILITY, not proximity. The sample loop is
    untuned (+1.4 K overshoot, bath-limited recovery), so waiting for |T-target| to close
    never converges below ~20 K. Returns the settled reading."""
    hist = []
    t0 = time.time()
    while time.time() - t0 < max_wait:
        interruptible_sleep(poll)
        hist.append(T_sample())
        if len(hist) >= window:
            w = hist[-window:]
            if float(np.std(w)) < stab:
                print(f"    settled: T = {np.mean(w):.3f} K (sigma {np.std(w):.4f} K over "
                      f"{window * poll} s, target {target} K) after {time.time() - t0:.0f} s")
                return float(np.mean(w))
    print(f"    WARNING: no stability within {max_wait} s; last T = {hist[-1]:.3f} K")
    return hist[-1]


results = []
for T_set in T_TARGETS:
    if T_set is None:
        print(f"\n=== base temperature (heaters off) ===")
        T_now = T_sample()
    else:
        print(f"\n=== set_both({T_set}, ratio=0.95) ===")
        heater.set_both(T_set, ratio=0.95)   # ratio 0.95 per rig card; any other value is
                                             # consent-gated and is deliberately not used
        T_now = hover(T_set)
    T_vap = T_vaporizer()
    print(f"    T_sample = {T_now:.3f} K   T_vaporizer = {T_vap:.3f} K")

    meas_config["comments"] = (f"tladder-cnp — CNP-line patch at T_sample ~ {T_now:.2f} K, "
                               f"B = 0; activation gap Delta(D) at charge neutrality")
    meas_config["sample_temperature:"] = T_now
    meas_config["Si (V)"] = dc205.voltage()

    s = sweep.AsyncStation(meas_config, basedir=DATA_DIR)
    s.fp(sr0.X).fp(sr0.Y).fp(sr1.X).fp(sr1.Y)
    s.fp(k_2400_tg.curr).fp(k_2400_bg.curr).fp(T_sample).fp(T_vaporizer)
    s.add_comment("tladder-cnp")
    s.add_comment(
        f"1D multisweep, co-swept (V_tg, V_bg), 245 pts = 5 offsets x 49 along-line pts "
        f"(reshape to (5, 49) in analysis) | line: V_bg = -1.2737*V_tg - 0.00764 "
        f"(MEASURED CNP line from run 3) | V_tg -0.300 -> +0.900 V @ 25 mV | "
        f"perpendicular V_bg offsets {list(np.round(OFFS, 3))} V so the TRUE Rxx peak is "
        f"captured even if the fitted line drifts; R_CNP(D) = max over offsets per V_tg | "
        f"D/eps0 -0.094 .. +0.285 V/nm | "
        f"T_setpoint = {T_set} K (ratio 0.95), T_sample settled = {T_now:.3f} K, "
        f"T_vaporizer = {T_vap:.3f} K | B = 0 T | V_si = 0.000 V | "
        f"delay 0.7 s = 7*tau (tau 0.1 s, 24 dB/oct) | I_bias 10.0 nA | "
        f"sr0 Ithaco -1e6 sens 20 mV | sr1 sens 1 mV"
    )
    s.plot(k_tg.volt, [sr0.X, sr0.Y, sr1.X, sr1.Y,
                       k_2400_tg.curr, k_2400_bg.curr, T_sample, T_vaporizer])

    res = s.multisweep([k_tg.volt, k_bg.volt], [VTG_ALL, VBG_ALL], delay=0.7)
    results.append((T_set, T_now, res.id))
    print(f"    run {res.id} written")

print("\n=== ladder complete ===")
for T_set, T_now, rid in results:
    print(f"  setpoint {str(T_set):>6} K -> T_sample {T_now:6.3f} K -> run {rid}")
print(f"post: T_sample = {T_sample():.3f} K  T_vaporizer = {T_vaporizer():.3f} K  "
      f"B = {magnet.field():+.4f} T  V_tg = {k_tg.volt():+.4f}  V_bg = {k_bg.volt():+.4f}")
