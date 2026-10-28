import numpy as np, time
# --- preconditions ---
T0 = heater.sample_temperature()
assert abs(magnet.mag()) < 0.15, 'magnet not near 0 for ascending fan'
assert abs(sr1.amplitude()-2.0) < 0.01, 'bias not 2 V'
assert abs(k_2410.volt()) < 1e-6, 'Si not 0'
# --- lock-in setup BEFORE the fan (no autorange mid-fan); tau low for fast-gate settling ---
for sr in (sr1, sr2, sr3): sr.time_constant(0.1)
sr0.sensitivity(5e-2); sr1.sensitivity(2e-5); sr2.sensitivity(2e-5); sr3.sensitivity(1e-4)
time.sleep(2)
for k,sr in [('sr0_sens',sr0),('sr1_sens',sr1),('sr2_sens',sr2),('sr3_sens',sr3)]:
    meas_config[k]=sr.sensitivity()
# --- fast axis: D=0 n-line (cm^-2). Prepend throwaway pt to absorb the per-row BG retrace ---
K = 2.760e12          # dn/dV_bg along D=0 (cm^-2/V), from this session's calibration
ratio = 1.2903        # V_tg = ratio * V_bg on the D=0 line through CNP origin
ns = np.concatenate([[-3.0e12], np.linspace(-3.0e12, -6.5e12, 29)])   # col 0 = throwaway
Vbgs = ns / K
Vtgs = ratio * Vbgs
assert Vtgs.min() > -6 and Vtgs.max() < 7 and Vbgs.min() > -4.5 and Vbgs.max() < 4.5, 'gate line out of validators'
# --- slow axis: B, coarse below 2 T, fine (40 mT) above (Nyquist for F_L up to ~70 T) ---
B_vec = np.concatenate([np.linspace(0.0, 2.0, 6, endpoint=False), np.linspace(2.0, 8.0, 151)])
print('fan: %d B-rows x %d n-pts (29 usable); B %.1f->%.1f T; n %.1f..%.1f e12; T=%.3f K' % (
    len(B_vec), len(ns), B_vec.min(), B_vec.max(), ns.max()/1e12, ns.min()/1e12, T0))
meas_config['comments'] = ('landau-fan-vti D=0 HOLE n=-3..-6.5e12 x B 0->8T; FS-count F(n) partition '
                           '(sr2 single? sr1 pair sum F_L?); 20nA; col0 throwaway; T_start=%.3f K' % T0)
s = async_station(meas_config)
s.add_comment('landau-fan-vti')
s.add_comment(meas_config['comments'])
s.fp(magnet.mag); s.fp(k_2400.curr); s.fp(k_2410.curr); s.fp(sr0.X)
for sr in (sr1, sr2, sr3):
    s.fp(sr.X); s.fp(sr.Y); s.fp(sr.R)
s.plot(dc205_volt, sr2.R)
s.multimegasweep([magnet.mag], [B_vec], [dc205_volt, k_2400.volt], [Vtgs, Vbgs],
                 slow_delay=1.0, fast_delay=0.7)
s.ramp(dc205_volt, 0.0); s.ramp(k_2400.volt, 0.0)
print('fan done; B=%.3f T  T_end=%.3f K' % (magnet.mag(), heater.sample_temperature()))
