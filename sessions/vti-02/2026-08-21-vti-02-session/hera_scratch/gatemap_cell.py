# === Step 1 — gatemap: full validator box at B = 0, Si = 0 (CNP location + (n, D) calibration input) ===
# Precondition reads (assumed, not set): stop on mismatch.
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
print(f"pre: T_sample={_Ts:.3f} K (want 1.05-1.45) | B={_B:+.4f} T (want |B|<0.02) | Si={_Vsi:+.3f} V (want 0) | heater ranges={_rs},{_rv} | nplci tg {k_tg.nplci()} bg {k_bg.nplci()} (want 1)")
assert 1.05 <= _Ts <= 1.45 and abs(_B) < 0.02 and abs(_Vsi) < 0.01 and _rs == 0 and _rv == 0
assert k_tg.nplci() == 1 and k_bg.nplci() == 1, "gate-current NPLC not reset to 1"

# Lock-in scale: gate C legs (runs 0-3) put Rxx in 60-320 Ohm at 10 nA; sr1 readback quantizes at
# ~1/16000 of full scale (run 0: 60 nV steps at 1 mV sens = 6 Ohm staircase), so sens sits near the signal:
# 50e-6 V full scale = 5000 Ohm at 10 nA (0.3 Ohm resolution). Railing above 5000 Ohm is accepted
# (gapped corners flat-top; the D~0 ridge is what this map is for).
sr1.sensitivity(50e-6)
print(f"sr0 sens={sr0.sensitivity()} tau={sr0.time_constant()} | sr1 sens={sr1.sensitivity()} tau={sr1.time_constant()} | I_bias {sr1.amplitude()/meas_config['bias_resistor']*1e9:.1f} nA")

# Grid: TG fast (1.3 V span, flyback ~1.6 s at 5 mV/6 ms), BG slow.
vtg_vec = np.linspace(TG_MIN, TG_MAX, 66)   # 20 mV
vbg_vec = np.linspace(BG_MIN, BG_MAX, 67)   # 50 mV
fast_delay, slow_delay = 0.7, 1.0               # dwell 7 tau at 24 dB/oct (tau 0.1 s) + 1 s row settle
LEAK_ABORT = 1e-9  # A — in-sweep guard: clean interrupt (partial data kept, gates parked in finally)

mc = dict(meas_config)
mc["comments"] = f"gatemap; B=0, Si=0, TG {TG_MIN}..{TG_MAX} ({len(vtg_vec)} fast) x BG {BG_MIN}..{BG_MAX} ({len(vbg_vec)} slow), 10 nA, sr1 sens {sr1.sensitivity()}"
s = sweep.AsyncStation(mc)
s.add_comment('gatemap')
s.add_comment(f'first map, full validator box: TG {TG_MIN:+g}..{TG_MAX:+g} V fast ({len(vtg_vec)} pts), BG {BG_MIN:+g}..{BG_MAX:+g} V slow ({len(vbg_vec)} rows); Si = 0 V; B = 0 T; I = 10 nA')
s.fp(T_sample)
s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
# row layout: [time, slow(bg), fast(tg), T_sample, I_tg, I_bg, sr0X, sr0P, sr1X, sr1P]
def _leak_guard(data, station):
    if abs(data[4]) > LEAK_ABORT or abs(data[5]) > LEAK_ABORT:
        print(f"LEAK GUARD: I_tg={data[4]:.2e} A, I_bg={data[5]:.2e} A at (tg {data[2]:+.3f}, bg {data[1]:+.3f}) — interrupting")
        station.interrupt_requested = True
s.register_run_after(_leak_guard, ())
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot(k_tg.volt, k_tg.curr); s.plot(k_bg.volt, k_bg.curr)

s.ramp(k_tg.volt, vtg_vec[0]); s.ramp(k_bg.volt, vbg_vec[0])
interruptible_sleep(5)
try:
    s.megasweep(k_bg.volt, vbg_vec, k_tg.volt, vtg_vec, slow_delay=slow_delay, fast_delay=fast_delay)
finally:
    k_tg.volt(0); k_bg.volt(0)
    print(f"gates parked: tg {k_tg.volt():+.4f} V, bg {k_bg.volt():+.4f} V")
