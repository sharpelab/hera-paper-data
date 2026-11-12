# Gate C — the reduced read: ridge positions per leg, leakage, cap ratio.
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

def ridges(V, R, smooth=2.0, prom_frac=0.03):
    """Peaks in R(V) on a smoothed trace, parabolic-refined. Raw argmax is not
    good enough here: it moved ridge B's implied cap ratio from 0.958 to 0.873."""
    o = np.argsort(V); Vs, Rs = V[o], R[o]
    Rsm = gaussian_filter1d(Rs, smooth)
    idx, props = find_peaks(Rsm, prominence=prom_frac * np.ptp(Rsm))
    out = []
    for i, p in zip(idx, props["prominences"]):
        if 0 < i < len(Vs) - 1:
            y0, y1, y2 = Rsm[i-1], Rsm[i], Rsm[i+1]
            d = y0 - 2*y1 + y2
            shift = 0.5*(y0 - y2)/d if d else 0.0
            vpk = Vs[i] + shift*np.median(np.diff(Vs))
        else:
            vpk = Vs[i]
        out.append((vpk, Rsm[i], p))
    return Vs, Rsm, out

legs, peaks = {}, {}
fig, ax = plt.subplots(2, 4, figsize=(17, 7.5))
for k, rid in enumerate((0, 1, 2, 3)):
    r = run(rid)
    xcol = max([c for c in r.cols if c.endswith("_volt")], key=lambda c: np.ptp(r.col(c)))
    V = r.col(xcol)
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    R = r.col("sr1_X") / I
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    Vs, Rsm, pk = ridges(V, R)
    legs[rid], peaks[rid] = (xcol, V, R, itg, ibg), pk
    print(f"run {rid}  {xcol}  R_xx {R.min():.1f}-{R.max():.1f} ohm   "
          f"I_tg excess {np.abs(itg-itg[0]).max()*1e12:.0f} pA   "
          f"I_bg excess {np.abs(ibg-ibg[0]).max()*1e12:.0f} pA")
    for v, rr, p in pk:
        print(f"    RIDGE {xcol} = {v:+.4f} V   R = {rr:.1f} ohm   prominence {p:.1f} ohm")

    a = ax[0][k]
    a.plot(V, R, ".", ms=3, color="0.6"); a.plot(Vs, Rsm, "-", lw=1.2)
    for v, rr, p in pk:
        a.axvline(v, color="C3", ls="--", lw=0.9)
        a.annotate(f"{v:+.3f} V\n{rr:.0f} $\Omega$", (v, rr), textcoords="offset points",
                   xytext=(4, 6), fontsize=8, color="C3")
    a.set_xlabel(f"{xcol} (V)"); a.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    a.set_title(f"run {rid}", fontsize=10); a.grid(alpha=0.3)

    a = ax[1][k]
    a.plot(V, itg*1e12, ".-", ms=2, lw=0.7, label="$I_{tg}$")
    a.plot(V, ibg*1e12, ".-", ms=2, lw=0.7, label="$I_{bg}$")
    a.axhline(0, color="k", lw=0.5)
    a.set_xlabel(f"{xcol} (V)"); a.set_ylabel("gate current (pA)")
    a.grid(alpha=0.3); a.legend(fontsize=7)
fig.suptitle("Gate C — vti-02, B = 0, $V_{si}$ = 0, T = 1.18 K, $I_{bias}$ = 49.2 nA")
fig.tight_layout(); plt.show()

# two-point cap ratio: a CNP line through (Vtg_i, 0) and (0, Vbg_i) has
# c_bg/c_tg = Vtg_i / Vbg_i
tg = sorted(v for v, _, _ in peaks[0] + peaks[1])
bg = sorted(v for v, _, _ in peaks[2] + peaks[3])
print(f"\nTG-axis ridges (V_bg=0): {['%+.4f' % v for v in tg]}")
print(f"BG-axis ridges (V_tg=0): {['%+.4f' % v for v in bg]}")
for vt, vb, name in zip(tg, bg, "AB"):
    print(f"  ridge {name}: (V_tg={vt:+.4f}, V_bg={vb:+.4f})  ->  c_bg/c_tg = {vt/vb:.4f}")
print(f"  geometry prior c_bg/c_tg = {t_bg/t_tg if False else 9.5/11:.4f}")
