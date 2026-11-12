# === Gate C — cheap liveness check (first-session branch, gate-current-sanity-check) ===
# Confirms: (1) device passes lock-in current, (2) provided contacts read clean,
# (3) the 4T longitudinal Rxx channel (sr3 = 30-31) is live, (4) no gate leakage at
# the operating point. Validators are ALREADY committed from the device card
# (SAFETIES, cell 16) -> liveness only, NOT the iterate-then-bless range loop.

# --- precondition reads (silent state this cell assumes but does not set) ---
_T = temperature()
_B = magnet.field()
print(f"probe MC T = {_T*1e3:.1f} mK   (expect base, mK range)")
print(f"magnet B   = {_B*1e3:+.3f} mT  (expect ~0)")
print(f"k_tg.volt  = {k_tg.volt():+.4f} V    k_bg.volt = {k_bg.volt():+.4f} V    (cell parks both to 0)")
assert _T < 0.060, f"T={_T*1e3:.1f} mK not at base"
assert abs(_B) < 0.005, f"|B|={_B*1e3:.2f} mT not ~0"

# AC sense drive -> ~1 nA at the device (device card: 0.1 V over the 100 MOhm bias R)
sr830_1.amplitude(0.1)

# nplci=10 on the gate-current channels for pA-floor leakage readback; reset to 1 in finally.
k_tg.nplci(10)
k_bg.nplci(10)

meas_config["comment"] = "Gate C liveness: k_tg 0->+1V, k_bg=0, 1nA AC, B=0"

gate       = k_tg
v_endpoint = +1.0        # small excursion, deep inside the +6 V validator
n_pts      = 51
delay      = 1           # s
lockins    = [sr830_1, sr830_2, sr830_3]   # current + 2T + 4T-longitudinal, per meas_config

s = sweep.AsyncStation(meas_config)
s.add_comment('gate-current-sanity-check')
s.add_comment('branch: cheap-liveness (validators pre-committed from device card)')
s.add_comment(f'gate: {gate.name}  leg: 0 -> {v_endpoint:+g} V  (k_bg parked 0)')

s.ramp(k_bg.volt, 0)
s.ramp(k_tg.volt, 0)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in lockins:
    s.fp(lia.X).fp(lia.P)

xp = gate.volt
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
for lia in lockins:
    s.plot(xp, lia.X)

try:
    s.sweep(gate.volt, np.linspace(0, v_endpoint, n_pts), delay=delay)
finally:
    s.ramp(gate.volt, 0)
    k_tg.nplci(1)
    k_bg.nplci(1)
