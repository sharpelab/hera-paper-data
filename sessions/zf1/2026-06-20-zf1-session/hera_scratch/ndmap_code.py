import numpy as np
import time
from sweep import raster
from sharpelab_nb.gates import calculate_gate_voltages

# --- preconditions ---
T = temperature(); B = magnet.field()
print(f"precond: T={T*1e3:.1f} mK ; B={B*1e3:.4f} mT (nominal zero; ~2 mT trapped) ; "
      f"k_tg={k_tg.volt():+.3f} k_bg={k_bg.volt():+.3f}")
assert T < 0.1, f"T not at base: {T} K"
assert abs(B) < 0.005, f"field not pristine: {B} T"
sr830_1.amplitude(0.05); meas_config["bias_voltage_1"] = sr830_1.amplitude()
assert abs(sr830_1.amplitude()-0.05) < 1e-4, "drive not 0.5 nA"
k_tg.nplci(1); k_bg.nplci(1)

# --- rasterized (n,D) box around the dip; n[e12 cm^-2], D[V/nm] ---
DTG, DBG, EP = 23.6, 20.0, 3.0       # device hBN thicknesses (nm) + kappa (device card)
N_LO, N_HI = -0.63, -0.28
D_LO, D_HI = -0.67, -0.50            # negative-D edge capped by Vbg<=4.2
NX, NY = 71, 35                       # ~0.005 e12 x ~0.005 V/nm
verts = np.array([[N_LO,D_LO],[N_HI,D_LO],[N_HI,D_HI],[N_LO,D_HI],[N_LO,D_LO]])
ns, Ds = raster.rasterize(verts, NX, NY, 0)
vtg_vec, vbg_vec = calculate_gate_voltages(ns, Ds, dtg=DTG, dbg=DBG, ep=EP)
vtg_new, vbg_new = sanitize_tg_bg(vtg_vec, vbg_vec, tg_lims, bg_lims)
print(f"raster {len(ns)} pts -> in-validator {len(vtg_new)} (clipped {len(ns)-len(vtg_new)}, "
      f"{100*(1-len(vtg_new)/len(ns)):.1f}%)")
print(f"gate extent: Vtg {vtg_new.min():.3f}..{vtg_new.max():.3f} ; Vbg {vbg_new.min():.3f}..{vbg_new.max():.3f}")

meas_config["comment"] = (
    "nD-map SC-extent zoom @ run-5 dip (n=-0.465e12, D=-0.65 V/nm); "
    "n[-0.63,-0.28] x D[-0.67,-0.50], 71x35 raster; Rxx=sr2 (+sr3 marker); 0.5 nA; B~0 nominal"
)
s = sweep.AsyncStation(meas_config)
s.add_comment('nD-map')
s.add_comment('SC-extent zoom @ dip; n[-0.63,-0.28]e12 x D[-0.67,-0.50]V/nm; 71x35; B~0 nominal; 0.5 nA; sr2+sr3')

s.ramp(k_tg.volt, vtg_new[0])
s.ramp(k_bg.volt, vbg_new[0])
time.sleep(10)

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)
s.plot(k_bg.volt, k_bg.curr)
s.plot('time', k_tg.curr)
s.plot(k_bg.volt, sr830_2.X)   # 4T Rxx
s.plot(k_bg.volt, sr830_3.X)   # sharp marker

try:
    s.multisweep([k_tg.volt, k_bg.volt], [vtg_new, vbg_new], delay=1.2)
finally:
    s.ramp(k_tg.volt, 0)
    s.ramp(k_bg.volt, 0)
