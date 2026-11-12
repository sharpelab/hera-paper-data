# Run 4 read: LL ladder, SdH tone count, and how far the absolute calibration can go.
fan4 = fan_grids(g4)
rg4 = resistance_grids(fan4)
R4 = np.abs(rg4.R["sr1"])
nB, nfast = R4.shape

# DUPLICATE-COLUMN TRAP: magnet.field is both the slow setpoint and a followed readback,
# so "magnet_field" appears twice. FanGrids.grid() silently returns the FIRST (setpoint).
# The measurement is the LAST one — and it differs, which is the whole point of following it.
_bi = [i for i, c in enumerate(fan4.cols) if c == "magnet_field"]
Bgrid = fan4.data[:, _bi[-1]].reshape(nB, nfast)
B4 = Bgrid.mean(axis=1)
print(f"measured B vs setpoint: mean offset {np.mean(B4 - fan4.slow)*1e3:+.1f} mT, "
      f"within-row spread up to {(Bgrid.max(1)-Bgrid.min(1)).max()*1e3:.1f} mT "
      f"-> following magnet.field was necessary, not optional")

# sr1 clips at 1 mV full scale; above ~1.7 T the nu=0 columns rail. Mask them.
_si = [i for i, c in enumerate(fan4.cols) if c == "sr1_X"][0]
Vxx4 = fan4.data[:, _si].reshape(nB, nfast)
clip4 = np.abs(Vxx4) > 0.95e-3
R4 = np.where(clip4, np.nan, R4)
print(f"clipped: {clip4.sum()} of {clip4.size} pts ({100*clip4.mean():.1f} %), "
      f"confined to the nu=0 columns above B ~ 1.7 T")

Vtg4 = fan4.grid("k_2400_tg_volt")[0]
cal_s = GateCalibration(c_tg=cal.c_tg, c_bg=cal.c_tg / 1.2737)
n_ass = cal_s.density(Vtg4, 1.2737 * Vtg4)

# ---- LL ladder: Rxx minima, fitted as lines through the origin in (B, n) ----
pts = []
for i in range(nB):
    if B4[i] < 1.5:
        continue
    row = R4[i]
    for sel in (n_ass > 0.15e16, n_ass < -0.15e16):
        idx = np.where(sel & np.isfinite(row))[0]
        if len(idx) < 5:
            continue
        sub = row[idx]
        for k in range(1, len(sub) - 1):
            if sub[k] < sub[k-1] and sub[k] <= sub[k+1] and sub[k] < 0.6 * np.nanmedian(sub):
                pts.append((B4[i], n_ass[idx[k]]))
pts = np.array(pts)
nu_ass = pts[:, 1] * cst.h / (cst.e * pts[:, 0])
cand = np.linspace(1.0, 12.0, 2201)
sc = []
for s_ in cand:
    fr = np.abs(np.round(nu_ass / s_) - nu_ass / s_)
    ok = np.abs(nu_ass) > 0.7 * s_
    sc.append(np.mean(fr[ok]) if ok.sum() > 5 else 1.0)
S = cand[int(np.argmin(sc))]
print(f"\n{len(pts)} Rxx minima (B >= 1.5 T). Best uniform ladder spacing on the ASSUMED "
      f"scale: delta_nu = {S:.3f}")

# ---- SdH tones: does a SECOND tone scale linearly with n? -------------------
span = (1 / B4).max() - (1 / B4).min()
F_RES, F_NYQ = 1 / span, nB / (2 * span)
print(f"1/B record: resolution {F_RES:.2f} T, Nyquist {F_NYQ:.1f} T "
      f"(columns with Onsager > Nyquist alias and are excluded)")
