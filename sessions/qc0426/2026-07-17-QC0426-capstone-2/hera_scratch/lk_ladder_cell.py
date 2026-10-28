# === LK mass ladder (temperature-dependence-vti, Flavor B) ===
# Fixed point: hole n = -3.0e12, D = 0. Same-window field sweep per rung,
# alternating direction (never re-traverse). Per-branch LK masses decide
# the ABA call (two masses + a sum-mass breakdown tone) — investigation Verify.

RUNGS = [None, 6.0, 10.0, 15.0, 22.0, 32.0]   # None = base (no heater); K
B_LK_LO, B_LK_HI = 1.5, 8.0                   # deltaF = 1.85 T — splits 28/33
D_INVB = 1.0 / (3 * 33.2)
DB = D_INVB * B_LK_LO**2                       # 22.6 mT
NPTS = int(np.floor((B_LK_HI - B_LK_LO) / DB)) + 1

# -- preconditions
B = magnet.field()
Ts = T_sample()
print(f"precheck: B={B:+.3f} T (expect ~8, fan end), T={Ts:.3f} K (base)")
assert abs(B - 8.0) < 0.1, f"STOP: field not at 8 T: {B}"
assert Ts < 1.5, f"STOP: not at base: {Ts}"
hr = (heater.sample_range(), heater.vaporizer_range())
print(f"heater ranges at start: {hr} (expect (0, 0))")
assert hr == (0, 0), "STOP: heaters not off at ladder start"

# gates to the hole spot (already characterized; run-4 voltage convention —
# rung labels/gates keep the run-5 operating point for comparability)
vtg_h, vbg_h = gates_for(-3.0, 0.0)
k_2400_tg.volt(vtg_h)
k_2400_bg.volt(vbg_h)
sr1.sensitivity(1e-4)   # run-6 proven at this point to 8 T
sr2.sensitivity(5e-5)
sr3.sensitivity(1e-4)   # headroom for warm-rung R drift
print(f"gates ({vtg_h:+.3f}, {vbg_h:+.3f}); sens sr1 1e-4, sr2 5e-5, sr3 1e-4")

import os
LOGFILE = VTI.temp_logfile_candidates["T_sample"][0]

def fresh_T():
    """Logfile-freshness-guarded T read (>= 2-3 write periods per rig card)."""
    age = time.time() - os.path.getmtime(LOGFILE)
    assert age < 15.0, f"STOP: T logfile stale ({age:.0f} s) — dead worker?"
    return T_sample()

def wait_hover(target, timeout_s=1800):
    """Hover acceptance: spread < 0.1 K over 90 s inside [target-0.5, target+3].
    Direction-aware runaway guard: fault only on T_vap rising > 2 K above both
    its rung-start value and the target."""
    tv0 = T_vaporizer()
    t0 = time.time()
    window = []
    while time.time() - t0 < timeout_s:
        interruptible_sleep(10)
        Tn = fresh_T()
        tv = T_vaporizer()
        if tv > tv0 + 2.0 and tv > target + 2.0:
            heater.off("both")
            raise RuntimeError(f"runaway: T_vap={tv:.2f} K > start+2 and target+2 — heaters off")
        window.append((time.time(), Tn))
        window = [(t, x) for t, x in window if time.time() - t <= 90]
        vals = [x for _, x in window]
        if (len(window) >= 8 and (target - 0.5) <= np.mean(vals) <= (target + 3.0)
                and (max(vals) - min(vals)) < 0.1):
            return np.mean(vals)
    raise RuntimeError(f"hover acceptance timed out at {timeout_s} s (T={fresh_T():.2f} K)")

for ri, rung in enumerate(RUNGS):
    if rung is None:
        T_acc = fresh_T()
        print(f"rung 0: base, T = {T_acc:.3f} K (no heater)")
    else:
        heater.set_both(rung, ratio=0.95)
        interruptible_sleep(5)
        hr = (heater.sample_range(), heater.vaporizer_range())
        assert hr != (0, 0), f"STOP: set_both({rung}) left ranges at 0 — heater not driving"
        T_acc = wait_hover(rung)
        print(f"rung {ri}: nominal {rung} K, hover-accepted at {T_acc:.3f} K "
              f"(ranges {hr}, T_vap {T_vaporizer():.2f} K)")

    # alternate direction from the live field (never re-traverse)
    B_now = magnet.field()
    if abs(B_now - B_LK_HI) < abs(B_now - B_LK_LO):
        B_vec = np.linspace(B_LK_HI, B_LK_LO, NPTS)
    else:
        B_vec = np.linspace(B_LK_LO, B_LK_HI, NPTS)

    meas_config["comments"] = (
        f"temperature-dependence-vti Flavor B (LK mass ladder): rung {ri} "
        f"nominal {'base' if rung is None else rung}, accepted T={T_acc:.3f} K; "
        f"hole n=-3.0e12 D=0 (Vtg={vtg_h:+.3f}, Vbg={vbg_h:+.3f}); "
        f"B {B_vec[0]:.2f}->{B_vec[-1]:.2f} T, dB=22.6 mT; 20 nA @ 13 Hz"
    )
    s = sweep.AsyncStation(meas_config)
    s.add_comment('temperature-dependence-vti')
    s.add_comment(f'LK rung {ri}: T_nom={"base" if rung is None else rung} K, '
                  f'T_acc={T_acc:.3f} K, (Vtg, Vbg) = ({vtg_h:.4f}, {vbg_h:.4f}), n = -3.0, D = 0')
    s.fp(magnet.field)
    s.fp(k_2400_tg.volt).fp(k_2400_tg.curr)
    s.fp(k_2400_bg.volt).fp(k_2400_bg.curr)
    s.fp(T_sample).fp(T_vaporizer)
    s.plot(magnet.field, T_sample)
    s.plot(magnet.field, k_2400_tg.curr)
    s.plot(magnet.field, k_2400_bg.curr)
    for lia in (sr0, sr1, sr2, sr3):
        s.fp(lia.X).fp(lia.P)
        s.plot(magnet.field, lia.X)
    s.sweep(magnet.field, B_vec, delay=0)
    print(f"rung {ri} sweep done (file per rung); B at {magnet.field():+.2f} T")

# ladder done: heaters off, passive descent toward base (no catch — end state)
heater.off("both")
print(f"ladder complete; heaters off, passive cooldown from ~{fresh_T():.1f} K; "
      f"B at {magnet.field():+.2f} T; gates hold the hole spot")
