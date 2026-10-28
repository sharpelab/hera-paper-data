# === 0 T gate map (gatemap): full validator box, 101x101 ===
# BG slow -4.5 -> +4.5 (101 rows), TG fast -3 -> +3 (101 pts, 60 mV steps).
# Feeds cnp-and-dline-calibration (investigation step 1).

# -- preconditions (assumed, not set by this cell)
B = magnet.field()
Ts = T_sample()
print(f"precheck: B={B:+.4f} T (expect ~0), T_sample={Ts:.3f} K (expect ~1.2)")
assert abs(B) < 0.05, f"STOP: field not at zero: {B} T"
assert Ts < 1.5, f"STOP: sample not at base: {Ts} K"

# -- drive + sensitivities for the CNP-scale map (device-card starting points,
#    tuned to what gate C measured: R ~ 1-3 kOhm near (0,0), tens of Ohm metallic)
sr1.amplitude(0.5)          # 0.5 V / 100 MOhm = 5 nA bias
for lia in (sr1, sr2, sr3):
    lia.sensitivity(2e-4)   # ceiling R = 2e-4/5nA = 40 kOhm; quantization ~1.2 Ohm
sr0.sensitivity(1e-2)       # drain: 5 nA x 1e6 V/A = 5 mV signal on 10 mV sens
print(f"drive {sr1.amplitude()} V -> 5 nA; sens sr1/sr2/sr3 = 2e-4, sr0 = 1e-2")

meas_config["comments"] = (
    "gatemap: 0 T, TG fast [-3,+3] 101 pts x BG slow [-4.5,+4.5] 101 rows, "
    "Si 0 V; drive 0.5 V / 100 MOhm = 5 nA @ 13 Hz; fast_delay 1 s, slow_delay 3 s"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('first map of cooldown: full validator box, feeds cnp-and-dline-calibration')

# park at start corner and settle
s.ramp(k_2400_tg.volt, -3.0)
s.ramp(k_2400_bg.volt, -4.5)
interruptible_sleep(10)

xp = k_2400_tg.volt
s.fp(k_2400_tg.volt).fp(k_2400_tg.curr)
s.fp(k_2400_bg.volt).fp(k_2400_bg.curr)
s.fp(T_sample)
s.plot(xp, k_2400_tg.curr)
s.plot(xp, k_2400_bg.curr)
s.plot(xp, T_sample)
for lia in (sr0, sr1, sr2, sr3):
    s.fp(lia.X).fp(lia.P)
    s.plot(xp, lia.X)

try:
    s.megasweep(
        k_2400_bg.volt, np.linspace(-4.5, 4.5, 101),
        k_2400_tg.volt, np.linspace(-3.0, 3.0, 101),
        slow_delay=3, fast_delay=1,
    )
finally:
    s.ramp(k_2400_tg.volt, 0)
    s.ramp(k_2400_bg.volt, 0)

print("gatemap complete; gates parked at 0")
