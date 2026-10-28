# === Heater block — warm-up + dwell calibration + R(T) preview at the optimum ===
# Step the heater up to the ceiling at the dome optimum (gates already here from
# Fig 1). At each step: confirm heater drawing, poll (T, R) until dT/dt settles,
# record. Outputs: (a) per-step settle time -> sets Fig-3 multimegasweep slow_delay;
# (b) heater->T re-confirmation; (c) 4T R(T) at the dome center = a free Tc preview.
# Leaves the heater at the ceiling, positioned for the descending Fig-3 ladder.
import time

# --- silent-precondition reads (optimum, B_eff0, base T, heater off) ---
B_EFF0 = -0.366e-3
T0 = temperature(); B_now = magnet.field()
Vtg = k_tg.volt(); Vbg = k_bg.volt(); Hv = heater.volt()
print(f"T = {T0*1e3:.1f} mK     (expect ~34, base)")
print(f"B = {B_now*1e3:.4f} mT  (expect B_eff0 = {B_EFF0*1e3:.3f})")
print(f"V_tg = {Vtg:.3f}      (expect -5.365, optimum n=-5.0)")
print(f"V_bg = {Vbg:.3f}      (expect +3.987)")
print(f"heater = {Hv:.3f} V    (expect 0)")
assert T0 < 0.060, f"T not at base: {T0*1e3:.1f} mK"
assert abs(B_now - B_EFF0) < 0.0015, f"B off B_eff0: {B_now*1e3:.3f} mT"
assert abs(Vtg-(-5.365)) < 0.010 and abs(Vbg-(+3.987)) < 0.010, "gates off optimum"
assert Hv < 0.01, f"heater already on: {Hv:.3f} V"

# --- AC sense (same as the dome map; 4T resolves 0..1 kOhm) ---
dc205_1.volt(0.0)
sr830_1.amplitude(0.1)          # 1 nA
sr830_2.sensitivity(0.005)
sr830_3.sensitivity(1e-4)       # 0.1 mV, 4T (30-31)
I_bias = 0.1/1e8                # 1 nA
def read_R():                   # 4T Rxx at the optimum, Ohm
    return (sr830_3.X()/100)/I_bias

# --- step up, settle-gated; record (T, R) per step ---
steps = [1.0, 2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]   # finer near the top (larger dT/V, longer settle)
POLL = 30.0           # s between (T,R) reads
MAX_DWELL = 15*60     # s cap per step
SETTLE = 1.0          # mK/min: |dT/dt| below this = settled
ladder = []
print("\nstep  Vh(V)  I_heat(A)   T(mK)   dT/dt(mK/min)  R4T(ohm)  t_settle(s)")
for sp in steps:
    s_ramp_t = time.monotonic()
    heater.volt(sp)                      # substepped at volt.step=5mV
    time.sleep(1.0)
    Ih = heater.curr()
    assert abs(Ih) > 1e-9, f"heater not drawing at {sp} V (open line?): I={Ih:.2e} A"
    Tprev = temperature(); tprev = time.monotonic(); dTdt = 9e9
    while True:
        interruptable_sleep(POLL)
        Tnow = temperature(); tnow = time.monotonic()
        dTdt = (Tnow - Tprev)*1e3 / ((tnow - tprev)/60.0)   # mK/min
        elapsed = tnow - s_ramp_t
        print(f"      {sp:4.1f}  {Ih: .3e}  {Tnow*1e3:6.1f}  {dTdt:+8.2f}        {read_R():7.2f}   {elapsed:5.0f}")
        Tprev, tprev = Tnow, tnow
        if abs(dTdt) < SETTLE or elapsed > MAX_DWELL:
            break
    ladder.append((sp, Ih, temperature(), read_R(), time.monotonic()-s_ramp_t))
    print(f"  -> step {sp:4.1f} V settled: T={temperature()*1e3:.1f} mK, R={read_R():.2f} ohm, "
          f"settle={time.monotonic()-s_ramp_t:.0f} s, |dT/dt|={abs(dTdt):.2f} mK/min")

print("\n=== heater->T ladder (this cooldown) + R(T) at optimum + settle times ===")
print("Vh(V)  T(mK)   R4T(ohm)  settle(s)")
for sp, Ih, T, R, st in ladder:
    print(f"{sp:4.1f}  {T*1e3:6.1f}  {R:7.2f}   {st:5.0f}")
print(f"\nHeater held at {heater.volt():.2f} V, T={temperature()*1e3:.1f} mK. "
      f"Positioned for descending Fig-3 R(T,n) ladder. Max settle informs slow_delay.")
