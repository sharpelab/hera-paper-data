# Fraunhofer (Ic vs B_perp) at the SC arc minimum — base-T phase-coherence read.
# dV/dI vs (I_dc, B) at n=-5.02e11, D=-0.673. Looks for Ic modulation/lobes
# (Josephson) and pins the effective-zero (max Ic). B_c_perp~2.5 mT so the dome
# closes by ~few mT -> fine B steps, +/-3 mT. FIELD DISCIPLINE: two one-sided
# halves (+3->0, -3->0) meeting at 0; never increase |B| through 0 in a sweep.
# AC 0.5 nA (low, don't wash lobes). Recipe: fraunhofer.md.
import numpy as np, time

T=temperature(); B=magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  rate={magnet.ramp_rate()} T/s")
assert T<0.08, f"T not base {T*1e3:.1f} mK"

sr830_1.amplitude(0.05)                 # 0.5 nA AC
for sr in (sr830_1,sr830_3): sr.time_constant(0.3)
sr830_1.sensitivity(1e-3); sr830_3.sensitivity(2e-5)

Vdc=np.linspace(-1.2,1.2,49)            # +/-12 nA fast axis (0.5 nA step)
mc=dict(meas_config); mc["bias_voltage_1"]=sr830_1.amplitude()
mc["comment"]="Fraunhofer Ic vs Bperp at SC arc min n=-5.02e11 D=-0.673; dV/dI(Idc,B), Iac0.5nA, +/-3mT two halves"
s=sweep.AsyncStation(mc)
s.add_comment('fraunhofer')
s.add_comment('Ic vs Bperp at SC arc min n=-5.02e11 D=-0.673, base T')
s.ramp(dc205_1.volt,0.0)
s.ramp(k_tg.volt,-5.640); s.ramp(k_bg.volt,4.200); time.sleep(5)
s.fp(temperature).fp(fridge_temperature).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr830_1.X).fp(sr830_1.P).fp(sr830_3.X).fp(sr830_3.P)
s.plot(dc205_1.volt, sr830_3.X)

# Half 1: B +3mT -> 0 (slow), DC bias fast
s.ramp(magnet.field, 0.003); time.sleep(45)
s.megasweep(magnet.field, np.linspace(0.003,0.0,13), dc205_1.volt, Vdc, slow_delay=3, fast_delay=1)
# Half 2: B -3mT -> 0
s.ramp(dc205_1.volt,0.0)
s.ramp(magnet.field, -0.003); time.sleep(45)
s.megasweep(magnet.field, np.linspace(-0.003,0.0,13), dc205_1.volt, Vdc, slow_delay=3, fast_delay=1)

s.ramp(dc205_1.volt,0.0); s.ramp(magnet.field,0.0)
