# === Verify: LK mass split — temperature-dependence-vti Flavor B at the electron spot point (n = +3.0e12 design, D = 0) ===
from sharpelab_nb.gates import calc_gate_voltages
from sharpelab_nb.autorange import autorange_sr830s
C_TG, C_BG, N_OFFSET, D_OFFSET = 2.7961e-3, 2.0330e-3, -0.069, 0.0
Vtg_spot, Vbg_spot = calc_gate_voltages(3.0, 0.0, C_TG, C_BG, n_offset=N_OFFSET, D_offset=D_OFFSET)   # (+0.879, +1.209) V, run 5's point
RUNGS = [4.0, 7.0, 10.0, 14.0, 20.0, 28.0]   # K, ascending (up-legs catch in minutes on this rig; base rung = run 5)
RATIO = 0.95                                 # rig-card sanctioned; any other value is consent-gated
B_LO, B_HI, DB = 2.4, 10.0, 0.024            # run-5 grid restricted to the above-onset window
assert max(RUNGS) <= T_SESSION_CAP and B_HI <= B_SESSION_CAP and RATIO == 0.95

def _fresh_T():
    assert_thermometry_live("T_sample", VTI.temp_logfile_candidates["T_sample"], max_age=15, max_period=12)
    assert_thermometry_live("T_vaporizer", VTI.temp_logfile_candidates["T_vaporizer"], max_age=15, max_period=12)
    return T_sample(), T_vaporizer()

def settle_hover(target, t_start_vap, timeout_s=25*60):
    """Hover acceptance (VTI variant): stable (spread < 0.1 K over 90 s) inside [target-0.5, target+3] K.
    Runaway guard: T_vap > 2 K above BOTH its rung-start value and the target -> heaters off, stop.
    Timeout: if stable (spread < 0.2 K) proceed at the actual T (it is fp'd); else stop the cell."""
    hist = []  # (t, T)
    t0 = time.time()
    while True:
        Ts, Tv = _fresh_T()
        now = time.time(); hist.append((now, Ts)); hist = [(t, T) for (t, T) in hist if now - t <= 90]
        if Tv > t_start_vap + 2.0 and Tv > target + 2.0:
            heater.off('both')
            raise RuntimeError(f"RUNAWAY: T_vap {Tv:.2f} K > start {t_start_vap:.2f}+2 and > target {target}+2 — heaters off")
        spread = max(T for _, T in hist) - min(T for _, T in hist) if len(hist) >= 6 else 9.9
        inband = (target - 0.5) <= Ts <= (target + 3.0)
        if (now - t0) % 60 < 10: print(f"  settle {target} K: T_s {Ts:.3f} T_v {Tv:.3f} spread90 {spread:.3f} inband {inband} [{(now-t0)/60:.1f} min]")
        if inband and spread < 0.1 and (now - t0) > 90:
            return Ts
        if now - t0 > timeout_s:
            if spread < 0.2:
                print(f"  settle timeout at T_s {Ts:.3f} K (stable, spread {spread:.3f}) — proceeding at the actual T")
                return Ts
            raise RuntimeError(f"settle timeout: T_s {Ts:.3f} K not stable (spread {spread:.3f}) — stopping")
        interruptible_sleep(10)

# Preconditions (assumed, not set)
Ts0, Tv0 = _fresh_T(); _B = magnet.field(); _Vsi = dc205.voltage(); _st = magnet._status()
print(f"pre: T_s {Ts0:.3f} T_v {Tv0:.3f} K | B {_B:+.3f} T | Si {_Vsi:+.3f} | heater ranges {heater.sample_range()},{heater.vaporizer_range()} | output {_st['output_enabled']} PS {_st['persistent_switch_on']}")
assert abs(_Vsi) < 0.01 and _st['output_enabled'] and _st['persistent_switch_on']
assert (abs(_B - B_LO) < 0.2) or (abs(_B - B_HI) < 0.2), "magnet must sit at an end of the ladder window"

sr1.sensitivity(2e-6)
k_tg.volt(Vtg_spot); k_bg.volt(Vbg_spot)
interruptible_sleep(5)
print(f"gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V")

try:
    for i, T_rung in enumerate(RUNGS):
        Ts_pre, Tv_pre = _fresh_T()
        heater.set_both(T_rung, ratio=RATIO)
        time.sleep(2)
        print(f"rung {i}: set_both({T_rung}, {RATIO}) -> ranges {heater.sample_range()},{heater.vaporizer_range()}; setpoints {heater.sample_setpoint()},{heater.vaporizer_setpoint()}")
        assert heater.sample_range() > 0 and heater.vaporizer_range() > 0, "heater ranges did not turn on"
        T_ok = settle_hover(T_rung, Tv_pre)
        B_now = magnet.field()
        B_vec = np.arange(B_LO, B_HI + 1e-9, DB)
        if B_now > (B_LO + B_HI) / 2: B_vec = B_vec[::-1]          # alternate direction from the live field, never re-traverse
        print(f"rung {i}: T_s {T_ok:.3f} K accepted; sweep {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T")
        mc = dict(meas_config); mc["comments"] = f"temperature-dependence-vti Flavor B (LK): rung {T_rung} K (T_s {T_ok:.2f}), electron (+3.0e12 design, D=0), B {B_vec[0]:.1f} -> {B_vec[-1]:.1f} T, dB 24 mT, 10 nA, Si 0"
        s = sweep.AsyncStation(mc)
        s.add_comment('temperature-dependence-vti')
        s.add_comment(f'Flavor B LK ladder, rung {i}: nominal {T_rung} K (hover-accepted T_s {T_ok:.3f} K, ratio {RATIO}); fixed point electron n = +3.0e12 design (x0.90), D = 0, (Vtg, Vbg) = ({Vtg_spot:+.4f}, {Vbg_spot:+.4f}); B {B_vec[0]:.2f} -> {B_vec[-1]:.2f} T uniform dB {DB*1e3:.0f} mT ({len(B_vec)} pts); I = 10 nA; sr1 autorange; Si = 0')
        s.add_comment('sdh-spot-check')   # same acquisition as run 5 (grid, settling, autorange) for amplitude comparison
        s.register_run_before(autorange_sr830s, (sr0, [sr1]))
        s.fp(T_sample).fp(T_vaporizer)   # logfile reads only — never poll the LS335 per point (rig card: the worker owns its GPIB)
        s.fp(k_tg.volt).fp(k_bg.volt).fp(k_tg.curr).fp(k_bg.curr)
        s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.P)
        s.plot(magnet.field, sr1.X); s.plot(magnet.field, sr0.X); s.plot(magnet.field, T_sample); s.plot('time', k_tg.curr)
        s.sweep(magnet.field, B_vec, delay=0.7)
        Ts_end, Tv_end = _fresh_T()
        print(f"rung {i} done at B {magnet.field():+.3f} T; T_s {Ts_end:.3f} T_v {Tv_end:.3f} K")
finally:
    heater.off('both')
    print(f"heaters off: ranges {heater.sample_range()},{heater.vaporizer_range()}; B {magnet.field():+.3f} T; gates ({k_tg.volt():+.4f}, {k_bg.volt():+.4f}) V; T_s {T_sample():.3f} K")
