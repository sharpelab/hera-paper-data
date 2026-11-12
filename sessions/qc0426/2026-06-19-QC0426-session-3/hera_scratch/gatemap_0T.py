# Step 1b — 0 T TG-BG gate map (gatemap.md / cnp-and-dline-calibration Step 1).
# Axis-aligned megasweep in raw gate volts (no cap-ratio assumed): slow = BG rows,
# fast = TG. CNP ridge V_tg(V_bg) -> slope = -c_bg/c_tg for the (n,D) calibration,
# plus the metallic/insulating survey for picking fan contact pairs. Si held at 0
# (contact gate). Sized from run-0: CNP intercept +0.44 V, prior slope -1.3.
import numpy as np, time

# --- preconditions (assumed, not set) ---
_T = heater.sample_temperature(); _B = magnet.mag()
print(f"[precond] sample_T={_T:.3f} K  B={_B:+.4f} T")
assert _T < 5.0 and abs(_B) < 0.05, "T/B precondition failed"
_I = sr0.X() / abs(meas_config["sr0_gain"])
print(f"[precond] I_meas={_I*1e9:.3f} nA")
assert abs(_I) > 1e-10, "no current — contacts/mux lost?"

# --- station (fresh; comments per run) ---
meas_config["comments"] = "0T gatemap: slow BG[-4,4] x17, fast TG[-6,7] x105, Si=0; CNP-line + metallic survey; provided config"
s = async_station(meas_config)
s.add_comment('gatemap')
s.add_comment(meas_config["comments"])
s.fp(heater.sample_temperature)
s.fp(k_2400.curr).fp(k_2410.curr)
for sx in (sr0, sr1, sr2, sr3):
    s.fp(sx.X).fp(sx.P)
# live leakage + a fast-row Rxx monitor (2D plot.png does not show the map; re-form from TSV)
s.plot('time', k_2400.curr); s.plot('time', k_2410.curr); s.plot(dc205_volt, sr1.X)

# --- position, then map ---
s.ramp(k_si.volt, 0.0)
s.ramp(k_bg.volt, -4.0); s.ramp(dc205_volt, -6.0); time.sleep(3)
bg_vec = np.linspace(-4.0, 4.0, 17)     # slow, 0.5 V rows
tg_vec = np.linspace(-6.0, 7.0, 105)    # fast, 0.125 V
s.megasweep(k_bg.volt, bg_vec, dc205_volt, tg_vec, slow_delay=2.0, fast_delay=1.0)
# park gates
k_bg.volt(0.0); dc205_volt(0.0)
print("[done] gatemap complete; gates parked at 0")
