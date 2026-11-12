# === Run 3: fine constant-D n-linecuts (rule out an undersampled SC arc) ===
# 4 D-lines (D=-0.35,-0.45,-0.55,-0.65), n=-1.5..-9e11, n-step 0.075e11 (~11x
# finer than the survey BG step). Gate vectors precomputed from the confirmed
# calibration (c_bg/c_tg=1.185), clipped by dropping out-of-box pts. Base T, B nominal-0.

# --- precondition reads (state this cell assumes but does not set) ---
_T = temperature(); _B = magnet.field()
print(f"probe MC T = {_T*1e3:.1f} mK   (expect base)")
print(f"magnet B   = {_B*1e3:+.3f} mT  (expect ~0 nominal; ~2 mT trapped flux unchanged)")
assert _T < 0.060, f"T={_T*1e3:.1f} mK not at base"
assert abs(_B) < 0.005, f"|B|={_B*1e3:.2f} mT not ~nominal-0"

# load precomputed constant-D vectors
_lc = np.load("hera_scratch/linecut_vectors.npz")
vtg_vec = _lc["vtg"]; vbg_vec = _lc["vbg"]
print(f"loaded {len(vtg_vec)} pts across D-lines {list(_lc['Ds'])}")
assert (vtg_vec>=-7.0).all() and (vtg_vec<=6.0).all(), "Vtg out of validator box"
assert (vbg_vec>=-4.0).all() and (vbg_vec<=4.2).all(), "Vbg out of validator box"

# AC drive -> 1 nA; refresh meas_config
sr830_1.amplitude(0.1)
meas_config["bias_voltage_1"] = sr830_1.amplitude()
meas_config["lockin_freq_1"]  = sr830_1.frequency()
meas_config["comment"] = "Run3 fine n-linecuts: D={-.35,-.45,-.55,-.65}, n=-1.5..-9e11, step .075e11, 1nA, B=0"

sr830_2.sensitivity(0.1)
sr830_3.sensitivity(0.002)
for lia in (sr830_1, sr830_2, sr830_3):
    print(f"{lia.name}: tc={lia.time_constant()} s  sens={lia.sensitivity()} V")

s = sweep.AsyncStation(meas_config)
s.add_comment('cnp-and-dline-calibration')   # constant-D lines designed off this recipe
s.add_comment('Run3 fine n-linecuts to rule out undersampled SC arc (sc-characterization Step 1)')
s.add_comment('D={-0.35,-0.45,-0.55,-0.65} V/nm; n=-1.5..-9e11; step 0.075e11; 1nA; B=0')

s.ramp(k_tg.volt, float(vtg_vec[0]))
s.ramp(k_bg.volt, float(vbg_vec[0]))

s.fp(temperature)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for lia in (sr830_1, sr830_2, sr830_3):
    s.fp(lia.X).fp(lia.P)

s.plot(k_tg.volt, sr830_3.X)   # 4T Rxx — candidate channel
s.plot('time', k_tg.curr)      # live leakage
s.plot('time', k_bg.curr)

try:
    s.multisweep([k_tg.volt, k_bg.volt], [vtg_vec, vbg_vec], delay=1.2)
finally:
    s.ramp(k_tg.volt, 0.0)
    s.ramp(k_bg.volt, 0.0)
