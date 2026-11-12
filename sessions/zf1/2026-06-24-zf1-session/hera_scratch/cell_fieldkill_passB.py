# === Step 3 (cont): field-kill PASS B — negative-controller side ===
# Pass A (+50->0) showed only the high-field shoulder: Rxx 43->36 ohm, no dip at
# controller-0. The 50 mT excursion left ~10 mT remanence (rig card: set by going
# to finite field, NOT flipped by direction reversal), so TRUE B=0 (the SC's field
# maximum) is at NEGATIVE controller field. This pass crosses it: position at
# -50 mT, settle, sweep one-sided UP to 0. Expect the ~7 ohm dip near controller
# ~-8 mT = effective zero, with Rxx rising on both sides (the field-kill).
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

print("T:", temperature(), "B:", magnet.field(), "gates:", k_tg.volt(), k_bg.volt(),
      "dc205_1:", dc205_1.volt())
assert temperature() < 0.060, "not at base T"
assert abs(dc205_1.volt()) < 1e-6, "DC bias not at 0"

c_tg = stack_capacitance([(23.6,3)]); c_bg = c_tg*1.1833
n_off = -calc_nD(0.1634,0.0,c_tg,c_bg)[0]
Vtg_arr, Vbg_arr = calc_gate_voltages(np.array([-0.55]), np.array([-0.6]), c_tg, c_bg, n_offset=n_off)
Vtg_op, Vbg_op = float(Vtg_arr[0]), float(Vbg_arr[0])

sr830_1.amplitude(0.1)
sr830_3.sensitivity(2e-5)
B_MIN = -0.05                       # T (-50 mT)

s = sweep.AsyncStation(meas_config)
s.add_comment('field-sweep-1d')
s.add_comment('Step3 field-kill PASS B (neg side) at candidate n=-0.55, D=-0.60 (zero DC bias)')
s.add_comment(f'(Vtg, Vbg) = ({Vtg_op:.3f}, {Vbg_op:.3f}); B {B_MIN*1e3:.0f} mT -> 0, one-sided toward 0; locate effective zero')

s.ramp(dc205_1.volt, 0)
s.ramp(k_tg.volt, Vtg_op)
s.ramp(k_bg.volt, Vbg_op)
s.ramp(magnet.field, B_MIN)        # 0 -> -50 mT (~50 s); does not cross 0
interruptable_sleep(120)
print("after settle: T =", temperature(), "K  B =", magnet.field(), "T")

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(magnet.field)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)
s.plot(magnet.field, sr830_3.X)
s.plot('time', k_tg.curr)

s.sweep(magnet.field, np.linspace(B_MIN, 0.0, 101), delay=1)   # -50 -> 0, toward zero

s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)
