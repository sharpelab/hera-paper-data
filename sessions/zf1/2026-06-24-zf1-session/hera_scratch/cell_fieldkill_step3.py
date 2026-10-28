# === Step 3: field response (B_perp field-kill) at the candidate ===
# sc-characterization Step 3: does a small B_perp quench the zero-bias dip while
# the normal state stays ~unchanged? Rxx(B) at n=-0.55e12 cm^-2, D=-0.60 V/nm,
# ZERO DC bias, AC 1 nA. FIRST magnet move of the session (ends pristine era).
# Field discipline (brief): position at +|B|max, settle, sweep one-sided DOWN to
# 0 — never increase |B| through 0 in a measurement.
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

# --- preconditions ---
print("T:", temperature(), "B:", magnet.field(), "gates:", k_tg.volt(), k_bg.volt(),
      "dc205_1:", dc205_1.volt())
assert temperature() < 0.060, "not at base T"
assert abs(dc205_1.volt()) < 1e-6, "DC bias not at 0"

c_tg = stack_capacitance([(23.6,3)]); c_bg = c_tg*1.1833
n_off = -calc_nD(0.1634,0.0,c_tg,c_bg)[0]
Vtg_arr, Vbg_arr = calc_gate_voltages(np.array([-0.55]), np.array([-0.6]), c_tg, c_bg, n_offset=n_off)
Vtg_op, Vbg_op = float(Vtg_arr[0]), float(Vbg_arr[0])
print("operating point: Vtg=%.3f Vbg=%.3f" % (Vtg_op, Vbg_op))

sr830_1.amplitude(0.1)            # AC 1 nA
sr830_3.sensitivity(2e-5)         # dV/dI up to ~200 ohm; resolves dip (~7) -> normal (~50)
B_MAX = 0.05                      # T (50 mT; well within 100 mT cap)

s = sweep.AsyncStation(meas_config)
s.add_comment('field-sweep-1d')
s.add_comment('Step3 field-kill at candidate n=-0.55e12 cm^-2, D=-0.60 V/nm (zero DC bias)')
s.add_comment(f'(Vtg, Vbg) = ({Vtg_op:.3f}, {Vbg_op:.3f}); B {B_MAX*1e3:.0f} mT -> 0, one-sided toward 0; AC 1 nA')

# position: gates to candidate, DC bias 0, then magnet UP to +B_MAX
s.ramp(dc205_1.volt, 0)
s.ramp(k_tg.volt, Vtg_op)
s.ramp(k_bg.volt, Vbg_op)
s.ramp(magnet.field, B_MAX)       # 0 -> +50 mT at 1 mT/s (~50 s)
interruptable_sleep(120)          # first-ramp thermal settle
print("after settle: T =", temperature(), "K  B =", magnet.field(), "T")

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(magnet.field)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)
s.plot(magnet.field, sr830_3.X)   # Rxx vs B (the field-kill trace)
s.plot('time', k_tg.curr)         # leakage

# one-sided sweep DOWN to 0 (toward zero), fine steps
s.sweep(magnet.field, np.linspace(B_MAX, 0.0, 101), delay=1)

# park: magnet already at 0; gates to 0
s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)
