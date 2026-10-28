"""cnp-and-dline-calibration on gatemap run 5: per-row ridge extraction (two ridges), ratio fit on the
operating window near D = 0, offsets, closure check, realized D = 0 n-window; writes cal params to JSON."""
import json
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

rid = 5
g = fan_grids(str(Path(file_path) / str(rid))); rg = resistance_grids(g)
R = np.abs(rg.R["sr1"]); Vbg = g.slow
fs = g.meta["fast_setpoints"]; Vtg = np.asarray(fs[0] if isinstance(fs[0], list) else fs)
c_tg0 = stack_capacitance([(9.5, 3)]); c_bg0 = stack_capacitance([(11, 3)])
print(f"run {rid}: {g.nrows} rows x {g.nfast}; R {R.min():.0f}-{R.max():.0f} Ohm; prior c_bg/c_tg = {c_bg0/c_tg0:.3f}")

# ridge extraction: per row, up to two peaks; track continuity from the high-|D| end where ridge A is unambiguous
pts = []   # (Vbg, Vtg, R, ridge)
for i in range(g.nrows):
    r = gaussian_filter1d(R[i], 1.0)
    pk, _ = find_peaks(r, prominence=0.05 * (r.max() - r.min()) + 5)
    pk = [p for p in pk if 1 < p < g.nfast - 2]
    for p in sorted(pk, key=lambda p: -r[p])[:2]:
        pts.append((Vbg[i], Vtg[p], r[p]))
pts = np.array(pts)
# assign to ridges by distance to the high-D fit of ridge A (rows Vbg < -0.6), then refit each
selA = pts[:, 0] < -0.6
cfA0 = np.polyfit(pts[selA, 0], pts[selA, 1], 1)
dist = pts[:, 1] - np.polyval(cfA0, pts[:, 0])
ridgeA = pts[np.abs(dist) < 0.08]; ridgeB = pts[(dist < -0.08) & (dist > -0.45)]

def fit(p, lo, hi, label):
    m = (p[:, 0] >= lo) & (p[:, 0] <= hi)
    x, y = p[m, 0], p[m, 1]
    if len(x) < 4: print(f"{label}: {len(x)} rows, skip"); return None
    keep = np.ones(len(x), bool)
    for _ in range(3):
        cf = np.polyfit(x[keep], y[keep], 1); res = y - np.polyval(cf, x)
        keep = np.abs(res) < 2.5 * max(np.std(res[keep]), 0.01)
    cf = np.polyfit(x[keep], y[keep], 1); res = (y - np.polyval(cf, x))[keep]
    print(f"{label}: {keep.sum()}/{len(x)} rows, Vbg [{lo:+.2f},{hi:+.2f}]: Vtg = {cf[0]:+.4f} Vbg {cf[1]:+.4f}; "
          f"c_bg/c_tg = {-cf[0]:.3f}; rms {np.std(res)*1e3:.1f} mV")
    return cf

print("--- ridge A (main) ---")
cfA_all = fit(ridgeA, -2, 2, "A all rows")
cfA_hiD = fit(ridgeA, -2, -0.6, "A high-D rows")
cfA_op = fit(ridgeA, -0.5, 0.5, "A operating window |Vbg|<0.5")
print("--- ridge B (parallel, lower Vtg) ---")
cfB_all = fit(ridgeB, -2, 2, "B all rows")
cfB_op = fit(ridgeB, -0.5, 0.5, "B operating window")

# calibration: anchor c_tg at the prior (single hBN dielectric, better constrained), set c_bg from the operating-window ratio
cf = cfA_op if cfA_op is not None else cfA_all
ratio = -cf[0]; c_tg = c_tg0; c_bg = ratio * c_tg
n0, _ = calc_nD(cf[1], 0.0, c_tg, c_bg); n_offset = -n0
nA_ridge = calc_nD(np.polyval(cf, ridgeA[:, 0]), ridgeA[:, 0], c_tg, c_bg, n_offset=n_offset)[0]
print(f"\nCALIBRATION (ridge A, operating window): ratio {ratio:.3f} (prior {c_bg0/c_tg0:.3f}, {100*(ratio/(c_bg0/c_tg0)-1):+.0f}%), "
      f"c_tg {c_tg:.3e} F/m2 (prior anchor), c_bg {c_bg:.3e}; n_offset {n_offset:+.4f}e12; closure max|n| on fitted line {np.abs(nA_ridge).max():.3f}e12")
nB = calc_nD(ridgeB[:, 1], ridgeB[:, 0], c_tg, c_bg, n_offset=n_offset)[0] if len(ridgeB) else np.array([np.nan])
print(f"ridge B density offset relative to A: n_B = {np.nanmedian(nB):+.3f}e12 (std {np.nanstd(nB):.3f}), i.e. region B is {'hole' if np.nanmedian(nB)>0 else 'electron'}-doped vs A by {abs(np.nanmedian(nB)):.2f}e12")
# D = 0 line of region A: V_tg = (c_bg/c_tg) V_bg + V_tg0 where n=0 at ... use calc_gate_voltages
ns = np.linspace(-1.5, 4.5, 601); Vt, Vb = calc_gate_voltages(ns, np.zeros_like(ns), c_tg, c_bg, n_offset=n_offset)
ok = (Vt >= -0.3) & (Vt <= 1.0) & (Vb >= -1.3) & (Vb <= 2.0)
print(f"D = 0 line (region A) realized n-window inside validators: {ns[ok].min():+.2f} .. {ns[ok].max():+.2f} e12; "
      f"CNP at (Vtg, Vbg) = ({calc_gate_voltages(0,0,c_tg,c_bg,n_offset=n_offset)[0]:+.3f}, {calc_gate_voltages(0,0,c_tg,c_bg,n_offset=n_offset)[1]:+.3f})")
