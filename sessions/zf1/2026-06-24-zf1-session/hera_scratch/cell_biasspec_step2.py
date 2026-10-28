# === Step 2: bias spectroscopy (dV/dI vs I_dc) at the candidate ===
# sc-characterization Step 2 / bias-spectroscopy point-check. Decisive SC test:
# dV/dI ~ 0 for |I_dc| < Ic, rising at a critical current = supercurrent.
# Candidate from Step-1 linecuts: n=-0.55e12 cm^-2, D=-0.60 V/nm (Vtg=-5.03,
# Vbg=3.73) — the +/-D-asymmetric Rxx dip to ~6 ohm.
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

# --- preconditions (field pristine; DC bias starts from 0) ---
print("T:", temperature(), "B:", magnet.field(), "gates:", k_tg.volt(), k_bg.volt(),
      "dc205_1:", dc205_1.volt())
assert temperature() < 0.060, "not at base T"
assert abs(magnet.field()) < 0.005, "field not near zero"
assert abs(dc205_1.volt()) < 1e-6, "DC bias not at 0"

c_tg = stack_capacitance([(23.6,3)]); c_bg = c_tg*1.1833
n_off = -calc_nD(0.1634,0.0,c_tg,c_bg)[0]
Vtg_arr, Vbg_arr = calc_gate_voltages(np.array([-0.55]), np.array([-0.6]), c_tg, c_bg, n_offset=n_off)
Vtg_op, Vbg_op = float(Vtg_arr[0]), float(Vbg_arr[0])
print("operating point: Vtg=%.3f Vbg=%.3f" % (Vtg_op, Vbg_op))

# AC excitation 1 nA (0.1 V / 100 MOhm); DC bias via dc205_1 / 100 MOhm: +/-15 V -> +/-150 nA
sr830_1.amplitude(0.1)
sr830_3.sensitivity(2e-5)              # dV/dI up to ~200 ohm @1nA, gain 100; resolves SC near-zero
R_BIAS = 1e8

# round-trip bias sweep, symmetric across 0 (must cross I_dc=0 — this is current, not field)
fwd = np.linspace(-15, 15, 121)
bwd = np.linspace(15, -15, 121)
Vdc = np.hstack((fwd, bwd))             # I_dc = Vdc / R_BIAS -> +/-150 nA

s = sweep.AsyncStation(meas_config)
s.add_comment('bias-spectroscopy')
s.add_comment('Step2 point-check at candidate n=-0.55e12 cm^-2, D=-0.60 V/nm')
s.add_comment(f'Vtg={Vtg_op:.3f} Vbg={Vbg_op:.3f}; Idc +/-150 nA (Vdc +/-15 V / 100 MOhm); AC 1 nA; round-trip')

# ramp gates to the operating point, settle
s.ramp(k_tg.volt, Vtg_op)
s.ramp(k_bg.volt, Vbg_op)
interruptable_sleep(10)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(dc205_1.volt)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)
s.plot(dc205_1.volt, sr830_3.X)        # dV/dI (4T) vs DC bias
s.plot(dc205_1.volt, sr830_1.X)        # AC current monitor

s.sweep(dc205_1.volt, Vdc, delay=1.5)  # 5 x TC settle

# park DC bias to 0 first (device card), then gates
s.ramp(dc205_1.volt, 0)
s.ramp(k_tg.volt, 0)
s.ramp(k_bg.volt, 0)
