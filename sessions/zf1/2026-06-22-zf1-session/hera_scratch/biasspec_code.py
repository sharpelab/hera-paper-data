# === Run 5: bias spectroscopy (dV/dI vs Idc) at the SC candidate optimum ===
# Gates fixed at n=-4.65e11, D=-0.65 (Vtg=-5.444, Vbg=+4.053). DC bias swept
# +/-15V (=+/-150nA via 100MOhm), step <=0.1V to avoid the DC205 10s settle.
# Looking for a critical-current lobe: dV/dI~0 below Ic, rising at Ic.

# --- precondition reads ---
_T = temperature(); _B = magnet.field()
print(f"probe MC T = {_T*1e3:.1f} mK   (expect base)")
print(f"magnet B   = {_B*1e3:+.3f} mT  (expect ~0 nominal)")
assert _T < 0.060, f"T={_T*1e3:.1f} mK not at base"
assert abs(_B) < 0.005, f"|B|={_B*1e3:.2f} mT not ~nominal-0"

_pt = np.load("hera_scratch/bias_pt.npz"); VTG_OPT=float(_pt["vtg"]); VBG_OPT=float(_pt["vbg"])
print(f"optimum gates: Vtg={VTG_OPT:+.4f} Vbg={VBG_OPT:+.4f}")
assert -7.0<=VTG_OPT<=6.0 and -4.0<=VBG_OPT<=4.2, "optimum out of validator box"

sr830_1.amplitude(0.1)                       # 1 nA AC sense (<< expected Ic)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
meas_config["lockin_freq_1"]  = sr830_1.frequency()
meas_config["comment"] = "Run5 bias-spec: dV/dI vs Idc at n=-4.65e11/D=-0.65, Idc +/-150nA, 1nA AC, B=0"

sr830_2.sensitivity(0.1); sr830_3.sensitivity(2e-4); sr830_3.time_constant(0.3)

Vdc_vec = np.linspace(-15.0, 15.0, 305)      # step ~0.0987V (<0.1 -> no 10s DC205 settle); Idc=Vdc/1e8
print(f"DC bias: {len(Vdc_vec)} pts, Idc {Vdc_vec[0]/1e8*1e9:+.0f}..{Vdc_vec[-1]/1e8*1e9:+.0f} nA, step {abs(Vdc_vec[1]-Vdc_vec[0]):.4f} V")

s = sweep.AsyncStation(meas_config)
s.add_comment('bias-spectroscopy')
s.add_comment('Run5 dV/dI vs Idc point check at SC candidate optimum')
s.add_comment('gates: Vtg=-5.444 Vbg=+4.053 (n=-4.65e11, D=-0.65); Idc +/-150nA; 1nA AC; B=0')

# ramp gates to optimum, settle; start DC at one extreme
s.ramp(k_tg.volt, VTG_OPT)
s.ramp(k_bg.volt, VBG_OPT)
s.ramp(dc205_1.volt, float(Vdc_vec[0]))
print(f"gates set: Vtg={k_tg.volt():+.4f} Vbg={k_bg.volt():+.4f}")

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(dc205_1.volt)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

s.plot(dc205_1.volt, sr830_3.X)   # dV/dI vs Idc (4T)

try:
    s.sweep(dc205_1.volt, Vdc_vec, delay=1.5)
finally:
    s.ramp(dc205_1.volt, 0.0)     # device-card rule: dc205 -> 0 before ending
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
