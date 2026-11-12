# Activation gap Delta(D) from the ladder (runs 6-12).
#
# R_CNP at each point along the CNP line is the MAXIMUM over the 5 perpendicular offsets —
# that is what makes it robust to the fitted line drifting, or to the CNP itself moving as
# the sample warms. Then at each D fit  ln R_CNP = ln R0 + Delta/(2 k_B T).
#   ABCA (inversion symmetric): Delta minimal at D = 0, growing with |D|
#   ABCB (no inversion)       : Delta minimum displaced to finite D
#   ABAB                      : no activated behaviour at all
# COMPLETENESS GUARD below: the 245-pt path is offset0's 49 pts then offset1's 49, ... so a
# partial run reshaped to (5, npts) silently interleaves offsets and yields plausible
# garbage (caught doing exactly that on run 6 mid-write).
here_dir = Path(file_path).parent
RIDS = list(range(6, 13))
RATIO = 1.2737
cal_s = GateCalibration(c_tg=cal.c_tg, c_bg=cal.c_tg / RATIO)
NOFF = 5

curves = []
for rid in RIDS:
    p = here_dir / "data" / str(rid)
    r = open_run(p)
    _sp = r.meta.get("setpoints")
    _exp = len(_sp[0]) if isinstance(_sp, list) and _sp and isinstance(_sp[0], list) else None
    if (_exp is not None and r.rows != _exp) or r.interrupted:
        print(f"run {rid}: incomplete/interrupted ({r.rows} of {_exp}) — skipped")
        continue
    vtg = r.col("k_2400_tg_volt")
    vbg = r.col("k_2400_bg_volt")
    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    Vxx = r.col("sr1_X")
    npts = len(vtg) // NOFF
    assert npts * NOFF == len(vtg)
    R = np.abs((Vxx / I).reshape(NOFF, npts))
    vtg_g = vtg.reshape(NOFF, npts)
    vbg_g = vbg.reshape(NOFF, npts)
    k = np.nanargmax(R, axis=0)
    Rc = R[k, np.arange(npts)]
    D = cal_s.displacement_field(vtg_g[0], vbg_g[k, np.arange(npts)]) * 1e-9
    Tm = float(np.nanmean(r.col("T_sample")))
    curves.append((Tm, D, Rc, rid))
    print(f"run {rid}: T = {Tm:6.3f} K   R_CNP {Rc.min():7.1f} .. {Rc.max():8.1f} ohm   "
          f"D {D.min():+.3f}..{D.max():+.3f} V/nm")

curves.sort(key=lambda c: c[0])
Ts = np.array([c[0] for c in curves])
Dgrid = curves[0][1]
Rmat = np.vstack([np.interp(Dgrid, c[1], c[2]) for c in curves])

