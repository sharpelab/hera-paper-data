# === Landau fan, electron side, D = 0 (`landau-fan-vti`) — three chained runs in one cell ===
#   run A: measured ride-up 0 -> 10 T at n = +2.5e12 (`sdh-spot-check`, third density)
#   run B: one n-line row at 10 T (worst dynamic-range corner) -> sizes the fan's fixed sensitivity
#   run C: the fan, 10 -> 1 T descending, uniform in 1/B, n-line 3.2 -> 1.0e12 at D = 0
import numpy as np
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
from hera.analysis import field_invB

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)   # run-5 cnp-and-dline-calibration
I_BIAS = 1.0 / 100e6          # 10 nA nominal (drive 1 V / 100 MOhm); measured 9.85-9.93 nA in runs 6/7
I_TRIP = 1e-9                 # gate-leak trip (A)
FAST_DELAY, SLOW_DELAY = 1.2, 1.0

def gv(n12):
    vt, vb = calc_gate_voltages(n12, 0.0, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
    assert np.all((vt >= TG_MIN) & (vt <= TG_MAX)) and np.all((vb >= BG_MIN) & (vb <= BG_MAX)), (np.min(vt), np.max(vt), np.min(vb), np.max(vb))
    return vt, vb

# ---------- design numbers (computed, on the page) ----------
n_up = 2.5                                        # ride-up density, 1e12 cm^-2
ns = np.linspace(3.2, 1.0, 101)                   # fan n-line (fast axis), descending n per row
Vtgs, Vbgs = gv(ns); Vtg_up, Vbg_up = gv(n_up)
B_up = np.unique(np.round(np.hstack((np.arange(0.0, 1.0, 0.05), np.arange(1.0, 2.0, 0.0125), np.arange(2.0, 10.0001, 0.025))), 4))
N_B = 93; B_fan = field_invB(10.0, 1.0, N_B)      # uniform in 1/B, descending
dinvB = (1 / B_fan[-1] - 1 / B_fan[0]) / (N_B - 1)
h_over_4e = 4.1357e-15 / 4                        # T m^2
F_L_hi = h_over_4e * ns.max() * 1e16
assert B_up.max() <= B_SESSION_CAP and B_fan.max() <= B_SESSION_CAP
assert dinvB <= 1 / (3 * F_L_hi), (dinvB, F_L_hi)                       # >= 3 rows per period of F_L(n_hi)
dn_ray_1T = 4 * 2.4180e14 * 1.0 * 1e-16                                  # 4eB/h at 1 T, 1e12 cm^-2
print(f"fan: n {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts, dn {abs(ns[1]-ns[0]):.3f}e12 = {dn_ray_1T/abs(ns[1]-ns[0]):.1f} pts per 4eB/h ray at 1 T); "
      f"D = 0; Vtg {Vtgs.min():+.4f}..{Vtgs.max():+.4f}, Vbg {Vbgs.min():+.4f}..{Vbgs.max():+.4f} V")
print(f"fan: B {B_fan[0]:.3f} -> {B_fan[-1]:.3f} T, {N_B} rows uniform in 1/B, d(1/B) = {dinvB:.5f} /T -> Nyquist {1/(2*dinvB):.1f} T (F_L(n_hi) = {F_L_hi:.1f} T, {1/(dinvB*F_L_hi):.1f} rows/period)")
print(f"ride-up: n = {n_up:+.2f}e12 -> (Vtg, Vbg) = ({Vtg_up:+.4f}, {Vbg_up:+.4f}); {len(B_up)} pts 0 -> 10 T (50 mT | 12.5 mT 1-2 T | 25 mT 2-10 T); F_L = {h_over_4e*n_up*1e16:.1f} T")
t_pt = FAST_DELAY + 0.10   # gatemap run 5 calibration: 0.10 s/pt read overhead on top of fast_delay
t_fan = N_B * (len(ns) * t_pt + SLOW_DELAY + 3.0 + 4.0) + (B_fan[0] - B_fan[-1]) / 0.137 * 60
t_up = 10.0 / 0.137 * 60 + len(B_up) * 3.1        # runs 6/7: 3.1 s per field setpoint over the bare ramp
print(f"price: ride-up {t_up/3600:.2f} h + sizing row ~0.05 h + fan {t_fan/3600:.2f} h = {(t_up + 180 + t_fan)/3600:.2f} h")

# ---------- preconditions (assumed, not set) ----------
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B| < 0.05: ride-up starts at 0), V_si = {k_si():+.3f} V (0), "
      f"PS heater {magnet.persistent_switch_on()}, output {magnet.output_enabled()}, sr1 tau {sr1.time_constant()} s / {sr1.filter_slope()} dB")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.05 and abs(k_si()) < 0.01
assert magnet.persistent_switch_on() and magnet.output_enabled()
assert abs(sr1.amplitude() - 1.0) < 1e-3 and abs(sr1.time_constant() - 0.3) < 1e-3

