# === 0 T gatemap (`gatemap`): TG fast [-0.3, +1.0] V x BG slow [-1.3, +1.2] V, 20 x 40 mV ===
# --- preconditions (assumed, not set) ---
assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
_T0, _B0 = T_sample(), magnet.field()
print(f"precondition T_sample = {_T0:.3f} K (1.0-1.5), B = {_B0:+.4f} T (|B|<0.02), V_si = {k_si():+.3f} V (0), "
      f"nplci tg/bg = {k_tg.nplci()}/{k_bg.nplci()} (1/1)")
assert 1.0 <= _T0 <= 1.5 and abs(_B0) < 0.02 and abs(k_si()) < 0.01
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current nplci not reset to 1"

Vtg_vec = np.linspace(-0.3, 1.0, 66)    # fast, 20 mV
Vbg_vec = np.linspace(-1.3, 1.2, 63)    # slow, 40 mV
assert Vtg_vec.min() >= TG_MIN and Vtg_vec.max() <= TG_MAX and Vbg_vec.min() >= BG_MIN and Vbg_vec.max() <= BG_MAX
FAST_DELAY, SLOW_DELAY = 1.0, 3.0
I_TRIP = 1e-9

# Fixed sensitivity for the whole map (no autorange mid-row): 100 uV = 10 kOhm full scale at 10 nA.
sr1.sensitivity(100e-6)
print(f"drive {sr1.amplitude()} V -> 10 nA; sr1 sens {sr1.sensitivity()} V (10 kOhm FS); sr0 sens {sr0.sensitivity()} V; tau {sr1.time_constant()} s")

mc = dict(meas_config); mc["Si (V)"] = k_si(); mc["sample_temperature:"] = _T0
mc["comments"] = "gatemap: TG fast -0.3..+1.0 V (66), BG slow -1.3..+1.2 V (63), B = 0, Vsi = 0, sr1 sens 100 uV; re-run of run 4 (railed at 2 kOhm)"
s = sweep.AsyncStation(mc)
s.add_comment('gatemap')
s.add_comment('TG fast [-0.3, +1.0] V 66 pts (20 mV); BG slow [-1.3, +1.2] V 63 rows (40 mV); B = 0; Vsi = 0; first map of cooldown')
s.ramp(k_bg.volt, Vbg_vec[0]); s.ramp(k_tg.volt, Vtg_vec[0])
interruptible_sleep(10)

# row layout: [time, Vbg(slow), Vtg(fast), T_sample, k_tg.curr, k_bg.curr, sr0.X, sr0.P, sr1.X, sr1.P]
s.fp(T_sample).fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_bg.volt, k_bg.curr); s.plot('time', k_tg.curr)

def leak_guard(station, data):
    i_tg, i_bg = abs(float(data[4])), abs(float(data[5]))
    if i_tg > I_TRIP or i_bg > I_TRIP:
        print(f"LEAK TRIP at Vbg={float(data[1]):+.3f}, Vtg={float(data[2]):+.3f}: |I_tg|={i_tg:.3e}, |I_bg|={i_bg:.3e} A")
        station.interrupt_requested = True
s.register_run_after(leak_guard, ())

try:
    s.megasweep(k_bg.volt, Vbg_vec, k_tg.volt, Vtg_vec, slow_delay=SLOW_DELAY, fast_delay=FAST_DELAY)
finally:
    s.ramp(k_tg.volt, 0); s.ramp(k_bg.volt, 0)
