# Step 1b (v2) — 0 T TG-BG gate map. FIX vs v1: do NOT fp the LS335 (per-point KRDG?
# contends with the Grafana logger -> VISA timeout, killed run 1, rig-card quirk).
# Temperature: one guarded read at the top into the comment; Grafana logs per-point T.
# GPIB Keithley leakage channels are single-master -> safe to fp per-point.
import numpy as np, time

# --- preconditions (assumed, not set) ---
try:
    _T = heater.sample_temperature()          # single read only (not per-point)
except Exception as e:
    _T = None; print("[warn] T read failed (LS335 busy):", e)
_B = magnet.mag()
print(f"[precond] sample_T={_T} K  B={_B:+.4f} T")
assert (_T is None) or _T < 5.0, "T precondition failed"
assert abs(_B) < 0.05, "B precondition failed"
_I = sr0.X() / abs(meas_config["sr0_gain"])
print(f"[precond] I_meas={_I*1e9:.3f} nA")
assert abs(_I) > 1e-10, "no current — contacts/mux lost?"

# --- station (fresh; comments per run; T snapshot in the comment, NOT fp'd) ---
meas_config["comments"] = f"0T gatemap v2: slow BG[-4,4] x17, fast TG[-6,7] x105, Si=0; T_start={_T} K; CNP-line + metallic survey; provided config (NO LS335 fp)"
s = async_station(meas_config)
s.add_comment('gatemap')
s.add_comment(meas_config["comments"])
s.fp(k_2400.curr).fp(k_2410.curr)             # BG, Si leakage (GPIB, safe per-point)
for sx in (sr0, sr1, sr2, sr3):
    s.fp(sx.X).fp(sx.P)
s.plot('time', k_2400.curr); s.plot('time', k_2410.curr); s.plot(dc205_volt, sr1.X)

# --- position from current state, then map ---
s.ramp(k_si.volt, 0.0)
s.ramp(k_bg.volt, -4.0); s.ramp(dc205_volt, -6.0); time.sleep(3)
bg_vec = np.linspace(-4.0, 4.0, 17)
tg_vec = np.linspace(-6.0, 7.0, 105)
s.megasweep(k_bg.volt, bg_vec, dc205_volt, tg_vec, slow_delay=2.0, fast_delay=1.0)
k_bg.volt(0.0); dc205_volt(0.0)
print("[done] gatemap v2 complete; gates parked at 0")