# D range along ridge A
DA = calc_nD(ridgeA[:, 1], ridgeA[:, 0], c_tg, c_bg, n_offset=n_offset)[1]
print(f"ridge A spans D = {DA.min():+.3f} .. {DA.max():+.3f} V/nm; peak R vs D: " +
      ", ".join(f"{d:+.2f}:{r:.0f}" for d, r in sorted(zip(np.round(DA, 2), ridgeA[:, 2]))[::6]))
json.dump({"run": rid, "ratio": ratio, "c_tg": c_tg, "c_bg": c_bg, "n_offset": n_offset, "D_offset": float(-D0_raw) if "D0_raw" in globals() else 0.0,
           "slope": cf[0], "intercept": cf[1], "window": "A |Vbg|<0.5", "nB_offset": float(np.nanmedian(nB))},
          open(Path(file_path).parent / "hera_scratch" / "cal_run5.json", "w"), indent=1)

fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
m = ax[0].pcolormesh(Vtg, Vbg, np.log10(R), shading="nearest", cmap="magma"); fig.colorbar(m, ax=ax[0], label="log10 |Rxx| (Ohm)")
ax[0].plot(ridgeA[:, 1], ridgeA[:, 0], "c.", ms=3, label="ridge A pts"); ax[0].plot(ridgeB[:, 1], ridgeB[:, 0], "g.", ms=3, label="ridge B pts")
xx = np.array([Vbg.min(), Vbg.max()])
ax[0].plot(np.polyval(cf, xx), xx, "w--", lw=1, label=f"A fit (op. window): slope {cf[0]:+.3f}")
if cfB_all is not None: ax[0].plot(np.polyval(cfB_all, xx), xx, "g--", lw=1, label=f"B fit: slope {cfB_all[0]:+.3f}")
ax[0].plot(Vt[ok], Vb[ok], "y:", lw=1.5, label="D = 0 (calibrated)")
ax[0].set_xlim(Vtg.min(), Vtg.max()); ax[0].set_ylim(Vbg.min(), Vbg.max()); ax[0].set_xlabel("V_tg (V)"); ax[0].set_ylabel("V_bg (V)")
ax[0].legend(fontsize=7, loc="upper right"); ax[0].set_title(f"run {rid} gatemap — ridges + calibration")
# (n, D) projection
N, D = calc_nD(Vtg[None, :], Vbg[:, None], c_tg, c_bg, n_offset=n_offset)
m2 = ax[1].pcolormesh(N, D, np.log10(R), shading="nearest", cmap="magma"); fig.colorbar(m2, ax=ax[1], label="log10 |Rxx|")
ax[1].axhline(0, color="y", ls=":", lw=1); ax[1].set_xlabel("n (1e12 cm^-2)"); ax[1].set_ylabel("D (V/nm)"); ax[1].set_title("(n, D) projection, region-A calibration")
fig.tight_layout(); plt.show()

# D_offset from the CNP-resistance symmetry in ±D (ridge A only, n within 0.1e12 of the fit line)
rows = []
for i in range(g.nrows):
    vc = cf[0] * Vbg[i] + cf[1]
    if vc < Vtg.min() + 0.03 or vc > Vtg.max() - 0.03: continue
    msk = np.abs(Vtg - vc) < 0.12
    r = gaussian_filter1d(R[i], 1.0); j = np.argmax(np.where(msk, r, -1))
    n_j, D_j = calc_nD(Vtg[j], Vbg[i], c_tg, c_bg, n_offset=n_offset)
    if abs(n_j) < 0.1: rows.append((D_j, r[j]))
rows = np.array(sorted(rows)); k = np.argmin(rows[:, 1]); sel = np.abs(rows[:, 0] - rows[k, 0]) < 0.12
cq = np.polyfit(rows[sel, 0], rows[sel, 1], 2); D0_raw = -cq[1] / (2 * cq[0])
print(f"R_CNP(D) minimum: {rows[k,1]:.0f} Ohm at raw D = {rows[k,0]:+.3f}; parabola vertex raw D = {D0_raw:+.4f} V/nm -> D_offset = {-D0_raw:+.4f}")
plt.figure(figsize=(5, 3.5)); plt.plot(rows[:, 0], rows[:, 1], "o-", ms=3); plt.axvline(D0_raw, color="r", ls="--")
plt.xlabel("raw D (V/nm)"); plt.ylabel("R_CNP ridge A (Ohm)"); plt.title("CNP resistance vs D — vertex = physical D = 0"); plt.show()
