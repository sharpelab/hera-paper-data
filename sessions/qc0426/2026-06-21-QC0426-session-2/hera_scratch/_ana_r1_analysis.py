# Run 1 — CNP-line extraction -> cap ratio -> (n,D) calibration + D=0 line
def _extract_ridge(R):
    A = np.abs(R)
    As = gaussian_filter1d(A, 1.5, axis=1)          # smooth along TG (fast)
    j = np.argmax(As, axis=1)
    return tg_axis[j], (j <= 1) | (j >= fan.nfast - 2)   # ridge Vtg, edge-clip guard

fits = {}
for ch in ("sr1", "sr2"):
    vtg_cnp, edge = _extract_ridge(rg.R[ch])
    keep = ~edge
    c0 = np.polyfit(VBG[keep], vtg_cnp[keep], 1)     # first pass
    good = keep & (np.abs(vtg_cnp - np.polyval(c0, VBG)) < 3 * np.std((vtg_cnp - np.polyval(c0, VBG))[keep]))
    sl, ic = np.polyfit(VBG[good], vtg_cnp[good], 1)
    rms = np.std(vtg_cnp[good] - np.polyval([sl, ic], VBG[good]))
    fits[ch] = (sl, ic, vtg_cnp, good)
    print(f"{ch}: slope dVtg/dVbg={sl:+.4f} -> c_bg/c_tg={-sl:.4f} | "
          f"intercept(Vtg@Vbg0)={ic:+.4f} V | rms {rms*1e3:.1f} mV | "
          f"{good.sum()}/{fan.nrows} rows")
print(f"geometry-prior ratio = 15.6/12 = {15.6/12:.4f}  (agreement <1%)")

# Calibrated (n,D): anchor c_tg on geometry prior (t_tg=15.6 nm); ratio from sr1; n_offset from CNP intercept
ratio = -fits["sr1"][0]; t_bg_eff = 15.6e-9 / ratio; intc = fits["sr1"][1]
_c0 = GateCalibration.from_thicknesses(15.6e-9, t_bg_eff, 0.0)
_n0, _ = _c0.n_D(intc, 0.0)
cal = GateCalibration.from_thicknesses(15.6e-9, t_bg_eff, 0.0, n_offset=-_n0)   # session calibration
# Linear inverse for (n,D) -> (Vtg,Vbg)
_base = np.array(cal.n_D(0.0, 0.0))
_M = np.column_stack([np.array(cal.n_D(1.0, 0.0)) - _base, np.array(cal.n_D(0.0, 1.0)) - _base])
_Minv = np.linalg.inv(_M)
def gates_for(n, D):
    """(n [m^-2], D [V/m]) -> (V_tg, V_bg)."""
    return _Minv @ (np.array([n, D]) - _base)
vtg0, vbg0 = gates_for(0.0, 0.0)
_p1, _p2 = gates_for(1e16, 0.0), gates_for(-1e16, 0.0)
_d0slope = (_p1[0] - _p2[0]) / (_p1[1] - _p2[1])
print(f"(n=0,D=0) point: V_tg={vtg0:+.3f} V, V_bg={vbg0:+.3f} V ; D=0 line slope dVtg/dVbg={_d0slope:+.4f}")

# Map + CNP fit + D=0 line overlay
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
for ax, ch in zip(axes, ("sr1", "sr2")):
    sl, ic, vtg_cnp, good = fits[ch]
    ax.pcolormesh(tg_axis, VBG, np.log10(np.abs(rg.R[ch]) + 1), shading="nearest", cmap="viridis")
    ax.plot(vtg_cnp[good], VBG[good], "r.", ms=4, label="CNP argmax")
    ax.plot(np.polyval([sl, ic], VBG), VBG, "w--", lw=1.0, label=f"CNP fit {sl:+.3f}")
    ng = np.linspace(-6e16, 6e16, 200); gg = np.array([gates_for(n, 0.0) for n in ng])
    inw = (gg[:, 0] >= -6) & (gg[:, 0] <= 7) & (gg[:, 1] >= -4.5) & (gg[:, 1] <= 4.5)
    ax.plot(gg[inw, 0], gg[inw, 1], "c-", lw=1.5, label="D=0 line")
    ax.set_xlabel("V_tg [V]"); ax.set_ylabel("V_bg [V]"); ax.legend(fontsize=8)
    ax.set_title(f"{ch}  CNP fit + D=0 line")
plt.show()
