# === Step 4 — Landau fan, D=0, hole side (landau-fan-vti) ===
# Ride the magnet home from 7.95 T (no re-traverse). Per-column SdH FFT ->
# F(n); the Onsager overlay (Step 5) is the primary read. Key discriminator:
# does the main tone's F(n) lie on the FULL-density Luttinger line
# (n*h/4e -> ABC single pocket) or BELOW it (ABA-BL, deficit = ML pocket)?
# Non-uniform B: dense at low/mid field to avoid aliasing the fast ~40 T tone
# into a spurious low-F pocket (QC0426/VTI 2026-06-14 trap).

import numpy as np, scipy.constants as cst
C_TG = cst.epsilon_0*3.0/15.6e-9          # geometry-anchored (file_id 1 cal)
C_BG = 1.298*C_TG                         # fitted ratio
N_OFF = -7.095e14
def gates_for(n_cm2, D=0.0):
    n_m2=n_cm2*1e4; a=(n_m2-N_OFF)*cst.e; b=2.0*D*cst.epsilon_0
    return (a+b)/(2*C_TG), (a-b)/(2*C_BG)

# fast axis: D=0 hole-side n-line
n_vec = np.linspace(-1.4e12, -5.0e12, 36)
Vtgs, Vbgs = gates_for(n_vec, 0.0)
assert Vtgs.min()>-6 and Vtgs.max()<7 and Vbgs.min()>-4.5 and Vbgs.max()<4.5, "n-line out of validators"
print(f"n-line: {n_vec[0]:.2e}..{n_vec[-1]:.2e} cm^-2, {len(n_vec)} pts")
print(f"  Vtg {Vtgs[0]:.3f}..{Vtgs[-1]:.3f} V ; Vbg {Vbgs[0]:.3f}..{Vbgs[-1]:.3f} V")

# slow axis: B descending from where the magnet sits (~7.95 T), non-uniform
B_vec = np.hstack([np.linspace(7.95, 4.0, 27), np.linspace(3.9, 0.5, 52)])
print(f"B: {B_vec[0]}..{B_vec[-1]} T, {len(B_vec)} rows; dB_hi={B_vec[0]-B_vec[1]:.3f} dB_lo={B_vec[-2]-B_vec[-1]:.3f}")

# --- Preconditions ---
assert abs(magnet.mag()-7.95) < 0.3, f"magnet not at ~7.95 T: {magnet.mag()}"
assert heater.sample_temperature() < 2.0, f"T not at base: {heater.sample_temperature()}"
print("pre: B =", magnet.mag(), "T ; T =", heater.sample_temperature(), "K ; Si =", k_2410.volt())

mc = dict(meas_config)
mc["sr0"]="drain current on T7"; mc["sr1"]="Rxx T3-T4"; mc["sr2"]="Rxx B4-B5"; mc["sr3"]="Rxy T5-B6"
mc["comments"]=f"Step4 Landau fan D=0 hole side, n={n_vec[0]:.1e}..{n_vec[-1]:.1e}, B 7.95->0.5 T (ride home), Si=0"

s = async_station(mc)
s.add_comment('landau-fan-vti')
s.add_comment('trilayer-stacking-fs-count Step4; D=0 hole side; cal file_id 1 (ratio 1.298)')
s.add_comment(f'D=0, n={n_vec[0]:.2e}..{n_vec[-1]:.2e} cm-2, B=7.95->0.5 T descending non-uniform')

# Position gates at first n-point; Si=0; magnet already at ~7.95 T (first B).
s.ramp(k_2410.volt, 0)
s.ramp(k_bg.volt, Vbgs[0])
s.ramp(dc205_volt, Vtgs[0])

s.fp(k_bg.curr).fp(k_2410.curr)
for sr in [sr0, sr1, sr2, sr3]:
    s.fp(sr.X).fp(sr.P)
s.plot(magnet.mag, sr1.X)

try:
    s.multimegasweep([magnet.mag], [B_vec], [dc205_volt, k_bg.volt], [Vtgs, Vbgs],
                     slow_delay=1, fast_delay=0.8)
finally:
    s.ramp(dc205_volt, 0); s.ramp(k_bg.volt, 0); s.ramp(magnet.mag, 0)
print("done; gates parked at 0, magnet ramped to 0")
