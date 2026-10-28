# Step 4 — Landau fan, ELECTRON side at D=0 (the cleaner side, run 3). Field = SLOW axis
# (magnet ramps once, monotonically), paired-gate n-line = FAST axis. FS-count via per-column
# 1/B FFT of F(n): tracks the ML+BL partition f_ML(n)+f_BL(n)=F_L(n) and feeds the Onsager
# overlay (valid n<=3.5e12). NO LS335 fp.
import numpy as np, time

c_tg, c_bg, n_off = 1.7027e-3, 2.2004e-3, -1.581e15
E, EPS0 = 1.602176634e-19, 8.8541878128e-12
def gates_for(n, D=0.0):
    return ((n-n_off)*E/2 + EPS0*D)/c_tg, ((n-n_off)*E/2 - EPS0*D)/c_bg

# fast axis: n-line at D=0, low->high electron density
ns = np.linspace(1.0e16, 4.5e16, 41)            # 1.0 .. 4.5 e12 cm^-2
Vtgs, Vbgs = gates_for(ns, 0.0)
assert Vtgs.min()>=-6 and Vtgs.max()<=7 and Vbgs.min()>=-4.5 and Vbgs.max()<=4.5, "n-line OOR"
# slow axis: field, ascending, 8 mT step
B_vec = np.linspace(0.4, 4.0, 451)              # 8 mT; per-column FFT window [1,4] T alias-free
print(f"fan: {len(B_vec)} B-rows x {len(ns)} n-pts; n {ns.min()/1e16:.1f}..{ns.max()/1e16:.1f} e12; "
      f"Vtg {Vtgs.min():.2f}..{Vtgs.max():.2f}  Vbg {Vbgs.min():.2f}..{Vbgs.max():.2f}")

# --- preconditions ---
B0 = magnet.mag(); print(f"[precond] B={B0:+.4f} T (expect ~0)")
assert abs(B0) < 0.1, "magnet not near 0"
try: T0 = heater.sample_temperature()
except Exception as e: T0=None; print("[warn] T:",e)
sr1.amplitude(2.0)                              # bias 2V/20nA

# --- station ---
meas_config["bias_voltage"]=sr1.amplitude()
meas_config["comments"]=f"landau-fan-vti ELECTRON D=0, n=1.0..4.5e12 (41), B=0.4..4.0T (451, 8mT), bias 2V/20nA, fast_delay 1.0s; T_start={T0}"
s = async_station(meas_config)
s.add_comment('landau-fan-vti'); s.add_comment(meas_config["comments"])
s.fp(k_2400.curr).fp(k_2410.curr)
for sx in (sr0, sr1, sr2, sr3): s.fp(sx.X).fp(sx.P)
s.plot('time', k_2400.curr); s.plot('time', k_2410.curr); s.plot(magnet.mag, sr1.X)

# --- position: gates to first n-point, magnet to B_start, settle; fixed high-field sens ---
s.ramp(k_si.volt, 0.0); s.ramp(dc205_volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
s.ramp(magnet.mag, B_vec[0]); time.sleep(5)
sr1.sensitivity(1e-5); sr2.sensitivity(1e-5); sr3.sensitivity(2e-5)
meas_config["sr1_sens"]=sr1.sensitivity(); meas_config["sr2_sens"]=sr2.sensitivity(); meas_config["sr3_sens"]=sr3.sensitivity()
time.sleep(2)

# --- the fan ---
s.multimegasweep([magnet.mag], [B_vec], [dc205_volt, k_bg.volt], [Vtgs, Vbgs],
                 slow_delay=1.0, fast_delay=1.0)
# park
k_bg.volt(0.0); dc205_volt(0.0); magnet.mag(0.0)
print("[done] electron fan complete; gates 0, magnet ramping to 0")
