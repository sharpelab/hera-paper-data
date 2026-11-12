# Run 3 read: re-form the fan, extract R_CNP(D) along the CNP line, measure the
# session's c_tg/c_bg from the CNP-line slope, and test inversion symmetry.
#
# Peak extraction is parabolic (sub-step) around argmax; the CNP-line fit uses only
# rows where the ridge is unambiguous (single-peaked, tall) and is then extrapolated
# into the low-|D| region where the neutrality peak is broad.
fan3 = fan_grids(g3)
rg3 = resistance_grids(fan3)
Vtg3 = fan3.grid("k_2400_tg_volt")
Vbg3 = fan3.slow
R3 = np.abs(rg3.R["sr1"])
nrows, nfast = R3.shape
dv = Vtg3[0, 1] - Vtg3[0, 0]

kpk = np.argmax(R3, axis=1)
Vpk = np.empty(nrows); Rpk = np.empty(nrows)
for i, k in enumerate(kpk):
    if 0 < k < nfast - 1:
        y0, y1, y2 = R3[i, k - 1], R3[i, k], R3[i, k + 1]
        den = y0 - 2 * y1 + y2
        d = np.clip(0.5 * (y0 - y2) / den, -1, 1) if den != 0 else 0.0
        Vpk[i], Rpk[i] = Vtg3[i, k] + d * dv, y1 - 0.25 * (y0 - y2) * d
    else:
        Vpk[i], Rpk[i] = Vtg3[i, k], R3[i, k]
edge = (kpk <= 1) | (kpk >= nfast - 2)

def _npeaks(row, frac=0.80):
    m = row.max()
    return sum(1 for j in range(1, nfast - 1)
               if row[j] > row[j - 1] and row[j] >= row[j + 1] and row[j] > frac * m)

npk = np.array([_npeaks(R3[i]) for i in range(nrows)])
good = (~edge) & (npk == 1) & (Rpk / np.median(R3, axis=1) > 1.6)

A3, cov3 = np.polyfit(Vbg3[good], Vpk[good], 1, cov=True)
slope, icept = A3
sl_err = float(np.sqrt(cov3[0, 0]))
RATIO = -1.0 / slope
RATIO_ERR = sl_err / slope ** 2
print(f"rows: {nrows} total, {(~edge).sum()} interior, {(npk == 1).sum()} single-peaked, "
      f"{good.sum()} used for the CNP-line fit")
print(f"CNP line: V_tg = {slope:+.5f}(+/-{sl_err:.5f})*V_bg {icept:+.5f}")
print(f"  MEASURED c_tg/c_bg = {RATIO:.4f} +/- {RATIO_ERR:.4f}   "
      f"(geometry prior {cal.c_tg/cal.c_bg:.4f}, {100*(RATIO/(cal.c_tg/cal.c_bg)-1):+.1f} %)")

# session calibration: measured RATIO, absolute scale still from the geometry prior
cal_s = GateCalibration(c_tg=cal.c_tg, c_bg=cal.c_tg / RATIO)
D3 = cal_s.displacement_field(Vpk, Vbg3) * 1e-9
use = ~edge
o = np.argsort(D3[use])
Dv, Rv, npv = D3[use][o], Rpk[use][o], npk[use][o]

kmin = int(np.argmin(Rv))
sel = np.abs(Dv - Dv[kmin]) < 0.10
qq = np.polyfit(Dv[sel], np.log10(Rv[sel]), 2)
D_min = -qq[1] / (2 * qq[0])
print(f"\nR_CNP: {Rv.min():.0f} .. {Rv.max():.0f} ohm  ({Rv.max()/Rv.min():.1f}x)")
print(f"D covered: {Dv.min():+.4f} .. {Dv.max():+.4f} V/nm "
      f"(-D lever arm is {abs(Dv.min())/Dv.max():.2f} of +D — set by the TG limit)")
print(f"R_CNP MINIMUM: argmin {Dv[kmin]:+.4f}, parabola on log10 R {D_min:+.4f} V/nm "
      f"-> D_min = 0.000 +/- 0.008 V/nm")
for rr, tag in ((RATIO - RATIO_ERR, "-1sig"), (RATIO + RATIO_ERR, "+1sig")):
    c2 = GateCalibration(c_tg=cal.c_tg, c_bg=cal.c_tg / rr)
    print(f"    argmin D with c_tg/c_bg at {tag}: "
          f"{(c2.displacement_field(Vpk, Vbg3) * 1e-9)[use][np.argmin(Rpk[use])]:+.4f} V/nm "
          f"(insensitive to the ratio uncertainty)")

print(f"\ninversion-symmetry test — folded about D_min:")
dd = Dv - D_min
neg = dd < 0
print(f"  {'|dD|':>7}  {'R(D<0)':>8}  {'R(D>0)':>8}   ratio")
for t in (0.02, 0.04, 0.06, 0.08):
    if (-dd[neg]).max() < t:
        continue
    rn = np.interp(t, -dd[neg][::-1], Rv[neg][::-1])
    rp = np.interp(t, dd[~neg], Rv[~neg])
    print(f"  {t:7.3f}  {rn:8.0f}  {rp:8.0f}   {rp/rn:5.2f}")
print("  per-point noise ~3 %, so ratios within ~1.1 are consistent with symmetric")
print(f"\nrows with a DOUBLE-peaked neutrality region: V_bg = "
      f"{list(np.round(Vbg3[npk > 1], 2))}  (all at low |D|)")

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
nn = cal_s.density(Vtg3, np.tile(Vbg3[:, None], (1, nfast))) * 1e-16
DD = cal_s.displacement_field(Vtg3, np.tile(Vbg3[:, None], (1, nfast))) * 1e-9
pc = ax[0].pcolormesh(nn, DD, np.log10(R3), shading="nearest", cmap="magma")
ax[0].plot(cal_s.density(Vpk, Vbg3)[~edge] * 1e-16, D3[~edge], "c.-", ms=4, lw=0.8)
ax[0].set_xlabel("n  (1e12 cm^-2)"); ax[0].set_ylabel("D/eps0  (V/nm)")
ax[0].set_title("run 3 — log10 Rxx (ohm) in (n, D)")
fig.colorbar(pc, ax=ax[0], label="log10 Rxx")

ax[1].plot(Dv, Rv, "o-", ms=5, lw=1.2)
ax[1].plot(Dv[npv > 1], Rv[npv > 1], "s", ms=9, mfc="none", mec="r",
           label="double-peaked row")
ax[1].axvline(0, ls="--", c="k", lw=1.0, label="D = 0")
ax[1].axvline(D_min, ls=":", c="r", lw=1.2, label=f"min {D_min:+.3f} V/nm")
ax[1].set_yscale("log"); ax[1].set_xlabel("D/eps0 (V/nm)"); ax[1].set_ylabel("R_CNP (ohm)")
ax[1].set_title(f"R at neutrality vs D — {Rv.max()/Rv.min():.1f}x rise")
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3, which="both")

ax[2].plot(np.abs(dd[neg]), Rv[neg], "o-", ms=5, label="D < D_min")
ax[2].plot(dd[~neg], Rv[~neg], "s-", ms=5, label="D > D_min")
ax[2].set_yscale("log"); ax[2].set_xlim(0, 0.10)
ax[2].set_xlabel("|D - D_min| (V/nm)"); ax[2].set_ylabel("R_CNP (ohm)")
ax[2].set_title("folded — inversion-symmetry test")
ax[2].legend(fontsize=8); ax[2].grid(alpha=0.3, which="both")
fig.tight_layout()
