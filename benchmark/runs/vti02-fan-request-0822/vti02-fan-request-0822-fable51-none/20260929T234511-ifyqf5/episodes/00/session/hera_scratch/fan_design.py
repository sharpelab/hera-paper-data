"""landau-fan design: D = 0 line (run-5 cal) as the fast co-swept (Vtg, Vbg) axis, B slow on a hybrid grid
(uniform 1/B at low B, capped at a max dB step at high B). Prints the grid, validator margins and the price."""
import json, numpy as np, scipy.constants as cst
from sharpelab_nb.gates import calc_gate_voltages, calc_nD

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
TG = (-0.3, 1.0); BG = (-1.3, 2.0)
MARGIN = 0.008  # V inside each validator

# --- fast axis: n along D = 0, step dn, clipped so both gates sit >= MARGIN inside the validators
dn = 0.04
ns = np.round(np.arange(-1.40, 3.40 + 1e-9, dn), 3)
Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
ok = (Vt >= TG[0] + MARGIN) & (Vt <= TG[1] - MARGIN) & (Vb >= BG[0] + MARGIN) & (Vb <= BG[1] - MARGIN)
ns, Vt, Vb = ns[ok], Vt[ok], Vb[ok]
nchk, Dchk = calc_nD(Vt, Vb, CAL["c_tg"], CAL["c_bg"], CAL["n_offset"], CAL["D_offset"])
print(f"fast axis: {len(ns)} pts, n = {ns[0]:+.2f} .. {ns[-1]:+.2f} e12 (step {dn}); "
      f"Vtg {Vt.min():+.4f}..{Vt.max():+.4f}, Vbg {Vb.min():+.4f}..{Vb.max():+.4f}; max|D| {np.abs(Dchk).max():.1e} V/nm; "
      f"dVtg/pt {np.diff(Vt).mean()*1e3:.1f} mV, dVbg/pt {np.diff(Vb).mean()*1e3:.1f} mV")

# --- slow axis: B hybrid grid
B0, B1, d, dBmax = 0.8, 10.0, 0.008, 0.15
Bc = np.sqrt(dBmax / d)
inv = np.arange(1 / B0, 1 / Bc - 1e-12, -d)
seg1 = 1 / inv
seg2 = np.arange(seg1[-1] + dBmax, B1 + 1e-9, dBmax)
if B1 - seg2[-1] > 0.02: seg2 = np.append(seg2, B1)
else: seg2[-1] = B1
B = np.round(np.hstack((seg1, seg2)), 4)
assert np.all(np.diff(B) > 0) and B.max() <= 10.0
dB = np.diff(B)
print(f"slow axis: {len(B)} rows, B {B[0]} -> {B[-1]} T; seg1 uniform 1/B (d={d} T^-1) {len(seg1)} rows to {seg1[-1]:.3f} T "
      f"(dB {dB[0]*1e3:.1f} -> {dB[len(seg1)-2]*1e3:.0f} mT); seg2 {len(seg2)} rows at {dBmax} T")
nhe = 3.26e16 * cst.h / cst.e
print(f"  nu resolution at n=+3.26e12 (nh/e={nhe:.0f} T): seg1 d_nu/row = {nhe*d:.2f}; seg2 at 5 T {nhe*dBmax/25:.2f}, at 10 T {nhe*dBmax/100:.2f}")
print(f"  n-steps a nu=20 line moves per row: 1 T {20*cst.e*dB[0]/cst.h*1e-16/dn:.1f}, 3 T {20*cst.e*dB[np.searchsorted(B,3)]/cst.h*1e-16/dn:.1f}, 6 T {20*cst.e*dBmax/cst.h*1e-16/dn:.1f}")

# --- price (calibrated on run 5: 4158 pts / 81.2 min at fast_delay 1.0 -> 0.10 s/pt read overhead; 6 ms per 5 mV gate step)
FAST_DELAY, SLOW_DELAY, SETTLE = 1.0, 2.0, 3.0
per_pt = FAST_DELAY + 0.10 + 0.04           # + co-swept second Keithley write
flyback = ((Vt.max() - Vt.min()) + (Vb.max() - Vb.min())) / 0.005 * 0.006
row_meas = len(ns) * per_pt + flyback + SLOW_DELAY + SETTLE
ramp = (B[-1] - 0.0) / (1 / 7.3) * 60      # 0.137 T/min from 0
tot = len(B) * row_meas + ramp
print(f"price: per-point {per_pt:.2f} s, flyback {flyback:.1f} s, row {row_meas:.0f} s; rows {len(B)*row_meas/3600:.2f} h + ramp 0->{B[-1]} T {ramp/60:.0f} min "
      f"= {tot/3600:.2f} h; realistic (+8%) {tot*1.08/3600:.2f} h")
json.dump(dict(ns=ns.tolist(), Vtg=Vt.tolist(), Vbg=Vb.tolist(), B=B.tolist(), d=d, dBmax=dBmax, B0=B0,
               fast_delay=FAST_DELAY, slow_delay=SLOW_DELAY, hours=tot / 3600), open("hera_scratch/fan_design.json", "w"))