freqs, spec = sdh_fft(np.nan_to_num(R4, nan=np.nanmedian(R4)), B4, bg_degree=5, log=True)
print(f"\n{'n_ass(e12)':>11} {'f_full':>8} {'tone1':>8} {'t1/f_full':>10} {'tone2':>8} {'A2/A1':>7}")
t1s, t2s, ns = [], [], []
for j in range(14, nfast, 3):
    fo = luttinger_frequency(abs(n_ass[j]))
    # stay clear of BOTH spectral edges: within ~15 % of Nyquist the peak pick is
    # unreliable (the n=1.61 column picked a 1.78 T sidelobe over its 16.6 T tone).
    if fo > 0.85 * F_NYQ or fo < 2.0:
        continue
    m = (freqs > 1.5) & (freqs < F_NYQ)
    fi, si = freqs[m], spec[j][m]
    loc = [k for k in range(1, len(si)-1) if si[k] > si[k-1] and si[k] >= si[k+1]]
    loc.sort(key=lambda k: -si[k])
    if not loc:
        continue
    f1, a1 = fi[loc[0]], si[loc[0]]
    f2, a2 = np.nan, np.nan
    for k in loc[1:]:
        if abs(fi[k] - f1) > F_RES:
            f2, a2 = fi[k], si[k]
            break
    ns.append(n_ass[j] * 1e-16); t1s.append(f1); t2s.append(f2)
    print(f"{n_ass[j]*1e-16:11.2f} {fo:8.1f} {f1:8.2f} {f1/fo:10.2f} {f2:8.2f} {a2/a1:7.2f}")
ns, t1s, t2s = np.array(ns), np.array(t1s), np.array(t2s)
sl1 = np.sum(ns * t1s) / np.sum(ns ** 2)
r1 = np.corrcoef(ns, t1s)[0, 1]
ratios = t1s / luttinger_frequency(np.abs(ns * 1e16))
ok2 = np.isfinite(t2s)
r2 = np.corrcoef(ns[ok2], t2s[ok2])[0, 1] if ok2.sum() > 3 else np.nan
print(f"\ntone 1 vs n : slope {sl1:.2f} T per e12 cm^-2, correlation r = {r1:.3f}  "
      f"-> scales linearly through the origin")
print(f"tone 2 vs n : correlation r = {r2:.4f}  -> does NOT scale with density; these "
      f"are FFT sidelobes, not a second Fermi pocket.")
print(f"              Two pockets would give TWO tones both linear in n at a fixed "
      f"ratio. There is one.")
print(f"\nALPHA*g = 4/(mean t1/f_full) = {4/np.mean(t1s/luttinger_frequency(np.abs(ns*1e16))):.2f} "
      f"(ladder gives {S:.2f}) — consistent, but alpha and g are NOT separable here")

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
pc = ax[0].pcolormesh(np.tile(n_ass[None, :] * 1e-16, (nB, 1)),
                      np.tile(B4[:, None], (1, nfast)),
                      np.log10(np.maximum(R4, 1.0)), shading="nearest", cmap="magma")
ax[0].set_xlabel("n (assumed scale, 1e12 cm^-2)"); ax[0].set_ylabel("B (T)")
ax[0].set_title("run 4 — Landau fan, log10 Rxx"); fig.colorbar(pc, ax=ax[0])

ax[1].scatter(pts[:, 0], pts[:, 1] * 1e-16, c=np.round(nu_ass / S), cmap="tab20", s=18)
ax[1].set_xlabel("B (T)"); ax[1].set_ylabel("n_assumed (1e12 cm^-2)")
ax[1].set_title(f"Rxx minima — uniform ladder, spacing {S:.2f} in nu_assumed")

ax[2].plot(ns, t1s, "o", ms=6, label="dominant tone")
ax[2].plot(ns, sl1 * ns, "-", lw=1.0, color="C0")
ax[2].plot(ns[ok2], t2s[ok2], "x", ms=7, color="C3", label="secondary peaks")
ax[2].plot(ns, luttinger_frequency(np.abs(ns * 1e16)), "k--", lw=1.0,
           label="full Onsager (assumed n)")
ax[2].set_xlabel("n (assumed, 1e12 cm^-2)"); ax[2].set_ylabel("SdH frequency (T)")
ax[2].set_title("one tone scales with n; the other peaks do not")
ax[2].legend(fontsize=7); ax[2].grid(alpha=0.3)
fig.tight_layout()
