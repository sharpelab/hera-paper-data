import numpy as np
import time

# --- preconditions ---
T = temperature()
print(f"precond: T={T*1e3:.1f} mK ; B now={magnet.field()*1e3:.4f} mT ; ramp_rate={magnet.ramp_rate()} T/s")
print(f"precond: k_tg={k_tg.volt():+.3f} k_bg={k_bg.volt():+.3f} V")
assert T < 0.1, f"T not at base: {T} K"

# AC excitation 0.5 nA (clean MR for true-zero; re-probe any dip at lower AC)
sr830_1.amplitude(0.05); meas_config["bias_voltage_1"] = sr830_1.amplitude()

TG_OP, BG_OP = -4.79, 1.06       # n~-2.5e12 cm^-2, D~-0.4 V/nm (moderate hole, finite D)
B_EXT = 0.008                    # 8 mT extreme; <<100 mT cap
nB = 41                          # 0.2 mT steps per segment
k_tg.nplci(1); k_bg.nplci(1)

meas_config["comment"] = (
    f"effective-zero-field cal @ (Vtg={TG_OP},Vbg={BG_OP}; n~-2.5e12, D~-0.4); "
    f"two one-sided B-sweeps +/-8mT->0; trapped-flux ~2mT; Rxx=sr2(4T); AC 0.5 nA"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('field-sweep-1d')
s.add_comment(f'eff-zero-field cal; (Vtg,Vbg)=({TG_OP},{BG_OP}) n=-2.5e12 D=-0.4; one-sided -8/+8mT->0; trapped-flux search')

# gates to operating point (DC bias source already at 0)
s.ramp(k_tg.volt, TG_OP)
s.ramp(k_bg.volt, BG_OP)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)
s.plot(magnet.field, sr830_2.X)   # live MR = 4T Rxx vs B
s.plot('time', k_tg.curr)

# --- segment A: ramp to -8 mT (away from 0), settle, measure-sweep -8 -> 0 ---
s.ramp(magnet.field, -B_EXT)
time.sleep(60)                    # post-ramp thermal settle (first field excursion; monitor T)
s.sweep(magnet.field, np.linspace(-B_EXT, 0.0, nB), delay=1)

# --- segment B: ramp to +8 mT (ramp only, not measured), settle, measure-sweep +8 -> 0 ---
s.ramp(magnet.field, +B_EXT)
time.sleep(60)
s.sweep(magnet.field, np.linspace(+B_EXT, 0.0, nB), delay=1)

# leave magnet at 0 (segment B ends there); gates stay at op point for the follow-up
print("done; magnet at", magnet.field(), "T")