def leak_guard(station, data):
    # fp order below puts the gate currents at data[-6], data[-5] and sr1.X at data[-2] in every run of this cell
    i_tg, i_bg = abs(float(data[-6])), abs(float(data[-5]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A at row {data[:3]}")
        station.interrupt_requested = True

def add_fps(st):
    st.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
    st.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
    st.register_run_after(leak_guard, ())

# ================= run A: measured ride-up, sdh-spot-check at n = +2.5e12 =================
sr1.sensitivity(50e-6)                             # 5 kOhm FS; run 6 (n=3.2) peaked at 528 Ohm, run 7 (n=-1.2) at 583 Ohm
mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = f"sdh-spot-check electron n = {n_up:+.2f}e12, D = 0 (run-5 cal), ride-up 0 -> 10 T for the fan; sr1 50 uV"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron side: n = {n_up:+.2f}e12 cm^-2, D = +0.00 V/nm; (Vtg, Vbg) = ({Vtg_up:+.4f}, {Vbg_up:+.4f}); '
              f'B 0 -> 10 T uniform-B (50 mT to 1 T, 12.5 mT 1-2 T, 25 mT 2-10 T); ride-up for the landau-fan-vti; cal run 5')
s.ramp(k_bg.volt, Vbg_up); s.ramp(k_tg.volt, Vtg_up)
interruptible_sleep(10)
add_fps(s)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.sweep(magnet.field, B_up, delay=0)
print(f"ride-up done: B = {magnet.field():+.3f} T, T_sample = {T_sample():.3f} K")
if s.interrupt_requested: raise RuntimeError("ride-up interrupted — not starting the fan")

# ================= run B: sizing row at 10 T (worst corner: low n x high B) =================
sr1.sensitivity(100e-6)                            # 10 kOhm FS for the sizing read
_clip = {"n": 0, "xmax": 0.0}
def clip_track(station, data):
    x = abs(float(data[-2])); _clip["xmax"] = max(_clip["xmax"], x)
    if x >= 0.9 * sr1.sensitivity(): _clip["n"] += 1
mc2 = dict(mc); mc2["comments"] = "landau-fan-vti sizing row: fan n-line at B = 10 T, sr1 100 uV; sets the fan's fixed sensitivity"
s2 = sweep.AsyncStation(mc2)
s2.add_comment('landau-fan-vti'); s2.add_comment(f'sizing row: D = 0, n = {ns[0]:+.2f} to {ns[-1]:+.2f}e12 ({len(ns)} pts), B = 10 T fixed; sr1 100 uV')
s2.ramp(k_bg.volt, Vbgs[0]); s2.ramp(k_tg.volt, Vtgs[0])
interruptible_sleep(10)
add_fps(s2); s2.register_run_after(clip_track, ())
s2.plot(k_tg.volt, sr1.X); s2.plot(k_tg.volt, sr0.X); s2.plot('time', k_tg.curr); s2.plot('time', k_bg.curr)
s2.multimegasweep([magnet.field], [[10.0]], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
R_max = _clip["xmax"] / I_BIAS
print(f"sizing row: max |sr1_X| = {_clip['xmax']*1e6:.1f} uV -> R_max(10 T) = {R_max:.0f} Ohm; clipped pts = {_clip['n']}")
if _clip["n"] > 0:
    s2.ramp(k_tg.volt, 0); s2.ramp(k_bg.volt, 0)
    raise RuntimeError("sizing row railed at 10 kOhm FS — low-n x 10 T corner is insulating-scale; redesign n_lo (field left at 10 T, gates parked)")
ladder = [50e-6, 100e-6, 200e-6, 500e-6]
sens = next(sv for sv in ladder if sv / I_BIAS >= 2.0 * R_max)         # FS >= 2 x worst-corner R (headroom, not precision)
sr1.sensitivity(sens)
print(f"fan sensitivity: {sens*1e6:.0f} uV = {sens/I_BIAS:.0f} Ohm FS (>= 2 x {R_max:.0f} Ohm)")

# ================= run C: the fan =================
def clip_flag(station, data):
    x = abs(float(data[-2]))
    if x >= 0.95 * sens: print(f"CLIP B={float(data[1]):+.3f} T |sr1_X|={x*1e6:.1f} uV")
mc3 = dict(mc); mc3["comments"] = (f"landau-fan-vti: D = 0, n = {ns[0]:+.2f} -> {ns[-1]:+.2f}e12 ({len(ns)} pts) fast; B 10 -> 1 T {N_B} rows uniform 1/B slow; "
                                   f"sr1 {sens*1e6:.0f} uV; fast_delay {FAST_DELAY} s, slow_delay {SLOW_DELAY} s; cal run 5")
s3 = sweep.AsyncStation(mc3)
s3.add_comment('landau-fan-vti')
s3.add_comment(f'D = 0.00 V/nm, n = {ns[-1]:+.2f} to {ns[0]:+.2f}e12 cm^-2 ({len(ns)} pts, swept high->low n), B = {B_fan[0]:.2f} to {B_fan[-1]:.2f} T '
               f'({N_B} rows uniform in 1/B, d(1/B) = {dinvB:.5f} /T); electron side; cal run 5 (ratio 0.773, n_offset -0.089e12, D_offset -0.013); '
               f'sr1 sens {sens*1e6:.0f} uV sized from the 10 T row (R_max {R_max:.0f} Ohm)')
add_fps(s3); s3.register_run_after(clip_flag, ())
s3.plot(k_tg.volt, sr1.X); s3.plot(k_tg.volt, sr0.X); s3.plot('time', k_tg.curr); s3.plot('time', k_bg.curr)
try:
    s3.multimegasweep([magnet.field], [B_fan], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s3.ramp(k_tg.volt, 0); s3.ramp(k_bg.volt, 0)    # park gates; field stays at the fan's end (1 T) by design
print(f"fan done: B = {magnet.field():+.3f} T, gates ({k_tg.volt():+.3f}, {k_bg.volt():+.3f}) V, T_sample = {T_sample():.3f} K")
