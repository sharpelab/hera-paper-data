# Step 1 (cheap-first) — 1D CNP locator: TG sweep across its full validator range
# at BG = 0, Si = 0, B = 0. The Rxx maximum locates the CNP in V_tg at V_bg = 0
# (the CNP-line intercept), confirming the CNP sits inside the gate box and sizing
# the 2D map. ~106 pts -> ~2 min. Tags cnp-and-dline-calibration.
import numpy as np, time

# --- preconditions (assumed, not set by this cell) ---
_T = heater.sample_temperature(); _B = magnet.mag()
print(f"[precond] sample_T={_T:.3f} K  B={_B:+.4f} T")
assert _T < 5.0, f"sample_T {_T} K too high"
assert abs(_B) < 0.05, f"|B|={_B} T not at zero"
# contacts still live? (mux selection persists from Gate C)
_I = sr0.X() / abs(meas_config["sr0_gain"])
print(f"[precond] I_meas={_I*1e9:.3f} nA (expect ~few nA -> contacts live)")
assert abs(_I) > 1e-10, "no current — contacts/mux lost?"

# --- station (fresh; comments per run) ---
meas_config["comments"] = "1D CNP locator: TG sweep [-6,7] V at BG=0, Si=0, B=0; provided config (src T2/drn B7, sr1 T3-T4, sr2 B4-B5, sr3 T5-B6)"
s = async_station(meas_config)
s.add_comment('cnp-and-dline-calibration')
s.add_comment(meas_config["comments"])

# followed params (raw; gain division is analysis-side from metadata)
s.fp(heater.sample_temperature)
s.fp(k_2400.curr).fp(k_2410.curr)                 # BG, Si leakage
for sx in (sr0, sr1, sr2, sr3):
    s.fp(sx.X).fp(sx.P)

# live plots: Rxx + current vs TG, Si leakage vs time
s.plot(dc205_volt, sr1.X); s.plot(dc205_volt, sr0.X); s.plot('time', k_2410.curr)

# --- position gates, then sweep TG ---
s.ramp(k_bg.volt, 0.0); s.ramp(k_si.volt, 0.0)
s.ramp(dc205_volt, -6.0); time.sleep(2)
tg_vec = np.linspace(-6.0, 7.0, 106)              # 0.123 V/pt
s.sweep(dc205_volt, tg_vec, delay=1.0)            # ~106 * ~1.2 s ~ 2 min
print("[done] CNP locator complete")
