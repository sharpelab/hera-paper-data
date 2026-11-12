# Run 4 — gatemap, full validator box, B = 0, Si = 0, 10 nA. Re-form (TSV, complete rows), CNP ridge, CNP-line fit, R(D) profile, D-line realization.
"""Gatemap re-form + CNP-ridge extraction + CNP-line fit (cnp-and-dline-calibration steps 0-4).
Usage: menv python hera_scratch/gatemap_ana.py <run_id> [--fit-rows lo hi]
Works on partial data (complete rows only).
"""
import numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, fan_grids, resistance_grids, GateCalibration, luttinger_frequency
from sharpelab_nb.gates import calc_gate_voltages

rid = 4
r = run(rid)
f = fan_grids(r)
rg = resistance_grids(f)
Vbg = f.slow                          # (nrows,)
Vtg = f.grid("k_2400_tg_volt")[0]     # (nfast,)
R = np.abs(rg.R["sr1"])               # (nrows, nfast)
I = rg.current
print(f"run {rid}: {f.nrows}/{len(r.meta['slow_setpoints'])} rows complete, nfast={f.nfast}, Vbg {Vbg.min():+.3f}..{Vbg.max():+.3f}, Vtg {Vtg.min():+.3f}..{Vtg.max():+.3f}")
print(f"R_xx: {np.nanmin(R):.1f}..{np.nanmax(R):.1f} Ohm | I_drain {np.nanmin(I)*1e9:.2f}..{np.nanmax(I)*1e9:.2f} nA")
sens = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["sensitivity"]["value"]
ib = r.meta["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"] / r.meta["measurement_config"]["bias_resistor"]
rfs = sens / ib
railed = (R > 0.9 * rfs)
print(f"sr1 full scale {rfs:.0f} Ohm; railed points: {railed.sum()} ({100*railed.mean():.1f}%)")
itg, ibg = f.grid("k_2400_tg_curr"), f.grid("k_2400_bg_curr")
print(f"gate currents: |I_tg| max {np.abs(itg).max()*1e12:.0f} pA, |I_bg| max {np.abs(ibg).max()*1e12:.0f} pA")

# --- ridge extraction per row (smoothed argmax, edge-clip guard, contrast guard, continuity) ---
Rs = gaussian_filter1d(R, sigma=1.5, axis=1)
idx = np.argmax(Rs, axis=1)
edge = (idx <= 1) | (idx >= f.nfast - 2)
vtg_ridge = Vtg[idx]
contrast = Rs[np.arange(f.nrows), idx] / np.median(Rs, axis=1)
CONTRAST_MIN = 1.5   # heuristic: rows whose peak is < 1.5x the row median have no locatable ridge (weak-gap D~0 rows)
rows_ok = ~edge & (contrast >= CONTRAST_MIN)
# seed the line on the highest-contrast rows (the strong, in-box part of the ridge), then accept rows near it:
# a parallel/secondary feature (or a ridge that has left the box) has no vote.
seed = np.zeros(f.nrows, bool); seed[np.argsort(-np.where(rows_ok, contrast, 0))[:12]] = True
p = np.polyfit(Vbg[seed], vtg_ridge[seed], 1)
sel = rows_ok & (np.abs(vtg_ridge - np.polyval(p, Vbg)) < 0.08)
for _ in range(5):
    p = np.polyfit(Vbg[sel], vtg_ridge[sel], 1)
    res = vtg_ridge - np.polyval(p, Vbg)
    sig = max(np.std(res[sel]), 0.01)
    new = rows_ok & (np.abs(res) < 2.5 * sig)
    if np.all(new == sel): break
    sel = new
p = np.polyfit(Vbg[sel], vtg_ridge[sel], 1)
res = vtg_ridge[sel] - np.polyval(p, Vbg[sel])
slope, b = p
print(f"ridge rows: {(~edge).sum()} unclipped of {f.nrows}; {rows_ok.sum()} with contrast >= {CONTRAST_MIN}; {sel.sum()} kept after 2-sigma rejection (Vbg {Vbg[sel].min():+.2f}..{Vbg[sel].max():+.2f})")
print(f"CNP line (Vtg vs Vbg): Vtg = {slope:+.4f} * Vbg + {b:+.4f} ; rms residual {np.std(res)*1e3:.1f} mV ; ridge R at fit rows {np.median(R[np.arange(f.nrows)[sel], idx[sel]]):.0f} Ohm (median)")
print(f"  => c_bg/c_tg = {-slope:.4f} (geometry prior 0.8636 from 11 nm / 9.5 nm)")

# --- calibration: anchor c_tg at the stack prior, c_bg from the ratio; n_offset from the intercept ---
cal0 = GateCalibration.from_thicknesses(9.5e-9, 11e-9, 0)
c_tg = cal0.c_tg; c_bg = -slope * c_tg
n_off = -GateCalibration(c_tg, c_bg).density(b, 0.0)
cal = GateCalibration(c_tg, c_bg, n_offset=float(n_off))
n_chk = cal.density(np.polyval(p, Vbg[sel]), Vbg[sel])
print(f"calibrated: c_tg {c_tg:.4e} (prior), c_bg {c_bg:.4e} (ratio-calibrated), n_offset {n_off*1e-16:+.3f}e12 cm^-2; closure max|n| on ridge {np.abs(n_chk).max()*1e-16:.3f}e12")

