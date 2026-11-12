# HERA — first 0 T gate map. recipe: measurements/gatemap.md
# Axis-aligned megasweep over (V_tg fast, V_bg slow) at B = 0, V_si = 0.
# Sweeping raw gate volts (not (n, D)) because the cap ratio is not yet
# data-calibrated — that is what this map exists to produce.
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vsi = dc205.voltage()
_B, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={k_tg.volt():+.4f} V  V_bg={k_bg.volt():+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vsi) < 0.01, "V_si not at 0"
assert abs(_B) < 0.02, "field not at zero"
assert 1.0 <= _Ts <= 1.4, "sample not at base"
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1 (Cell B)"
assert abs(sr1.filter_slope() - 24) < 1, "sr1 filter slope not 24 dB/oct"
assert np.isclose(sr1.time_constant(), 0.1), "sr1 tau not the committed 0.1 s"
print(f"acquisition: drive={sr1.amplitude()} V, I_bias={I_BIAS:.4e} A, tau={sr1.time_constant()} s, "
      f"dwell={DWELL:.2f} s, sr0 sens={sr0.sensitivity():.2e}, sr1 sens={sr1.sensitivity():.2e} "
      f"(R ceiling {sr1.sensitivity()/abs(I_BIAS)/1e3:.1f} kohm)")

TG_V = np.linspace(TG_MIN, TG_MAX, 101)     # fast axis, 13 mV steps
BG_V = np.linspace(-1.3, 1.3, 37)           # slow axis, 72 mV rows
assert TG_V.min() >= TG_MIN and TG_V.max() <= TG_MAX, "TG vector outside committed validator"
assert BG_V.min() >= BG_MIN and BG_V.max() <= BG_MAX, "BG vector outside committed validator"
print(f"grid: V_tg {TG_V[0]:+.3f} -> {TG_V[-1]:+.3f} V x{len(TG_V)} ({np.diff(TG_V)[0]*1e3:.1f} mV)  "
      f"[fast]")
print(f"      V_bg {BG_V[0]:+.3f} -> {BG_V[-1]:+.3f} V x{len(BG_V)} ({np.diff(BG_V)[0]*1e3:.1f} mV)  "
      f"[slow]")
print(f"      {len(TG_V)*len(BG_V)} points")

meas_config["comments"] = ("first 0 T gate map, full committed TG window x BG [-1.3,+1.3]; "
                           "CNP-line + (n,D) calibration substrate")
meas_config["Si (V)"] = dc205.voltage()
meas_config["sample_temperature:"] = T_sample()

s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('first 0 T gate map, B = 0 T, V_si = 0 V, base T')
s.add_comment(f'V_tg fast {TG_V[0]:+g}..{TG_V[-1]:+g} V x{len(TG_V)}; '
              f'V_bg slow {BG_V[0]:+g}..{BG_V[-1]:+g} V x{len(BG_V)}')
s.add_comment(f'I_bias = {I_BIAS:.4e} A, drive {sr1.amplitude()} V @ {sr1.frequency()} Hz')
s.add_comment(f'sr1 tau={sr1.time_constant()} s slope={sr1.filter_slope()} dB/oct, '
              f'fast_delay={DWELL:.2f} s (measured 7*tau settling floor)')
s.add_comment('substrate for device-init/cnp-and-dline-calibration')
s.add_comment('contacts hardwired: source T_0, drain B_3 (sr0), Rxx B_1-B_2 (sr1); sr2/sr3 n.c.')
s.add_comment('NOTE: TG leakage onset at V_tg ~0.62 V, reaching +88 pA excess at +1.0 V '
              '(Gate C run 0) - below the 1 nA abort; watch k_2400_tg_curr')

s.ramp(k_bg.volt, BG_V[0])
s.ramp(k_tg.volt, TG_V[0])
interruptible_sleep(10)

s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(T_sample).fp(T_vaporizer)
# every live value gets a plot
s.plot(k_tg.volt, k_tg.curr)
s.plot(k_tg.volt, k_bg.curr)
for _lia in (sr0, sr1, sr2, sr3):
    s.fp(_lia.X).fp(_lia.P)
    s.plot(k_tg.volt, _lia.X)

try:
    s.megasweep(k_bg.volt, BG_V, k_tg.volt, TG_V, slow_delay=1.0, fast_delay=DWELL)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
    print(f"parked: V_tg={k_tg.volt():+.4f} V, V_bg={k_bg.volt():+.4f} V; "
          f"I_tg={k_tg.curr():.3e} A, I_bg={k_bg.curr():.3e} A")

print("GATEMAP: done")
