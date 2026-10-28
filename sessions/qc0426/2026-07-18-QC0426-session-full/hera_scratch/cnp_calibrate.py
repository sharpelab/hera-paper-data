"""cnp-and-dline-calibration steps 3-4: conversion, closure, D=0 line design."""
import numpy as np
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages
from hera.analysis import GateCalibration, luttinger_frequency
import inspect

# fitted (per-channel, run 4): slope, intercept
fits = {"sr1": (-1.2817, 0.0484), "sr2": (-1.2887, 0.0543)}
slope = np.mean([f[0] for f in fits.values()])
b = np.mean([f[1] for f in fits.values()])
print(f"combined: slope {slope:+.4f}, intercept {b:+.4f} V")

# anchor: c_tg from the stack prior (15.6 nm hBN, single dielectric); c_bg from the fitted ratio
c_tg = stack_capacitance([(15.6, 3)])
ratio = -slope
c_bg = ratio * c_tg
c_bg_geom = stack_capacitance([(12, 3), (0, 3.9)])
print(f"c_tg (prior) = {c_tg:.4e} F/m^2; c_bg = ratio*c_tg = {c_bg:.4e} (geometry prior {c_bg_geom:.4e}, {100*(c_bg/c_bg_geom-1):+.1f}%)")

# density offset: n_offset so the fitted line maps to n = 0 (b = V_tg intercept at V_bg = 0)
# NB unit conventions: sharpelab_nb.gates works in 1e12 cm^-2 (= 1e16 m^-2) display
# units; GateCalibration is SI (m^-2). Convert explicitly.
n_offset_disp = -calc_nD(b, 0, c_tg, c_bg)[0]     # 1e12 cm^-2
n_offset_si = n_offset_disp * 1e16                 # m^-2
print(f"n_offset = {n_offset_disp:+.4f} e12 cm^-2 = {n_offset_si:.3e} m^-2")

cal = GateCalibration(c_tg=c_tg, c_bg=c_bg, n_offset=n_offset_si, D_offset=0.0)

# closure check: n along the fitted ridge (SI object)
vbg = np.linspace(-4.5, 4.5, 101)
vtg_ridge = slope * vbg + b
n_r, D_r = cal.n_D(vtg_ridge, vbg)
print(f"closure: max |n| along ridge = {np.abs(n_r).max()*1e-16:.4f} e12 cm^-2")

# D = 0 line: realized n-window inside validators (clip by dropping)
ns = np.linspace(-6, 6, 601)  # request +/- 6 e12 cm^-2 (display units)
vtg_l, vbg_l = calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_offset=n_offset_disp)
ok = (vtg_l >= -3.0) & (vtg_l <= 3.0) & (vbg_l >= -4.5) & (vbg_l <= 4.5)
print(f"D=0 line: realized n window [{ns[ok].min():.2f}, {ns[ok].max():.2f}] e12 cm^-2")
print(f"  at n_min: Vtg={vtg_l[ok][0]:+.3f}, Vbg={vbg_l[ok][0]:+.3f}; at n_max: Vtg={vtg_l[ok][-1]:+.3f}, Vbg={vbg_l[ok][-1]:+.3f}")
# roundtrip check (SI object)
n_rt, D_rt = cal.n_D(vtg_l[ok], vbg_l[ok])
print(f"roundtrip: max|D| = {np.abs(D_rt).max():.3e} V/m; n monotonic: {bool(np.all(np.diff(n_rt) > 0))}")

# Step 2 back-of-envelope: F_L at the realized window edges (luttinger_frequency takes SI m^-2)
print(inspect.signature(luttinger_frequency), inspect.getdoc(luttinger_frequency))
for n_edge in (ns[ok].min(), ns[ok].max()):
    FL = float(luttinger_frequency(abs(n_edge) * 1e16))
    print(f"n = {n_edge:+.2f} e12 cm^-2: F_L = {FL:.1f} T; Nyquist d(1/B) <= {1/(2*FL):.2e} /T")
