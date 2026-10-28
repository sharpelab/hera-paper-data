# === Run 6: field response (B_perp kill / B_c) at the SC optimum ===
# First magnet energization this session. One-sided sweep +80mT -> 0 (toward 0,
# never crossing). 1nA AC, zero DC bias, at n=-4.65e11/D=-0.65. Field discipline:
# settle after positioning ramp; record measured field; T fp'd to derive settle.

# --- precondition reads ---
_T = temperature(); _B = magnet.field(); _rr = magnet.ramp_rate()
print(f"probe MC T = {_T*1e3:.1f} mK   (expect base)")
print(f"magnet B   = {_B*1e3:+.3f} mT  (expect ~0 start)")
print(f"magnet ramp_rate = {_rr} T/s")
assert _T < 0.060, f"T={_T*1e3:.1f} mK not at base"
assert abs(_B) < 0.005, f"|B|={_B*1e3:.2f} mT not ~0 at start"

_pt = np.load("hera_scratch/bias_pt.npz"); VTG_OPT=float(_pt["vtg"]); VBG_OPT=float(_pt["vbg"])
assert -7.0<=VTG_OPT<=6.0 and -4.0<=VBG_OPT<=4.2

sr830_1.amplitude(0.1)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
meas_config["lockin_freq_1"]  = sr830_1.frequency()
meas_config["comment"] = "Run6 field-kill: Rxx(B) +80mT->0 at n=-4.65e11/D=-0.65, 1nA AC, Vdc=0"
sr830_2.sensitivity(0.1); sr830_3.sensitivity(2e-4); sr830_3.time_constant(0.3)

s = sweep.AsyncStation(meas_config)
s.add_comment('field-sweep-1d')
s.add_comment('Run6 field-kill at SC optimum: Rxx(B) +80mT->0, 1nA AC, Vdc=0')
s.add_comment('label: (Vtg, Vbg) = (-5.4443, +4.0529); n=-4.65e11, D=-0.65')

# set operating point, zero DC bias
s.ramp(k_tg.volt, VTG_OPT)
s.ramp(k_bg.volt, VBG_OPT)
s.ramp(dc205_1.volt, 0.0)

s.fp(temperature)
s.fp(magnet.field)                  # measured field readback (vs setpoint axis)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

s.plot(magnet.field, sr830_3.X)     # live Rxx(B)
s.plot('time', k_tg.curr)

# position to +80 mT (blocks until holding), settle, verify T, then sweep toward 0
magnet.field(0.080)
import time as _t; _t.sleep(120)
print(f"after +80mT ramp + 120s settle: T = {temperature()*1e3:.1f} mK, B = {magnet.field()*1e3:+.2f} mT")

try:
    s.sweep(magnet.field, np.linspace(0.080, 0.0, 161), delay=1)
finally:
    magnet.field(0.0)
    s.ramp(dc205_1.volt, 0.0)
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
