# === Step 3a — SdH spot check, ELECTRON side: n = +6e12 cm^-2, D = 0, B 0.5 -> 8 T ===
# recipe: measurements/sdh-spot-check.md (uniform-B, blocking magnet)

# --- preconditions ---
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
print(f"preconditions: T_sample={_Ts:.3f} K (expect 1.0-1.5), B={_B:+.4f} T (expect <0.6, ramping up), "
      f"V_si={_Vsi:+.3f} V (expect 0), settle_s={getattr(magnet, 'settle_s', '?')} (expect 3 s), "
      f"nplci={k_2400_tg.nplci()}/{k_2400_bg.nplci()} (expect 1/1)")
assert 1.0 <= _Ts <= 1.5, f"not at base T: {_Ts:.3f} K"
assert abs(_B) <= 0.6, f"field too high to start the up-sweep: {_B:+.4f} T"
assert abs(_Vsi) <= 0.05, f"Si gate not parked: {_Vsi:+.3f} V"

# --- drive + sensitivities (high-|n| metallic; card starting points tuned — see md) ---
sr1.amplitude(2.0)      # 2 V / 100 MOhm = 20 nA
sr1.sensitivity(2e-6)
sr2.sensitivity(1e-6)
sr3.sensitivity(5e-5)   # R_xy(8 T) ~ 830 Ohm -> 17 uV
sr0.sensitivity(5e-2)   # 20 nA x 1e6 = 20 mV

# --- uniform-B grid, Nyquist at the low edge (F_L = 62 T) ---
B_vec = np.concatenate([np.arange(0.5, 1.0, 0.002),          # onset segment
                        np.arange(1.0, 8.0 + 1e-9, 0.0054)])  # main segment
vtg_pt, vbg_pt = d0_point(+6.0)
print(f"target: (Vtg, Vbg) = ({vtg_pt:+.3f}, {vbg_pt:+.3f}); {len(B_vec)} field points")

meas_config["comments"] = (f"sdh-spot-check: electron n=+6e12 cm^-2 D=0 (Vtg={vtg_pt:+.3f}, Vbg={vbg_pt:+.3f}), "
                           "B 0.5->8 T uniform-B (2.0 mT to 1 T, 5.4 mT above), I_bias=20 nA, F_L=62 T")
s = sweep.AsyncStation(meas_config)
s.add_comment('sdh-spot-check')
s.add_comment('electron side; grid: Nyquist at low edge per segment; dwell = settle_s 3 s (=10 tau); '
              'cal: run-4 CNP calibration (see device card)')

s.ramp(k_tg.volt, vtg_pt)
s.ramp(k_bg.volt, vbg_pt)
interruptible_sleep(10)
s.ramp(magnet.field, B_vec[0])   # blocking ramp to the floor

xp = magnet.field
s.fp(T_sample).fp(T_vaporizer)
s.fp(magnet.field)
s.fp(k_tg.volt).fp(k_tg.curr)
s.fp(k_bg.volt).fp(k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.fp(_l.X).fp(_l.P)
s.plot(xp, k_tg.curr)
s.plot(xp, k_bg.curr)
for _l in (sr0, sr1, sr2, sr3):
    s.plot(xp, _l.X)
    s.plot(xp, _l.P)
s.plot('time', T_sample)
s.plot('time', T_vaporizer)

s.sweep(magnet.field, B_vec, delay=0)   # dwell = magnet settle_s + readback
print("electron spot check done; field holds at 8 T, gates at the electron point")
