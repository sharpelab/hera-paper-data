# Tc / I_c(T) ladder at the SC arc minimum (n=-5.02e11, D=-0.673, B=0) — the
# final constellation piece. Flavor B (temperature-dependence.md): warm to the
# top, step the heater DOWN (measure while cooling), dV/dI vs I_dc at each T.
# SC tell: the zero-bias dip / I_c collapses as T -> Tc. Heater per device card
# (<=6.5 V sustained -> ~480 mK). T is read back from data, never the setpoint.
import numpy as np, time

T0=temperature(); B=magnet.field()
print(f"T={T0*1e3:.1f} mK  B={B*1e3:.3f} mT  heater={heater.volt()} V")
assert abs(B)<0.01, f"B not ~0: {B*1e3:.3f} mT"

sr830_1.amplitude(0.05)                      # 0.5 nA AC
for sr in (sr830_1,sr830_3): sr.time_constant(0.3)
sr830_1.sensitivity(1e-3); sr830_3.sensitivity(2e-5)

Vdc=np.linspace(-1.5,1.5,61)                  # +/-15 nA
mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
s=sweep.AsyncStation(mc)
s.add_comment('temperature-dependence')
s.add_comment('Ic(T) ladder at SC arc min n=-5.02e11 D=-0.673, B=0 (heater down-ladder)')
s.ramp(dc205_1.volt,0.0); s.ramp(k_tg.volt,-5.640); s.ramp(k_bg.volt,4.200)
s.fp(temperature).fp(fridge_temperature).fp(heater.volt).fp(heater.curr)
s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_3.X).fp(sr830_3.P)
s.plot(dc205_1.volt, sr830_3.X)

for hv in [6.5, 5.5, 4.5, 3.5, 2.5, 1.5, 0.5, 0.0]:    # warm top -> base
    s.ramp(heater.volt, hv); time.sleep(1)
    ic=heater.curr()                                    # open-line check (recipe)
    time.sleep(8*60)                                    # thermalize (read T from data)
    Tnow=temperature()
    print(f"heater={hv:.1f} V  I_heat={ic:.2e} A  T={Tnow*1e3:.0f} mK")
    s.ramp(dc205_1.volt, -1.5)
    s.sweep(dc205_1.volt, Vdc, delay=1.0)               # one file per T
    s.ramp(dc205_1.volt, 0.0)

heater.volt(0.0)                                        # back toward base (re-cool ~1 h)
