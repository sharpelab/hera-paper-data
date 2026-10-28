# HERA — plan step 3: fine band map along the CNP line (R_CNP(D), peak width, ±D comparison)
_T, _B, _Vsi = T_sample(), magnet.field(), dc205.voltage()
print(f"precheck: T_sample={_T:.3f} K (want 1.0-1.4) | B={_B:.4f} T (want |B|<0.02) | V_si={_Vsi:.3f} V (want 0) | "
      f"gates now V_tg={k_tg.volt():.3f} V_bg={k_bg.volt():.3f}")
assert 1.0 <= _T <= 1.4, "T_sample out of base window"
assert abs(_B) < 0.02, "magnet not at zero"
assert abs(_Vsi) < 0.01, "Si not at 0 V"
for _s in (sr0, sr1):
    _s.time_constant(0.1)
print(f"sr0 sens={sr0.sensitivity()} V, sr1 sens={sr1.sensitivity()} V, tau={sr1.time_constant()} s")

# CNP line from run 3 ridge (rows V_bg -0.2..-1.3): V_tg = 0.10 - 0.691 * V_bg
CNP_A, CNP_B = 0.10, -0.691
_vb_rows = np.round(np.arange(-1.3, 0.60 + 1e-9, 0.05), 3)          # slow: hole-side end first (gates sit at V_bg=-1.3, V_tg=1.0)
_dv = np.round(np.arange(-0.15, 0.15 + 1e-9, 0.005), 4)             # fast: TG window about the line, 5 mV
_vt_list, _vb_list = [], []
for _vb in _vb_rows:
    _vt = CNP_A + CNP_B * _vb + _dv
    _vt_ok, _vb_ok = sanitize_tg_bg(_vt, np.full_like(_vt, _vb), tg_lims, bg_lims)
    _vt_list.append(_vt_ok); _vb_list.append(_vb_ok)
_vt_all = np.concatenate(_vt_list); _vb_all = np.concatenate(_vb_list)
_npts = len(_vt_all)
print(f"band map: {len(_vb_rows)} rows (V_bg {_vb_rows[0]:+.2f}..{_vb_rows[-1]:+.2f}), {_npts} pts after box clip; "
      f"V_tg in [{_vt_all.min():.3f}, {_vt_all.max():.3f}]; est {_npts*0.68/60:.0f} min")
assert _vt_all.min() >= TG_MIN and _vt_all.max() <= TG_MAX and _vb_all.min() >= BG_MIN and _vb_all.max() <= BG_MAX

meas_config["sample_temperature:"] = T_sample()
meas_config["Si (V)"] = dc205.voltage()
meas_config["comments"] = "cnp-band-map: multisweep (V_bg,V_tg) rows V_bg -1.3..0.6 @50 mV, TG +/-0.15 V about V_tg=0.10-0.691*V_bg @5 mV; Si=0, B=0, base T"
s = sweep.AsyncStation(meas_config)
s.fp(sr0.X).fp(sr0.P).fp(sr1.X).fp(sr1.Y).fp(k_tg.curr).fp(k_bg.curr).fp(T_sample)
s.add_comment("cnp-band-map")
s.add_comment(f"multisweep [k_bg.volt, k_tg.volt]: {len(_vb_rows)} rows V_bg -1.3..0.6 @50mV x TG window +/-0.15 V @5mV about "
              f"V_tg=0.10-0.691*V_bg (run 3 ridge), box-clipped ({_npts} pts); delay 0.5 s, tau 100 ms; V_si=0, B=0; I_bias 10 nA")
# multisweep row = [time, V_bg, V_tg, *followed] -> sr1_X idx 5, sr1_Y idx 6
ar1 = SrAutoRange(sr1, cols=(5, 6), gain=1.0, lo=1e-6, hi=0.5)
s.register_run_after(ar1, args=())
for _p in (sr1.X, sr0.X, sr1.Y, sr0.P, k_tg.curr, k_bg.curr, T_sample):
    s.plot(k_tg.volt, _p)

_t0 = time.time()
res = s.multisweep([k_bg.volt, k_tg.volt], [_vb_all, _vt_all], delay=0.5)
_dt = time.time() - _t0
print(f"run {res.id}: {_dt/60:.1f} min, {_dt/_npts:.3f} s/pt; sr1 autorange steps: {len(ar1.log)} (last {ar1.log[-5:]})")
print(f"end state: V_tg={k_tg.volt():.4f} V, V_bg={k_bg.volt():.4f} V, T_sample={T_sample():.3f} K, sr1 sens={sr1.sensitivity()} V")
