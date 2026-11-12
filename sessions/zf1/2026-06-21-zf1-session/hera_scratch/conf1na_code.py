# 1 nA confirmation cut — re-run the Gate C BG cut at the device-card nominal
# drive (0.1 V -> 1 nA) to validate 4T SNR and my lock-in sensitivity choices
# before the survey map. Direct before/after vs run 0 (40 pA). Recipe:
# contact-survey-2t (raw single-gate aliveness flavor).
import numpy as np, time

# ---- preconditions: state assumed but not set ----
T = temperature(); B = magnet.field()
vtg0, vbg0 = k_tg.volt(), k_bg.volt()
print(f"T = {T*1e3:.1f} mK   B = {B*1e3:.3f} mT   gates TG={vtg0:.3f} BG={vbg0:.3f}")
print(f"AC drive now = {sr830_1.amplitude()} V (raising to 0.1 V)")
assert T < 0.08, f"T not at base: {T*1e3:.1f} mK"
assert abs(B) < 0.01, f"B too large: {B*1e3:.3f} mT"

# ---- set drive + sensitivities for 1 nA (HERA-chosen, per operator) ----
s_drive = 0.1                  # 0.1 V -> 1 nA through 100 MOhm (device card)
sr830_1.amplitude(s_drive)
sr830_1.sensitivity(2e-3)      # current: 1 nA * 1e6 = 1 mV -> 2 mV range
sr830_2.sensitivity(1e-4)      # 2T: CNP ~43 uV -> 100 uV range
sr830_3.sensitivity(2e-5)      # 4T: tuned for the low-Rxx (metallic) regime;
                               #     CNP peak may clip (we don't need it for SC)
print("amp:", sr830_1.amplitude(), " sens:",
      sr830_1.sensitivity(), sr830_2.sensitivity(), sr830_3.sensitivity())

delay = max(0.2, 5*max(sr830_1.time_constant(),
                       sr830_2.time_constant(), sr830_3.time_constant()))
N = 141
bg_vec = np.linspace(-4.0, 4.2, N)
print(f"BG cut -4 -> 4.2 V, {N} pts, delay={delay:.2f}s "
      f"(~{N*(delay+1.0)/60:.1f} min + ramp)")

mc = dict(meas_config)
mc["bias_voltage_1"] = s_drive
mc["comment"] = ("1nA confirmation: raw BG cut TG=0, drive 0.1V/1nA, "
                 "sens sr1=2mV sr2=100uV sr3=20uV; validate 4T SNR vs run0(40pA)")

s = sweep.AsyncStation(mc)
s.add_comment('contact-survey-2t')
s.add_comment('1nA confirmation BG cut, TG=0 — validate 4T SNR for survey map')

s.ramp(dc205_1.volt, 0)        # AC-only
s.ramp(k_tg.volt, 0.0)
s.ramp(k_bg.volt, -4.0)
time.sleep(5)

s.fp(temperature).fp(fridge_temperature)
s.fp(k_tg.volt).fp(k_tg.curr).fp(k_bg.curr)   # not k_bg.volt (swept, auto-recorded)
s.fp(sr830_1.X).fp(sr830_1.P)
s.fp(sr830_2.X).fp(sr830_2.P)
s.fp(sr830_3.X).fp(sr830_3.P)
s.plot(k_bg.volt, sr830_3.X)   # 4T vs BG -> should now show a clean CNP
s.plot(k_bg.volt, sr830_1.X)   # current (pinned ~1 nA)
s.plot('time', k_bg.curr)      # live leakage

s.sweep(k_bg.volt, bg_vec, delay=delay)
s.ramp(k_bg.volt, 0.0)
