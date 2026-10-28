# Gate C — contact-wiring liveness check (first session).
# Governing recipe: measurements/contact-survey-2t.md (B=0 aliveness flavor).
# Pre-(n,D)-cal RAW single-gate cut: sweep BG across its full validator at
# TG=0, reading the provided config channels + gate leakage. Current-bias rig
# (~1 nA through 100 MOhm) -> current channel separates dead/alive only; the
# CNP / Rxx read comes from the 4T voltage channel sr3 (30-31).
import numpy as np, time

# ---- preconditions: state this cell assumes but does NOT set ----
T = temperature()
B = magnet.field()
vtg0, vbg0 = k_tg.volt(), k_bg.volt()
tc1, tc2, tc3 = sr830_1.time_constant(), sr830_2.time_constant(), sr830_3.time_constant()
amp, frq = sr830_1.amplitude(), sr830_1.frequency()
print(f"T(probe MC) = {T*1e3:.1f} mK   (expect base, mK range)")
print(f"B           = {B*1e3:.3f} mT   (expect ~0; field controller NOT touched)")
print(f"gates now   : TG={vtg0:.3f} V   BG={vbg0:.3f} V")
print(f"lock-in tc  : sr1={tc1*1e3:.0f} ms  sr2={tc2*1e3:.0f} ms  sr3={tc3*1e3:.0f} ms")
print(f"AC drive    : {amp} V @ {frq} Hz  (-> ~1 nA through 100 MOhm)")
assert T < 0.08, f"T not at base: {T*1e3:.1f} mK"
assert abs(B) < 0.01, f"B unexpectedly large: {B*1e3:.3f} mT"

# ---- sweep design ----
delay = max(0.2, 5*max(tc1, tc2, tc3))   # dwell >= ~5*tau (STYLE settling floor)
N = 141
bg_lo, bg_hi = -4.0, 4.2                  # full BG validator (-4, +4.2)
bg_vec = np.linspace(bg_lo, bg_hi, N)
print(f"BG cut: {bg_lo} -> {bg_hi} V, {N} pts, delay={delay:.2f}s  "
      f"(~{N*(delay+1.0)/60:.1f} min + ramp)")

mc = dict(meas_config)
mc["bias_voltage_1"] = sr830_1.amplitude()
mc["lockin_freq_1"]  = sr830_1.frequency()
mc["comment"] = ("Gate C liveness: raw BG cut at TG=0, full BG validator, B~0; "
                 "sr1=5-4(I) sr2=5-4(2T) sr3=30-31(4T longitudinal)")

s = sweep.AsyncStation(mc)
s.add_comment('contact-survey-2t')
s.add_comment('Gate C liveness — raw BG cut, TG=0, pre-(n,D)-cal, first session')

# AC-only liveness: zero DC bias, park TG, position BG at start
s.ramp(dc205_1.volt, 0)
s.ramp(k_tg.volt, 0.0)
s.ramp(k_bg.volt, bg_lo)
time.sleep(5)

s.fp(temperature).fp(fridge_temperature)
s.fp(k_tg.volt).fp(k_tg.curr).fp(k_bg.volt).fp(k_bg.curr)
s.fp(sr830_1.X).fp(sr830_1.P)
s.fp(sr830_2.X).fp(sr830_2.P)
s.fp(sr830_3.X).fp(sr830_3.P)
s.plot(k_bg.volt, sr830_3.X)   # 4T voltage vs BG -> CNP peak
s.plot(k_bg.volt, sr830_1.X)   # current channel -> pinned-at-I_bias check
s.plot('time', k_bg.curr)      # live BG leakage

s.sweep(k_bg.volt, bg_vec, delay=delay)

# park back gate
s.ramp(k_bg.volt, 0.0)
