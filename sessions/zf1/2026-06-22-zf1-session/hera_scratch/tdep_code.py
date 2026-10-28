# === Run 7: T-dependence — Ic(T) bias×T map (heat up LAST) ===
# slow = heater.volt 6->0 (measure while cooling), fast = dc205 bias +/-30nA.
# Gives Ic(T) -> Tc. First heater use: stepped warm-up, per-step thermalization,
# heater.curr verified. Gates at optimum, field nominal-0, 1nA AC.
import time as _t

# --- precondition reads ---
_T = temperature(); _B = magnet.field()
print(f"probe MC T = {_T*1e3:.1f} mK (expect base)")
print(f"magnet B   = {_B*1e3:+.3f} mT (nominal-0, effective-zero region)")
assert _T < 0.060, f"T={_T*1e3:.1f} mK not at base"
assert abs(_B) < 0.010, f"|B|={_B*1e3:.2f} mT not near 0"
_pt = np.load("hera_scratch/bias_pt.npz"); VTG_OPT=float(_pt["vtg"]); VBG_OPT=float(_pt["vbg"])

sr830_1.amplitude(0.1)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
meas_config["lockin_freq_1"]  = sr830_1.frequency()
meas_config["comment"] = "Run7 T-dep Ic(T): heater 6->0V, dc205 +/-30nA, opt n=-4.65e11/D=-0.65, B~0"
sr830_2.sensitivity(0.1); sr830_3.sensitivity(2e-4); sr830_3.time_constant(0.3)

Vdc_fast = np.linspace(-3.0, 3.0, 63)         # Idc +/-30nA, step <0.1V (no DC205 10s settle)
h_down   = np.linspace(6.0, 0.0, 11)          # heater V, measure while cooling

s = sweep.AsyncStation(meas_config)
s.add_comment('temperature-dependence')
s.add_comment('Run7 Ic(T): slow heater 6->0V (measure cooling), fast dc205 +/-30nA at SC optimum')
s.add_comment('axis: heater 0-6V; (Vtg,Vbg)=(-5.4443,+4.0529) n=-4.65e11 D=-0.65; B~0; 1nA AC')

# set operating point + zero bias
s.ramp(k_tg.volt, VTG_OPT); s.ramp(k_bg.volt, VBG_OPT); s.ramp(dc205_1.volt, 0.0)

s.fp(temperature)
s.fp(heater.volt).fp(heater.curr)
s.fp(magnet.field)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
s.fp(dc205_1.volt)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

s.plot(dc205_1.volt, sr830_3.X)

# --- stepped warm-up to 6V (<=1V steps, holds), then equilibrate (device-card rule) ---
for hv in (1.0, 2.0, 3.0, 4.0, 5.0, 6.0):
    s.ramp(heater.volt, hv); _t.sleep(60)
_t.sleep(300)
print(f"warmed: heater.volt={heater.volt():.2f} V, heater.curr={heater.curr()*1e6:.2f} uA, T={temperature()*1e3:.0f} mK")
assert abs(heater.curr()) > 1e-7, "heater drawing ~no current — open line? abort"

try:
    s.megasweep(heater.volt, h_down,
                dc205_1.volt, Vdc_fast,
                slow_delay=300, fast_delay=1)
finally:
    s.ramp(heater.volt, 0.0)      # start re-cool
    s.ramp(dc205_1.volt, 0.0)
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
