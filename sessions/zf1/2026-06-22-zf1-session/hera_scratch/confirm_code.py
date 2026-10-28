# === Run 4: confirm candidate + pin optimum D + resolve Rxx floor ===
# 3 fine constant-D linecuts (D=-0.55,-0.60,-0.65, in-box bracket) + an edge
# sweep (BG=+4.198 pinned, TG -4..-6) probing the max-|D| boundary. sr830_3 at
# 200 uV to resolve whether Rxx->0. Base T, B nominal-0. (Run 3 found the dip.)

# --- precondition reads ---
_T = temperature(); _B = magnet.field()
print(f"probe MC T = {_T*1e3:.1f} mK   (expect base)")
print(f"magnet B   = {_B*1e3:+.3f} mT  (expect ~0 nominal)")
assert _T < 0.060, f"T={_T*1e3:.1f} mK not at base"
assert abs(_B) < 0.005, f"|B|={_B*1e3:.2f} mT not ~nominal-0"

_v = np.load("hera_scratch/confirm_vectors.npz")
vtg_vec = _v["vtg"]; vbg_vec = _v["vbg"]
print(f"loaded {len(vtg_vec)} pts (segments: {sorted(set(_v['seg']))})")
assert (vtg_vec>=-7.0).all() and (vtg_vec<=6.0).all(), "Vtg out of box"
assert (vbg_vec>=-4.0).all() and (vbg_vec<=4.2).all(), "Vbg out of box"

sr830_1.amplitude(0.1)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
meas_config["lockin_freq_1"]  = sr830_1.frequency()
meas_config["comment"] = "Run4 confirm candidate: D={-.55,-.60,-.65}+edge(BG+4.198), n~-4.8 dip, 1nA, 200uV, B=0"

sr830_2.sensitivity(0.1)
sr830_3.sensitivity(2e-4)            # 200 uV -> resolve Rxx floor (~0.07 Ohm)
sr830_3.time_constant(0.3)
for lia in (sr830_1, sr830_2, sr830_3):
    print(f"{lia.name}: tc={lia.time_constant()} s  sens={lia.sensitivity()} V")

s = sweep.AsyncStation(meas_config)
s.add_comment('cnp-and-dline-calibration')   # constant-D gate linecuts
s.add_comment('Run4 candidate confirm: fine D-linecuts {-0.55,-0.60,-0.65}/nm + max-|D| edge sweep')
s.add_comment('dip from run3 at n~-4.8e11, D~-0.65; sr830_3 @ 200uV to resolve floor; 1nA; B=0')

s.ramp(k_tg.volt, float(vtg_vec[0]))
s.ramp(k_bg.volt, float(vbg_vec[0]))

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

s.plot(k_tg.volt, sr830_3.X)
s.plot('time', k_tg.curr)
s.plot('time', k_bg.curr)

try:
    s.multisweep([k_tg.volt, k_bg.volt], [vtg_vec, vbg_vec], delay=1.5)
finally:
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
