# === Step 4 — landau-fan-vti, electron side, D = 0: B 10 -> 2.4 T (uniform 1/B, slow) x n-line (fast) ===
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
C_TG, C_BG, N_OFFSET, D_OFFSET = 2.7961e-3, 2.0330e-3, -0.069, 0.0   # run 4 calibration (prior scale; Luttinger scale 0.90 from run 5)

# Precondition reads (assumed, not set)
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
_st = magnet._status()
print(f"pre: T_sample={_Ts:.3f} K | B={_B:+.4f} T (want ~10) | Si={_Vsi:+.3f} V (want 0) | heater ranges={_rs},{_rv} | output={_st['output_enabled']} PS={_st['persistent_switch_on']} | nplci {k_tg.nplci()},{k_bg.nplci()}")
assert 1.05 <= _Ts <= 1.45 and abs(_B - 10.0) < 0.05 and abs(_Vsi) < 0.01 and _rs == 0 and _rv == 0
assert _st['output_enabled'] and _st['persistent_switch_on']

# Fast axis: D = 0 line, n = 3.4 -> 1.5 (design frame = run-4 calibration; actual n = 0.90 x on the run-5 Luttinger scale)
ns = np.linspace(3.4, 1.5, 41)                 # dn = 0.0475e12 (prior frame); ray spacing at 2.4 T = 0.26e12 -> 5 pts/ray
Ds = np.zeros_like(ns)
Vtgs, Vbgs = calc_gate_voltages(ns, Ds, C_TG, C_BG, n_offset=N_OFFSET, D_offset=D_OFFSET)
Vtgs, Vbgs = sanitize_tg_bg(Vtgs, Vbgs, tg_lims, bg_lims)   # clip by dropping, never clamping
n_chk, D_chk = calc_nD(Vtgs, Vbgs, C_TG, C_BG, N_OFFSET, D_OFFSET)
assert np.allclose(D_chk, 0.0, atol=1e-6) and len(Vtgs) == len(ns), (len(Vtgs), D_chk.max())
print(f"n-line: {len(Vtgs)} pts, n {n_chk.min():+.2f}..{n_chk.max():+.2f} e12 (design frame), Vtg {Vtgs.min():+.3f}..{Vtgs.max():+.3f}, Vbg {Vbgs.min():+.3f}..{Vbgs.max():+.3f}")

# Slow axis: uniform in 1/B from 10 T (where the magnet sits) down to the measured onset 2.4 T (run 5).
# Nyquist: F_L at the top of the line = 31.7 T (actual) -> d(1/B) <= 1/(3 F_L) = 0.0105; 36 rows give 0.0090 (1/(3.7 F_L)).
B_vec = field_invB(10.0, 2.4, 36)
assert np.all(np.abs(B_vec) <= B_SESSION_CAP)
print(f"B rows: {len(B_vec)}, {B_vec[0]:.3f} -> {B_vec[-1]:.3f} T, d(1/B) = {np.diff(1/B_vec)[0]:.4f} T^-1, dB {np.abs(np.diff(B_vec)).min()*1e3:.0f}..{np.abs(np.diff(B_vec)).max()*1e3:.0f} mT")

# Fixed scale for the whole fan (no autorange inside a 2D map): worst corner is low n x 10 T, where the Hall admixture
# on this pair (alpha ~ 0.2, run 5) puts R ~ 1-2 kOhm; 50 uV = 5 kOhm full scale at 10 nA, 0.3 Ohm readback resolution
# against SdH amplitudes of +-20..150 Ohm (run 5).
sr1.sensitivity(50e-6)
fast_delay, slow_delay = 0.7, 2.0   # 7 tau at 24 dB/oct; the blocking field set already settles 3 s
print(f"sr1 sens {sr1.sensitivity()} tau {sr1.time_constant()} | I_bias {sr1.amplitude()/meas_config['bias_resistor']*1e9:.1f} nA")

mc = dict(meas_config)
mc["comments"] = f"landau-fan-vti; electron, D = 0, n {ns.max():.2f} -> {ns.min():.2f} e12 (design frame, x0.90 actual), B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform 1/B {len(B_vec)} rows x {len(Vtgs)} pts, 10 nA, sr1 50 uV, Si 0"
s = sweep.AsyncStation(mc)
s.add_comment('landau-fan-vti')
s.add_comment(f'D = 0 V/nm, n = {ns.max():.2f} to {ns.min():.2f} e12 cm^-2 (run-4 calibration frame; Luttinger scale 0.90 from run 5), B = {B_vec[0]:.2f} to {B_vec[-1]:.2f} T uniform in 1/B ({len(B_vec)} rows, d(1/B) {np.diff(1/B_vec)[0]:.4f}); fast axis {len(Vtgs)} pts (Vtg, Vbg) line; I = 10 nA; Si = 0 V; sr1 sens 50 uV fixed')
s.add_comment(f'calibration: c_tg {C_TG:.4e} (prior), c_bg {C_BG:.4e} (run 4 CNP slope), n_offset {N_OFFSET:+.3f}e12, D_offset {D_OFFSET}')
s.fp(T_sample).fp(T_vaporizer)
s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
# row layout: [time, B, Vtg, Vbg, T_sample, T_vap, I_tg, I_bg, sr0X, sr0P, sr1X, sr1P]
def _leak_guard(data, station):
    if abs(data[6]) > 1e-9 or abs(data[7]) > 1e-9:
        print(f"LEAK GUARD: I_tg={data[6]:.2e} A, I_bg={data[7]:.2e} A at B={data[1]:.3f}, (tg {data[2]:+.3f}, bg {data[3]:+.3f}) — interrupting")
        station.interrupt_requested = True
s.register_run_after(_leak_guard, ())
s.plot(k_tg.volt, sr1.X); s.plot(k_tg.volt, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot(magnet.field, T_sample)

s.ramp(k_tg.volt, Vtgs[0]); s.ramp(k_bg.volt, Vbgs[0])
interruptible_sleep(5)
try:
    s.multimegasweep([magnet.field], [B_vec], [k_tg.volt, k_bg.volt], [Vtgs, Vbgs], slow_delay=slow_delay, fast_delay=fast_delay)
finally:
    print(f"end: B = {magnet.field():+.3f} T (held; next step decides), gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")
