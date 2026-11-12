# HERA — Gate C: gate-current sanity check / contact liveness.
# recipe: device-init/gate-current-sanity-check.md (Cell A, all four legs).
# Each leg sweeps one gate 0 -> a committed card limit with the other parked at
# 0, watching both gate currents at pA resolution and every lock-in.
import numpy as np

# --- preconditions this cell assumes but does not set ---
_vtg, _vbg, _vsi = k_2400_tg.volt(), k_2400_bg.volt(), dc205.voltage()
_B, _Ts = magnet.field(), T_sample()
print(f"preconditions: V_tg={_vtg:+.4f} V  V_bg={_vbg:+.4f} V  V_si={_vsi:+.4f} V  "
      f"B={_B:+.4f} T  T_sample={_Ts:.3f} K")
assert abs(_vtg) < 1e-3 and abs(_vbg) < 1e-3 and abs(_vsi) < 0.01, "gates not parked at 0"
assert abs(_B) < 0.02, "field not at zero"
assert 1.0 <= _Ts <= 1.4, "sample not at base"
assert abs(sr1.filter_slope() - 24) < 1 and abs(sr0.filter_slope() - 24) < 1, "filter slope not 24 dB/oct"
print(f"acquisition: drive={sr1.amplitude()} V @ {sr1.frequency()} Hz, I_bias={I_BIAS:.4e} A, "
      f"tau={sr1.time_constant()} s, dwell={DWELL:.2f} s, "
      f"sr0 sens={sr0.sensitivity():.2e}, sr1 sens={sr1.sensitivity():.2e}")

# --- re-range sr1 for the CNP hunt -------------------------------------
# Committed sens 5e-5 ceilings R_xx at 5e-5/I = ~1 kohm, only 5x the metallic
# 206 ohm. This leg set is the CNP reconnaissance, so head-room matters more
# than resolution in the metallic region: 5e-4 puts the ceiling at ~10 kohm.
# Measure the noise penalty at the new range rather than assuming there is none.
sr1.sensitivity(5e-4)
interruptible_sleep(2.0)
_s = []
for _j in range(16):
    interruptible_sleep(DWELL)
    _s.append(sr1.X())
_s = np.array(_s)
_dR_new = _s.std(ddof=1) / abs(I_BIAS)
print(f"sr1 re-ranged: sens={sr1.sensitivity():.1e} V -> R_xx ceiling "
      f"{sr1.sensitivity()/abs(I_BIAS)/1e3:.1f} kohm; "
      f"load={abs(_s.mean())/sr1.sensitivity():.4f}, "
      f"R_xx={_s.mean()/I_BIAS:.2f} ohm, dR_xx={_dR_new:.3f} ohm "
      f"({_s.std(ddof=1)/abs(_s.mean()):.2%})")
print("  (a railed CNP peak still LOCATES the CNP, which is what Gate C needs;")
print("   precision R_xx at the peak comes later with a range chosen from it)")

N_PTS = 151
LOCKINS = [sr0, sr1, sr2, sr3]
LEGS = [
    (k_tg, "k_tg", TG_MAX), (k_tg, "k_tg", TG_MIN),
    (k_bg, "k_bg", BG_MAX), (k_bg, "k_bg", BG_MIN),
]

meas_config["comments"] = ("Gate C: gate-current sanity check + contact liveness + CNP "
                           "reconnaissance, B=0, V_si=0, base T")
meas_config["Si (V)"] = dc205.voltage()
meas_config["sample_temperature:"] = T_sample()

# pA-floor readback on the gate-current channels; reset in the next cell.
k_tg.nplci(10)
k_bg.nplci(10)
print(f"gate-current nplci -> tg={k_tg.nplci()}, bg={k_bg.nplci()} (pA floor; reset next cell)")

for _gate, _gname, _vend in LEGS:
    _other = k_bg if _gate is k_tg else k_tg
    _oname = "k_bg" if _gate is k_tg else "k_tg"
    print(f"\n=== leg: {_gname} 0 -> {_vend:+g} V ({N_PTS} pts, delay={DWELL:.2f} s) ===")

    s = sweep.AsyncStation(meas_config)
    s.add_comment('gate-current-sanity-check')
    s.add_comment(f'gate: {_gname}')
    s.add_comment(f'leg: 0 -> {_vend:+g} V (committed card limit)')
    s.add_comment(f'{_oname} parked at 0 V; V_si = 0 V; B = 0 T')
    s.add_comment(f'I_bias = {I_BIAS:.4e} A, drive {sr1.amplitude()} V @ {sr1.frequency()} Hz')
    s.add_comment(f'sr1 tau={sr1.time_constant()} s slope={sr1.filter_slope()} dB/oct, dwell={DWELL:.2f} s')
    s.add_comment('Gate C liveness on the provided hardwired configuration: '
                  'source T_0, drain B_3 (sr0), Rxx B_1-B_2 (sr1); sr2/sr3 n.c.')

    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)

    _xp = _gate.volt
    s.fp(_other.volt)
    s.fp(_gate.curr).fp(_other.curr)
    s.fp(T_sample).fp(T_vaporizer)
    # every live value gets a plot: both gate currents + every lock-in X
    s.plot(_xp, k_tg.curr)
    s.plot(_xp, k_bg.curr)
    for _lia in LOCKINS:
        s.fp(_lia.X).fp(_lia.P)
        s.plot(_xp, _lia.X)

    try:
        s.sweep(_gate.volt, np.linspace(0, _vend, N_PTS), delay=DWELL)
    finally:
        s.ramp(_gate.volt, 0)
        print(f"    parked {_gname} -> {_gate.volt():+.4f} V; "
              f"I_tg={k_tg.curr():.3e} A, I_bg={k_bg.curr():.3e} A")

print("\nGATE-C: all legs done")
print(f"final: V_tg={k_tg.volt():+.4f} V, V_bg={k_bg.volt():+.4f} V, V_si={dc205.voltage():+.4f} V")
