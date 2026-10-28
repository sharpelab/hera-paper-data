# === Step 3 — go/no-go fixed-(n,D=0) B-sweep (field-sweep-1d) ===
# trilayer-stacking-fs-count Step 3: confirm SdH is present and whether a
# small second (ML) tone is resolvable on THIS device before committing to a
# full fan. Hole side, high |n| (ML tone grows with |n|), D=0 (ML survives
# only at small D). Non-uniform B: dense at low field where the ML periods
# accumulate, coarse at high field for the BL tone.

import numpy as np

# --- (n,D) calibration from file_id 1 (cnp-and-dline-calibration) ---
# ratio data-calibrated (c_bg/c_tg=1.298); absolute scale = geometry prior
# (c_tg from 15.6 nm hBN), pending QH lever-arm upgrade.
import scipy.constants as cst
C_TG = cst.epsilon_0*3.0/15.6e-9          # anchored to stack prior
C_BG = 1.298*C_TG                         # from fitted CNP slope
N_OFF = -7.095e14                         # m^-2 (CNP intercept +0.067 V @ Vbg=0)
def gates_for(n_cm2, D=0.0):              # n in cm^-2 -> (Vtg,Vbg) at given D (V/nm units of calc_nD)
    n_m2 = n_cm2*1e4
    a = (n_m2 - N_OFF)*cst.e              # = C_TG*Vtg + C_BG*Vbg
    b = 2.0*D*cst.epsilon_0              # = C_TG*Vtg - C_BG*Vbg  (D_off=0)
    Vtg = (a+b)/(2*C_TG); Vbg = (a-b)/(2*C_BG)
    return Vtg, Vbg

n_target = -4.0e12
Vtg, Vbg = gates_for(n_target, 0.0)
print(f"target n={n_target:.2e} cm^-2, D=0 -> Vtg={Vtg:.4f} V, Vbg={Vbg:.4f} V")
assert -6.0 <= Vtg <= 7.0 and -4.5 <= Vbg <= 4.5, "gate target out of validators"

# --- Preconditions ---
assert abs(magnet.mag()) < 0.05, f"field not ~0 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
print("pre: B =", magnet.mag(), "T ;  T =", heater.sample_temperature(),
      "K ;  Si =", k_2410.volt(), "V")

# --- Non-uniform B grid (cap 7.95 T, inside the 8 T validator) ---
B_vec = np.hstack([np.linspace(0.05, 2.0, 196), np.linspace(2.05, 7.95, 120)])
print(f"B grid: {len(B_vec)} pts, dB_lo={B_vec[1]-B_vec[0]:.3f} dB_hi={B_vec[-1]-B_vec[-2]:.3f} T")

# --- Config (fresh station) ---
mc = dict(meas_config)
mc["sr0"]="drain current on T7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]=f"Step3 go/no-go B-sweep 0.05->7.95T at n={n_target:.1e}cm-2 D=0 (Vtg={Vtg:.3f},Vbg={Vbg:.3f}), Si=0"

s = async_station(mc)
s.add_comment('field-sweep-1d')
s.add_comment('trilayer-stacking-fs-count Step3 go/no-go; hole side high|n|, D=0')
s.add_comment(f'n={n_target:.2e} cm-2, D=0, B=0.05->7.95 T; cal from file_id 1 (ratio 1.298)')

# Position gates at the (n,D=0) point; field starts where it sits (~0).
s.ramp(k_2410.volt, 0)
s.ramp(k_bg.volt, Vbg)
s.ramp(dc205_volt, Vtg)

# No per-point Lakeshore polling (rig card: LS335 dual-master contention).
s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0, sr1, sr2, sr3]:
    s.fp(sr.X).fp(sr.P)
s.plot(magnet.mag, sr1.X)   # live Rxx vs B

try:
    s.sweep(magnet.mag, B_vec, delay=1.0)
finally:
    s.ramp(dc205_volt, 0); s.ramp(k_bg.volt, 0)
print("done; gates parked at 0, magnet held at", magnet.mag(), "T")
