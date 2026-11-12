# === Step 1: pristine-field gate map (axis-aligned raw V_tg / V_bg) ===
# sc-characterization Step 1: Rxx(V_tg, V_bg) at PRISTINE field, BEFORE energising
# the magnet. Double duty -> (a) coarse overview to locate low-Rxx candidate
# regions, (b) CNP-ridge slope for cap-ratio calibration (geometry is a prior).
# Coarse survey over the FULL validator box; zoom into candidates afterward.

# --- preconditions (this cell assumes; it does NOT touch the field) ---
print("T        :", temperature(), "K  (expect base ~0.03)")
print("B        :", magnet.field(), "T  (pristine - controller NOT ramped here)")
print("gates    :", k_tg.volt(), k_bg.volt(), "V")
print("I_bias   :", meas_config["bias_voltage_1"] / meas_config["bias_resistor"], "A")
assert temperature() < 0.060, "not at base T"
assert abs(magnet.field()) < 0.005, "field not near zero - map must be pristine-field"

# 4T channel sensitivity: resolve up to ~50 kOhm (sens >= R_max * I_ac * G;
# 5 mV / 100 gain / 1 nA = 50 kOhm). Clips only at a strongly gapped CNP, where
# the railed ridge still locates the CNP line for cap-ratio. Others left as-is
# (sr830_2 0.1 V -> ~1 MOhm 2T; sr830_1 1 mV current).
sr830_3.sensitivity(5e-3)

V_tg = np.linspace(-7.0, 6.0, 81)    # slow axis
V_bg = np.linspace(-4.0, 4.2, 69)    # fast axis

s = sweep.AsyncStation(meas_config)
s.add_comment('gatemap')
s.add_comment('Step1 pristine-field survey: full validator box; cap-ratio + candidate overview')
s.add_comment(f'B_pristine = {magnet.field():.3e} T (controller untouched)')
s.add_comment(f'grid: V_tg[{V_tg[0]:+g},{V_tg[-1]:+g}] x {len(V_tg)} slow, '
              f'V_bg[{V_bg[0]:+g},{V_bg[-1]:+g}] x {len(V_bg)} fast; sd=1.5 fd=0.5')

# ramp to the start corner, settle
s.ramp(k_tg.volt, V_tg[0])
s.ramp(k_bg.volt, V_bg[0])
interruptable_sleep(10)

# record
s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

# live monitors: leakage (both gates) + 4T Rxx + current
s.plot(k_bg.volt, k_bg.curr)     # fast-gate leakage vs fast axis
s.plot('time', k_tg.curr)        # slow-gate leakage over time
s.plot(k_bg.volt, sr830_3.X)     # 4T Rxx (30-31)
s.plot(k_bg.volt, sr830_1.X)     # current channel (should stay ~1 nA flat)

s.megasweep(k_tg.volt, V_tg, k_bg.volt, V_bg, slow_delay=1.5, fast_delay=0.5)

# park gates (leave field alone)
s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)
