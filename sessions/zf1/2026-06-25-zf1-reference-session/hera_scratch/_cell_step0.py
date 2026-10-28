# === Step 0 — effective-zero (B_eff0) calibration (ONCE, at the optimum) ===
# Rxx vs B_perp around 0 to find the symmetric-dip center = the cooldown's
# trapped-flux-compensated "B=0". Discipline-compliant: TWO one-sided cuts,
# each swept TOWARD 0 (+5->0 and -5->0); positioning ramps are not measurements.
# Gates held at the optimum (n=-5.0e11, D=-0.64). Zero DC bias, AC sense.

# --- silent-precondition reads ---
T_now = temperature(); B_now = magnet.field()
Vtg_now = k_tg.volt(); Vbg_now = k_bg.volt(); Hv = heater.volt()
print(f"T = {T_now*1e3:.1f} mK     (expect ~34)")
print(f"B = {B_now*1e3:.4f} mT    (expect ~0)")
print(f"V_tg = {Vtg_now:.3f} V     (expect -5.365, optimum)")
print(f"V_bg = {Vbg_now:.3f} V     (expect +3.987, optimum)")
print(f"heater = {Hv:.3f} V       (expect 0)")
assert T_now < 0.060, f"T high: {T_now*1e3:.1f} mK"
assert abs(B_now) < 0.005, f"B off-zero at start: {B_now*1e3:.3f} mT"
assert abs(Vtg_now - (-5.365)) < 0.010, f"V_tg off optimum: {Vtg_now:.3f}"
assert abs(Vbg_now - (+3.987)) < 0.010, f"V_bg off optimum: {Vbg_now:.3f}"
assert Hv < 0.01, f"heater on: {Hv:.3f} V"

# --- AC sense config: 1 nA, 4T sens 1 mV, zero DC bias ---
dc205_1.volt(0.0)
sr830_1.amplitude(0.1)        # 1 nA
sr830_2.sensitivity(0.005)
sr830_3.sensitivity(0.001)    # 4T (30-31), SC channel
print(f"magnet ramp_rate = {magnet.ramp_rate()*1e3:.3f} mT/s")

B_AMP = 5e-3       # +/-5 mT span
B_STEP = 0.1e-3    # 0.1 mT
NPTS = int(round(2*B_AMP/B_STEP/2)) + 1   # 51 pts per one-sided half (5->0)
DLY = 4.0          # ~4 s dwell/pt so each 0.1 mT step thermalizes

meas_config["comment"] = ("Step0 B_eff0 calibration at optimum (n=-5.0e11, D=-0.64); "
                          "Rxx vs B_perp; two one-sided cuts +5->0 and -5->0; "
                          "0.1 mT step, ~4 s/pt; AC 1 nA, 4T sens 1 mV, DC bias 0")
s = sweep.AsyncStation(meas_config)
s.add_comment('field-sweep-1d')
s.add_comment('Step 0: effective-zero (B_eff0) calibration, one-sided pair toward 0')
s.add_comment(meas_config["comment"])
xp = magnet.field
s.fp(k_tg.volt).fp(k_tg.curr); s.fp(k_bg.volt).fp(k_bg.curr); s.fp(temperature)
for lia in (sr830_1, sr830_2, sr830_3): s.fp(lia.X).fp(lia.P)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr)
s.plot(xp, sr830_1.X)       # current monitor
s.plot(xp, sr830_3.X)       # 4T Rxx vs B -- the field-kill dip

try:
    # --- half A: +5 -> 0 mT (one-sided toward 0) ---
    s.add_comment('half A: +5 -> 0 mT')
    s.ramp(magnet.field, +B_AMP); interruptable_sleep(20)   # position + settle
    print(f"positioned at B = {magnet.field()*1e3:.3f} mT; sweeping +5 -> 0")
    s.sweep(magnet.field, np.linspace(+B_AMP, 0.0, NPTS), delay=DLY)

    # --- half B: -5 -> 0 mT (one-sided toward 0) ---
    s.add_comment('half B: -5 -> 0 mT')
    s.ramp(magnet.field, -B_AMP); interruptable_sleep(20)   # position + settle
    print(f"positioned at B = {magnet.field()*1e3:.3f} mT; sweeping -5 -> 0")
    s.sweep(magnet.field, np.linspace(-B_AMP, 0.0, NPTS), delay=DLY)
finally:
    s.ramp(magnet.field, 0.0)
print(f"done; magnet at {magnet.field()*1e3:.3f} mT, gates held at optimum")
