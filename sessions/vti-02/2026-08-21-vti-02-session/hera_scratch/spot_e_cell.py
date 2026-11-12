# === Step 3 — sdh-spot-check, electron side, D = 0: B 0 -> 10 T, uniform in B ===
# Calibration committed from run 4 (cnp-and-dline-calibration): ratio data-calibrated, scale geometry prior.
C_TG = 2.7961e-3          # F/m^2, stack prior (9.5 nm hBN), anchor
C_BG = 2.0330e-3          # F/m^2, from the CNP-line slope -dVtg/dVbg = 0.7271 (run 4, rows Vbg -1.25..-0.2, rms 18 mV)
N_OFFSET = -0.069     # 1e12 cm^-2, from the CNP-line intercept (sharpelab_nb.gates units)
D_OFFSET = 0.0          # V/nm — stated assumption: D = 0 taken at the geometric symmetric point (run 4 read: ridge-R minimum at geometric D = +0.006 V/nm, so the gap minimum and the geometry agree)
from sharpelab_nb.gates import calc_gate_voltages, calc_nD
cal_s = GateCalibration(C_TG, C_BG, n_offset=N_OFFSET * 1e16, D_offset=D_OFFSET * 1e9)

N_SPOT, D_SPOT = 3.0, 0.0   # 1e12 cm^-2, V/nm
Vtg_spot, Vbg_spot = calc_gate_voltages(N_SPOT, D_SPOT, C_TG, C_BG, n_offset=N_OFFSET, D_offset=D_OFFSET)
assert TG_MIN <= Vtg_spot <= TG_MAX and BG_MIN <= Vbg_spot <= BG_MAX, (Vtg_spot, Vbg_spot)
print(f"spot (n, D) = ({N_SPOT:+.2f}e12, {D_SPOT:+.2f} V/nm) -> (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; roundtrip {calc_nD(Vtg_spot, Vbg_spot, C_TG, C_BG, N_OFFSET, D_OFFSET)}")

# Precondition reads (assumed, not set)
_Ts, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
_rs, _rv = heater.sample_range(), heater.vaporizer_range()
_st = magnet._status()
print(f"pre: T_sample={_Ts:.3f} K | B={_B:+.4f} T (want |B|<0.02) | Si={_Vsi:+.3f} V | heater ranges={_rs},{_rv} | output={_st['output_enabled']} PS={_st['persistent_switch_on']}")
assert 1.05 <= _Ts <= 1.45 and abs(_B) < 0.02 and abs(_Vsi) < 0.01 and _rs == 0 and _rv == 0
assert _st['output_enabled'] and _st['persistent_switch_on']

# Field grid: uniform in B, dB = Δ(1/B)·B_lo² with Δ(1/B) = 1/(3·F_L(n_spot)) = 0.0108 T^-1, B_lo = 1.5 T -> dB = 24 mT.
# Sweep from 0 (magnet is at 0; the sub-onset leg is the low-field MR + onset read, ~62 extra pts).
B_MAX = 10.0
assert B_MAX <= B_SESSION_CAP
B_vec = np.arange(0.0, B_MAX + 1e-9, 0.024)
# Lock-in: Rxx at this point is 54 Ohm at B = 0 (run 4) = 0.54 uV at 10 nA; the readback quantizes at ~1/16000 of
# full scale, so a fixed scale sized for the high-B MR would digitize the low-B oscillations. Use the corpus
# autorange hook (sharpelab_nb.autorange.autorange_sr830s: keeps sr1 between 10 % and 90 % of its range, 10 tau
# wait per change, floor 1 uV) as a run_before hook; the current channel (sr0, ~180 deg) is its validity check.
from sharpelab_nb.autorange import autorange_sr830s
sr1.sensitivity(2e-6)
dwell = 0.7
print(f"B grid: {len(B_vec)} pts, 0 -> {B_MAX} T, dB = {np.diff(B_vec)[0]*1e3:.1f} mT | sr1 start sens {sr1.sensitivity()} (autorange) tau {sr1.time_constant()} | magnet settle_s {getattr(magnet, 'settle_s', None)}")

mc = dict(meas_config)
mc["comments"] = f"sdh-spot-check; electron, (n, D) = ({N_SPOT:+.2f}e12, {D_SPOT:+.2f}), (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}), B 0 -> {B_MAX} T uniform dB {np.diff(B_vec)[0]*1e3:.1f} mT, 10 nA, Si 0"
s = sweep.AsyncStation(mc)
s.add_comment('sdh-spot-check')
s.add_comment(f'electron side, D = 0: n = {N_SPOT:+.2f}e12 cm^-2, (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}) V; B = 0 -> {B_MAX} T, {len(B_vec)} pts uniform-B (dB {np.diff(B_vec)[0]*1e3:.1f} mT = 1/(3 F_L) at B_lo {1.5} T); I = 10 nA; Si = 0 V')
s.add_comment(f'calibration: c_tg {C_TG:.4e} (prior), c_bg {C_BG:.4e} (ratio from run 4 CNP slope), n_offset {N_OFFSET:+.3f}e12, D_offset {D_OFFSET}')
s.register_run_before(autorange_sr830s, (sr0, [sr1]))
s.fp(T_sample).fp(T_vaporizer)
s.fp(k_tg.volt).fp(k_bg.volt)
s.fp(k_tg.curr).fp(k_bg.curr)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X)
s.plot('time', k_tg.curr); s.plot('time', k_bg.curr); s.plot(magnet.field, T_sample)

s.ramp(k_tg.volt, Vtg_spot); s.ramp(k_bg.volt, Vbg_spot)
interruptible_sleep(10)
print(f"gates at ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V; starting field sweep")
s.sweep(magnet.field, B_vec, delay=dwell)
print(f"done: B = {magnet.field():+.3f} T (left at B_MAX for the hole-side ride-down); gates held at the electron point")