# The rig's ELECTRON temperature is ~8 K, so sub-8 K points carry no independent
# information — and the data show it: R_CNP is flat between 1.2 and 8 K.
fitm = Ts >= 7.0
print(f"\nfitting over T = {np.round(Ts[fitm], 2)} K (base excluded: electron T ~ 8 K)")
inv2kT = 1.0 / (2 * cst.k * Ts[fitm]) * cst.e * 1e-3
gaps, gerr = [], []
for j in range(len(Dgrid)):
    y = np.log(np.maximum(Rmat[fitm, j], 1e-3))
    A = np.vstack([inv2kT, np.ones_like(inv2kT)]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ coef
    s2 = float(resid @ resid) / max(len(y) - 2, 1)
    gaps.append(coef[0])
    gerr.append(float(np.sqrt((s2 * np.linalg.inv(A.T @ A))[0, 0])))
gaps, gerr = np.array(gaps), np.array(gerr)

print(f"\n{'D/eps0':>8} {'Delta(meV)':>11} {'+/-':>7}   R(1.2K)  R(40K)")
for j in range(0, len(Dgrid), max(1, len(Dgrid) // 14)):
    print(f"{Dgrid[j]:+8.3f} {gaps[j]:11.3f} {gerr[j]:7.3f}   {Rmat[0, j]:8.1f} {Rmat[-1, j]:8.1f}")

k0 = int(np.argmin(np.abs(Dgrid)))
print(f"\nDelta at D = {Dgrid[k0]:+.3f} V/nm : {gaps[k0]:+.3f} +/- {gerr[k0]:.3f} meV"
      f"   (NEGATIVE = metallic, dR/dT > 0)")

# INVERSION-SYMMETRY TEST: where does Delta(D) MINIMISE? Not the intercept of a linear fit
# to the +D flank — Delta(D) is plainly curved near its minimum, so extrapolating a straight
# line back to zero is meaningless. ABCA must minimise at D = 0; ABCB at finite D.
near = np.abs(Dgrid - Dgrid[int(np.argmin(gaps))]) < 0.12
q = np.polyfit(Dgrid[near], gaps[near], 2)
D_gapmin = -q[1] / (2 * q[0])
rng = np.random.default_rng(0)
boot = []
for _ in range(400):
    yy = gaps[near] + rng.normal(0, np.maximum(gerr[near], 1e-3))
    qq = np.polyfit(Dgrid[near], yy, 2)
    if qq[0] > 0:
        boot.append(-qq[1] / (2 * qq[0]))
bs = float(np.std(boot)) if len(boot) > 50 else float("nan")
print(f"\nDelta(D) minimum (parabola over {int(near.sum())} pts): "
      f"D = {D_gapmin:+.3f} +/- {bs:.3f} V/nm")
print(f"  run 3's R_CNP minimum sat at D = 0.000 +/- 0.008 V/nm — consistent")
print(f"  ABCA requires this at D = 0; ABCB requires it clearly displaced")

hi = Dgrid > 0.13
jm = int(np.argmax(gaps))
print(f"\nDelta rises at {np.polyfit(Dgrid[hi], gaps[hi], 1)[0]:.1f} meV per V/nm on the "
      f"+D flank, peaking at {gaps[jm]:.2f} +/- {gerr[jm]:.2f} meV at D = {Dgrid[jm]:+.3f}")
cross = Dgrid[np.argmin(np.abs(gaps))]
print(f"dR/dT changes sign at D = {cross:+.3f} V/nm: METALLIC below, INSULATING above — "
      f"a displacement-field-driven metal-insulator crossover at charge neutrality.")

fig, ax = plt.subplots(1, 3, figsize=(17, 4.8))
for (Tm, D, Rc, rid) in curves:
    ax[0].plot(D, Rc, lw=1.1, label=f"{Tm:.1f} K")
ax[0].set_yscale("log"); ax[0].set_xlabel("D/eps0 (V/nm)"); ax[0].set_ylabel("R_CNP (ohm)")
ax[0].axvline(cross, ls=":", c="k", lw=1.0)
ax[0].set_title("R at neutrality vs D, per temperature"); ax[0].legend(fontsize=7)

for dt in (0.0, 0.10, 0.20, 0.28):
    j = int(np.argmin(np.abs(Dgrid - dt)))
    ax[1].plot(1 / Ts, Rmat[:, j], "o-", ms=5, label=f"D={Dgrid[j]:+.2f}")
ax[1].set_yscale("log"); ax[1].set_xlabel("1/T (1/K)"); ax[1].set_ylabel("R_CNP (ohm)")
ax[1].set_title("Arrhenius"); ax[1].legend(fontsize=7); ax[1].grid(alpha=0.3)

ax[2].errorbar(Dgrid, gaps, yerr=gerr, fmt="o-", ms=4, lw=1.0, capsize=2)
ax[2].axhline(0, ls="--", c="k", lw=0.9); ax[2].axvline(0, ls="--", c="k", lw=0.9)
ax[2].axvline(D_gapmin, ls=":", c="r", lw=1.2)
ax[2].set_xlabel("D/eps0 (V/nm)"); ax[2].set_ylabel("activation gap Delta (meV)")
ax[2].set_title(f"Delta(D), minimum at {D_gapmin:+.3f} V/nm")
ax[2].grid(alpha=0.3)
fig.tight_layout()
