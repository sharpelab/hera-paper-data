# Run 5 — LL ray tracking: CNP from ray convergence, lever arm from ray slopes.
#
# Physics used and nothing else: LLs hold n = nu*eB/h, so at fixed V_bg a minimum
# sits at V_tg = V_CNP + nu*alpha*B with alpha = e^2/(h*c_tg). Every ray therefore
# passes through (V_CNP, B=0), and slopes are nu*alpha. Both readings are
# degeneracy-only: no band model, no assumed capacitance.
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

DNU, SENS = 4, 5e-4
fg5 = fan_grids(run(5))
def G5(n): return fg5.data[:, fg5.cols.index(n)].reshape(fg5.nrows, fg5.nfast)
rg5 = resistance_grids(fg5, channels=["sr1"])
Rf = np.abs(rg5.R["sr1"]); tgf = G5("k_2400_tg_volt")[0]; Bf = G5("magnet_field")[:, 0]
Vxf = np.abs(G5("sr1_X")); dvf = tgf[1] - tgf[0]

def mins_of(row, prom=0.05, edge=3):
    y = gaussian_filter1d(np.log10(np.maximum(row, 1e-2)), 1.5)
    idx, _ = find_peaks(-y, prominence=prom * np.ptp(y))
    out = []
    for i in idx:
        if edge <= i < len(y) - edge:
            d = y[i-1] - 2*y[i] + y[i+1]
            out.append(tgf[i] + (0.5*(y[i-1]-y[i+1])/d if d else 0)*dvf)
    return np.array(sorted(out))

mn, clip = {}, {}
for k in range(fg5.nrows):
    ci = np.where(Vxf[k] > 0.9*SENS)[0]
    clip[k] = tgf[ci.max()] if len(ci) else -0.30
    mn[k] = mins_of(Rf[k])

start = min(k for k in range(fg5.nrows) if Bf[k] >= 1.0)
active = [[(Bf[start], v)] for v in mn[start] if v > clip[start] + 0.05]
for k in range(start+1, fg5.nrows):
    cand = [v for v in mn[k] if v > clip[k] + 0.05]; used = set()
    for ray in active:
        b0, v0 = ray[-1]
        pred = v0 * (Bf[k]/b0)
        near = [v for v in cand if v not in used and abs(v-pred) < 0.09]
        if near:
            v = min(near, key=lambda v: abs(v-pred)); used.add(v); ray.append((Bf[k], v))
    for v in cand:
        if v not in used: active.append([(Bf[k], v)])
rays = [np.array(r_) for r_ in active if len(r_) >= 3]

fits = [np.polyfit(r_[:,0], r_[:,1], 1) for r_ in rays]
ic = np.array([f[1] for f in fits]); sl = np.array([f[0] for f in fits])
good = np.abs(ic - np.median(ic)) < 0.08          # one short 3-pt ray is an outlier
print(f"{len(rays)} rays; intercepts {np.array2string(ic, precision=4)}")
print(f"  V_CNP = {ic[good].mean():+.4f} +/- {ic[good].std(ddof=1):.4f} V "
      f"({good.sum()}/{len(ic)} rays; excluded {np.array2string(ic[~good], precision=3)})")
print(f"  zero-field ridges were A -0.203, B +0.113 -> the CNP is BETWEEN them")

ss = np.sort(sl[sl > 0])
best = min(((np.mean((ss/(DNU*a) - np.round(ss/(DNU*a)))**2), a)
            for a in np.linspace(0.004, 0.040, 7201)
            if 1 <= np.round(ss/(DNU*a)).min() and np.round(ss/(DNU*a)).max() <= 15))
mult = np.round(ss/(DNU*best[1])).astype(int); x = DNU*mult
alpha = float(np.sum(x*ss)/np.sum(x*x))
c_tg_m = cst.e**2/(cst.h*alpha); c_pri = cst.epsilon_0*3.0/t_tg
print(f"\n  ray slopes {np.array2string(ss, precision=4)}")
print(f"  assigned nu {x.tolist()}   slope/nu {np.array2string(ss/x, precision=5)}")
print(f"  alpha = {alpha:.5f} V/(T*nu)  -> c_tg = {c_tg_m:.4e} F/m^2 "
      f"({c_tg_m/c_pri:.3f}x prior), dn/dV_tg = {c_tg_m/cst.e*1e-4*1e-12:.3f}e12 cm^-2/V")
print(f"  implied top-gate hBN {cst.epsilon_0*3.0/c_tg_m*1e9:.2f} nm (card {t_tg*1e9:.2f})")
vc = ic[good].mean()
print(f"\n  reachable n on this cut: {(tgf[0]-vc)*c_tg_m/cst.e*1e-4*1e-12:+.2f}"
      f" .. {(tgf[-1]-vc)*c_tg_m/cst.e*1e-4*1e-12:+.2f} e12 cm^-2 "
      f"-- short of the |n| >~ 2-3e12 the templates need")

fig, ax = plt.subplots(1, 2, figsize=(14.5, 5.6))
pc = ax[0].pcolormesh(tgf, Bf, np.log10(Rf), shading="nearest", cmap="magma")
fig.colorbar(pc, ax=ax[0], label=r"$\log_{10}R_{xx}$")
for r_, f in zip(rays, fits):
    ax[0].plot(r_[:,1], r_[:,0], "w.", ms=3)
    ax[0].plot(np.polyval(f, Bf), Bf, "c-", lw=0.6, alpha=0.7)
ax[0].axvline(vc, color="lime", ls="--", lw=1.3)
for rv, cl in ((-0.2032, "0.5"), (0.1125, "0.5")):
    ax[0].axvline(rv, color=cl, ls=":", lw=1.0)
ax[0].set_xlim(tgf[0], tgf[-1]); ax[0].set_ylim(Bf.min(), Bf.max())
ax[0].set_xlabel(r"$V_{tg}$ (V)"); ax[0].set_ylabel("B (T)")
ax[0].set_title(f"LL rays converge at $V_{{CNP}}$={vc:+.3f} V\n"
                "(dotted = the two zero-field ridges)")
ax[1].plot(x, ss, "o", ms=7)
ax[1].plot([0, x.max()], [0, alpha*x.max()], "-")
ax[1].set_xlabel(r"filling factor $\nu$"); ax[1].set_ylabel("ray slope (V/T)")
ax[1].set_title(f"ray slopes are nu*alpha; alpha={alpha:.5f} V/(T nu) -> " f"dn/dV_tg = {c_tg_m/cst.e*1e-4*1e-12:.3f}e12 cm^-2/V")
ax[1].grid(alpha=0.3)
fig.tight_layout(); plt.show()
