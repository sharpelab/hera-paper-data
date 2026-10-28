# === Cell B: LK ladder 25 -> base, one [4,8] T sweep per rung, alternating direction ===
from sharpelab_nb.gates import calc_gate_voltages

_B0 = magnet.field()
print(f"precheck: T={T_sample():.3f} K (expect ~50, holding), B={_B0:+.3f} T (expect ~8), "
      f"Vsi={dc205.voltage():+.3f}")
assert abs(dc205.voltage()) < 1e-3
logfile_fresh()   # from Cell A's namespace (set_T_verified too)

C_TG, C_BG, N_OFF = 1.7027e-3, 2.1751e-3, -0.0365
vtg_t, vbg_t = calc_gate_voltages(+6.0, 0.0, C_TG, C_BG, n_offset=N_OFF)
print(f"electron point: Vtg {vtg_t:+.3f}, Vbg {vbg_t:+.3f}")

sr1.sensitivity(2e-5); sr2.sensitivity(2e-5); sr3.sensitivity(5e-5); sr0.sensitivity(5e-2)
k_tg.volt(vtg_t); k_bg.volt(vbg_t)

RUNGS = [25.0, 18.0, 14.0, 10.0, 7.0, 5.0, 3.0, None]   # None = heaters off, base rung
N_PTS = 421                                              # [4,8] T at 9.5 mT

try:
    for i, rung in enumerate(RUNGS):
        if rung is not None:
            settle = set_T_verified(rung)
        else:
            heater.off('both')
            print("--> heaters OFF, settling to base (<=1.6 K)")
            t0 = time.time()
            while T_sample() > 1.6:
                interruptible_sleep(30)
                logfile_fresh()
                if time.time() - t0 > 3600:
                    raise RuntimeError(f"base not reached in 60 min (T={T_sample():.3f})")
            settle = time.time() - t0
        T_now = T_sample()

        # alternate direction; first rung starts at 8 T (where the magnet sits)
        down = (i % 2 == 0)
        B_vec = np.linspace(8.0, 4.0, N_PTS) if down else np.linspace(4.0, 8.0, N_PTS)

        s = sweep.AsyncStation(meas_config)
        s.add_comment('temperature-dependence')
        s.add_comment(f'LK ladder rung {i+1}/{len(RUNGS)}: T = {T_now:.3f} K '
                      f'({"base" if rung is None else str(rung)+" K set"}), electron n = +6e12, D = 0 '
                      f'({vtg_t:.3f}, {vbg_t:.3f}); B {B_vec[0]:.0f}->{B_vec[-1]:.0f} T uniform 9.5 mT; '
                      f'I_bias=20 nA, sens fixed across ladder, settle {settle:.0f} s, cal run 4')
        s.fp(T_sample)
        s.fp(k_tg.volt).fp(k_tg.curr)
        s.fp(k_bg.volt).fp(k_bg.curr)
        s.plot('time', k_tg.curr)
        s.plot('time', k_bg.curr)
        for lia in (sr0, sr1, sr2, sr3):
            s.fp(lia.X).fp(lia.P)
            s.plot(magnet.field, lia.X)
        s.sweep(magnet.field, B_vec, delay=1.2)
        print(f"    rung {i+1} done: T was {T_now:.3f} K (now {T_sample():.3f} K)")
finally:
    heater.off('both')
    k_tg.volt(0); k_bg.volt(0)
    print(f"ladder exit: heaters off, gates parked, T={T_sample():.3f} K, B={magnet.field():+.3f} T")
