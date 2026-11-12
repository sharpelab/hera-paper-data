# Pristine-field survey gate map — investigation sc-characterization Step 1.
# Axis-aligned (V_tg, V_bg) megasweep at B=0: candidate low-Rxx overview AND
# the cap-ratio / CNP-slope substrate (cnp-and-dline-calibration). COARSE
# reconnaissance — resolve the CNP line + broad candidate regions; the narrow
# SC arc gets located by n-linecuts + a tight nD map next. Recipe: gatemap.md.
# 4T (sr3, 30-31) is the science channel (validated SNR~108 at 1 nA, run 1);
# 2T (sr2) saturates at 1 nA (drive feedthrough on injection node 5) -> coarse
# range, cross-check only.
import numpy as np, time

# ---- preconditions: assumed, not set ----
T = temperature(); B = magnet.field()
print(f"T={T*1e3:.1f} mK  B={B*1e3:.3f} mT  TG={k_tg.volt():.3f} BG={k_bg.volt():.3f}  amp={sr830_1.amplitude()} V")
assert T < 0.08, f"T not at base: {T*1e3:.1f} mK"
assert abs(B) < 0.01, f"B too large: {B*1e3:.3f} mT (survey map must precede energising the magnet)"

# ---- instrument settings (HERA-set; operator owns hands) ----
for sr in (sr830_1, sr830_2, sr830_3):
    sr.time_constant(0.1)          # 100 ms: ~3x faster map; 4T SNR still ~60
sr830_1.sensitivity(2e-3)          # current ~1 mV
sr830_2.sensitivity(2e-3)          # 2T saturates at 1 nA -> coarse range, cross-check only
sr830_3.sensitivity(5e-6)          # 4T: resolve low-Rxx (CNP ~218 nV, metallic ~6-20 nV)
print("tc:", sr830_3.time_constant(), " sens 1/2/3:",
      sr830_1.sensitivity(), sr830_2.sensitivity(), sr830_3.sensitivity())

# ---- map geometry (full validator box) ----
N_tg, N_bg = 81, 121
tg_vec = np.linspace(-7.0, 6.0, N_tg)      # full TG validator, SLOW axis
bg_vec = np.linspace(-4.0, 4.2, N_bg)      # full BG validator, FAST axis
fast_delay, slow_delay = 0.3, 1.0          # fast_delay = 3x tc
est_h = N_tg*(slow_delay + N_bg*(fast_delay+0.2))/3600
print(f"map {N_tg}x{N_bg} (TG slow / BG fast), est ~{est_h:.1f} h")

mc = dict(meas_config); mc["bias_voltage_1"] = sr830_1.amplitude()
mc["comment"] = ("survey gatemap B=0: TG[-7,6] x BG[-4,4.2] 81x121 coarse; "
                 "4T=sr3(30-31) primary tc=100ms; cap-ratio + candidate overview")

s = sweep.AsyncStation(mc)
s.add_comment('gatemap')
s.add_comment('cnp-and-dline-calibration')      # this map is the cap-ratio substrate
s.add_comment('pristine-field survey B=0 — first map before energising magnet')

s.ramp(dc205_1.volt, 0)
s.ramp(k_tg.volt, -7.0)
s.ramp(k_bg.volt, -4.0)
time.sleep(10)

s.fp(temperature).fp(fridge_temperature)
s.fp(k_tg.curr).fp(k_bg.curr)                   # leakage (not the swept volts)
s.fp(sr830_1.X).fp(sr830_1.P)
s.fp(sr830_2.X).fp(sr830_2.P)
s.fp(sr830_3.X).fp(sr830_3.P)
s.plot(k_bg.volt, sr830_3.X)                    # live 4T vs BG (CNP / candidate tracking)
s.plot('time', k_bg.curr)                       # live BG leakage
s.plot('time', k_tg.curr)                       # live TG leakage

s.megasweep(k_tg.volt, tg_vec, k_bg.volt, bg_vec,
            slow_delay=slow_delay, fast_delay=fast_delay)

s.ramp(k_tg.volt, 0.0); s.ramp(k_bg.volt, 0.0)