# --- ridge R(D) along the fitted line: the gap minimum locates D = 0 physically (cnp-and-dline step 3, D offset) ---
vtg_line = np.polyval(p, Vbg)
R_line = np.array([np.interp(vtg_line[i], Vtg, Rs[i]) for i in range(f.nrows)])
inbox = (vtg_line >= Vtg.min()) & (vtg_line <= Vtg.max())
_, D_line = cal.n_D(vtg_line, Vbg)
D_line = D_line / 1e9
k = np.argmin(R_line[inbox]); D_min = D_line[inbox][k]
print("ridge R along fitted CNP line (D [V/nm] : R [Ohm]):", ", ".join(f"{d:+.2f}:{rr:.0f}" for d, rr in zip(D_line[inbox][::3], R_line[inbox][::3])))
print(f"ridge R minimum {R_line[inbox][k]:.0f} Ohm at D = {D_min:+.3f} V/nm (geometric D) -> candidate D_offset = {-D_min:+.3f} V/nm (so the gap minimum reads D = 0)")

# --- D = 0 line design, clipped to validators by dropping (sharpelab_nb.gates units: 1e12 cm^-2, V/nm) ---
TG = (-0.3, 1.0); BG = (-1.3, 2.0)
n_off12 = float(n_off) * 1e-16
ns = np.linspace(-3.0, 5.0, 801)
def realized(D0):
    vt_, vb_ = calc_gate_voltages(ns, D0 * np.ones_like(ns), c_tg, c_bg, n_offset=n_off12, D_offset=0.0)
    ok_ = (vt_ >= TG[0]) & (vt_ <= TG[1]) & (vb_ >= BG[0]) & (vb_ <= BG[1])
    return vt_, vb_, ok_
vt, vb, ok = realized(0.0)
if ok.any():
    print(f"D = 0 line realized: n {ns[ok].min():+.2f}..{ns[ok].max():+.2f} e12 cm^-2 (F_L {luttinger_frequency(ns[ok].min()*1e16):.1f} / {luttinger_frequency(ns[ok].max()*1e16):.1f} T); Vtg {vt[ok].min():+.3f}..{vt[ok].max():+.3f}, Vbg {vb[ok].min():+.3f}..{vb[ok].max():+.3f}")
for D0 in (0.05, -0.05, 0.1, -0.1, 0.2, -0.2):
    vt2, vb2, ok2 = realized(D0)
    if ok2.any(): print(f"D = {D0:+.2f} V/nm realized: n {ns[ok2].min():+.2f}..{ns[ok2].max():+.2f} e12")

# --- plots: raw map, ridge + fit overlay, (n, D) reprojection ---
fig, axs = plt.subplots(1, 3, figsize=(17, 5))
ax = axs[0]
pc = ax.pcolormesh(Vtg, Vbg, R, shading="nearest", cmap="viridis", vmin=0, vmax=np.nanpercentile(R, 99))
plt.colorbar(pc, ax=ax, label="R_xx sr1 [Ohm]"); ax.set_xlabel("V_tg [V]"); ax.set_ylabel("V_bg [V]"); ax.set_title(f"run {rid} raw R_xx ({f.nrows} rows)")
ax = axs[1]
pc = ax.pcolormesh(Vtg, Vbg, R, shading="nearest", cmap="viridis", vmin=0, vmax=np.nanpercentile(R, 99))
ax.plot(vtg_ridge[rows_ok], Vbg[rows_ok], "w.", ms=4, label="ridge (argmax)")
ax.plot(vtg_ridge[sel], Vbg[sel], "r.", ms=5, label="fit rows")
xx = np.array(BG); ax.plot(np.polyval(p, xx), xx, "r--", label=f"Vtg={slope:+.3f}Vbg{b:+.3f}")
ax.plot(vt[ok], vb[ok], "c-", lw=1, label="D=0 line")
ax.set_xlim(TG); ax.set_ylim(BG); ax.legend(fontsize=8, loc="upper right"); ax.set_xlabel("V_tg [V]"); ax.set_title("ridge + CNP-line fit")
ax = axs[2]
VT, VB = np.meshgrid(Vtg, Vbg)
n2, D2 = cal.n_D(VT, VB)
pc = ax.pcolormesh(n2*1e-16, D2/1e9, R, shading="nearest", cmap="viridis", vmin=0, vmax=np.nanpercentile(R, 99))
plt.colorbar(pc, ax=ax, label="R_xx [Ohm]"); ax.axhline(0, color="c", lw=0.8); ax.set_xlabel("n [1e12 cm^-2]"); ax.set_ylabel("D [V/nm]"); ax.set_title("(n, D) reprojection (ratio data-cal, scale prior)")
plt.tight_layout()
plt.show()
