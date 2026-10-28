"""Back-gate calibration fan (run 6): c_bg from ray slopes, CNP from convergence."""

import numpy as np, scipy.constants as cst

import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from hera.analysis import fan_grids, resistance_grids, open_run, summarize_run

BASE = file_path

RID = 6
FAST = "k_2400_bg_volt"; DNU = 4; SENS = 5e-4

r = run(RID); print(summarize_run(r))
fg = fan_grids(r)
def G(n): return fg.data[:, fg.cols.index(n)].reshape(fg.nrows, fg.nfast)
rg = resistance_grids(fg, channels=["sr1"])
R = np.abs(rg.R["sr1"]); x = G(FAST)[0]; B = G("magnet_field")[:, 0]
Vx = np.abs(G("sr1_X")); dx = x[1] - x[0]
print(f"{fg.nrows} rows, B = {B}, fast {FAST} {x[0]:+.3f}..{x[-1]:+.3f} ({len(x)} pts)")

def mins_of(row, prom=0.05, edge=3):
    y = gaussian_filter1d(np.log10(np.maximum(row, 1e-2)), 1.5)
    idx, _ = find_peaks(-y, prominence=prom*np.ptp(y))
    out = []
    for i in idx:
        if edge <= i < len(y)-edge:
            d = y[i-1]-2*y[i]+y[i+1]
            out.append(x[i] + (0.5*(y[i-1]-y[i+1])/d if d else 0)*dx)
    return np.array(sorted(out))

mn, clip = {}, {}
for k in range(fg.nrows):
    ci = np.where(Vx[k] > 0.9*SENS)[0]
    clip[k] = (x[ci.min()], x[ci.max()]) if len(ci) else (0.0, 0.0)
    mn[k] = mins_of(R[k])
    print(f"  B={B[k]:.1f} T  clip {clip[k][0]:+.2f}..{clip[k][1]:+.2f}  "
          f"minima: {' '.join(f'{v:+.3f}' for v in mn[k])}")

# track rays on the ELECTRON side (V_bg above the clipped CNP region)
order = np.argsort(-B)                      # descending B -> walk from high field
ks = [k for k in order if B[k] >= 2.0]
start = ks[0]
active = [[(B[start], v)] for v in mn[start] if v > clip[start][1] + 0.05]
for k in ks[1:]:
    cand = [v for v in mn[k] if v > clip[k][1] + 0.05]; used = set()
    for ray in active:
        b0, v0 = ray[-1]
        pred = v0 * (B[k]/b0)
        near = [v for v in cand if v not in used and abs(v-pred) < 0.16]
        if near:
            v = min(near, key=lambda v: abs(v-pred)); used.add(v); ray.append((B[k], v))
    for v in cand:
        if v not in used: active.append([(B[k], v)])
rays = [np.array(sorted(r_)) for r_ in active if len(r_) >= 3]
print(f"\n{len(rays)} rays with >= 3 rows")
fits = [np.polyfit(r_[:,0], r_[:,1], 1) for r_ in rays]
for r_, f in zip(rays, fits):
    print(f"  ray B={r_[0,0]:.0f}..{r_[-1,0]:.0f} ({len(r_)} pts): slope {f[0]:+.4f} V/T, "
          f"intercept {f[1]:+.4f} V")
if not rays: raise SystemExit
ic = np.array([f[1] for f in fits]); sl = np.array([f[0] for f in fits])
good = np.abs(ic - np.median(ic)) < 0.10
print(f"\n  V_CNP(bg) = {ic[good].mean():+.4f} +/- "
      f"{ic[good].std(ddof=1) if good.sum()>1 else 0:.4f} V  ({good.sum()}/{len(ic)} rays)")

ss = np.sort(sl[sl > 0])
if len(ss) >= 3:
    best = min(((np.mean((ss/(DNU*a) - np.round(ss/(DNU*a)))**2), a)
                for a in np.linspace(0.004, 0.060, 11201)
                if 1 <= np.round(ss/(DNU*a)).min() and np.round(ss/(DNU*a)).max() <= 20))
    mult = np.round(ss/(DNU*best[1])).astype(int); xx = DNU*mult
    alpha = float(np.sum(xx*ss)/np.sum(xx*xx))
    c_bg = cst.e**2/(cst.h*alpha)
    c_bg_prior = cst.epsilon_0*3.0/11e-9
    c_tg_meas = 2.5152e-3
    print(f"  ray slopes {np.array2string(ss, precision=4)}")
    print(f"  assigned nu {xx.tolist()}  slope/nu {np.array2string(ss/xx, precision=5)}")
    print(f"  alpha_bg = {alpha:.5f} V/(T*nu)")
    print(f"  c_bg = {c_bg:.4e} F/m^2  (prior {c_bg_prior:.4e}, ratio {c_bg/c_bg_prior:.3f})")
    print(f"  dn/dV_bg = {c_bg/cst.e*1e-4*1e-12:.4f} e12 cm^-2/V")
    print(f"  implied back-gate hBN = {cst.epsilon_0*3.0/c_bg*1e9:.2f} nm (card 11.00)")
    print(f"\n  >>> c_bg/c_tg (MEASURED) = {c_bg/c_tg_meas:.4f}   "
          f"(geometry prior 0.8636; zero-field ridge slopes gave 0.58-0.67)")
    vc = ic[good].mean()
    print(f"  reachable n on this cut: {(x[0]-vc)*c_bg/cst.e*1e-4*1e-12:+.2f} .. "
          f"{(x[-1]-vc)*c_bg/cst.e*1e-4*1e-12:+.2f} e12 cm^-2")

fig, ax = plt.subplots(1, 2, figsize=(14.5, 5.6))
pc = ax[0].pcolormesh(x, B, np.log10(R), shading="nearest", cmap="magma")
fig.colorbar(pc, ax=ax[0], label="log10 Rxx")
for r_, f in zip(rays, fits):
    ax[0].plot(r_[:,1], r_[:,0], "w.", ms=3)
    ax[0].plot(np.polyval(f, B), B, "c-", lw=0.6, alpha=0.7)
ax[0].axvline(ic[good].mean(), color="lime", ls="--", lw=1.3)
ax[0].set_xlim(x[0], x[-1]); ax[0].set_ylim(B.min(), B.max())
ax[0].set_xlabel("V_bg (V)"); ax[0].set_ylabel("B (T)")
ax[0].set_title("back-gate fan (descent 6->1 T)")
if len(ss) >= 3:
    ax[1].plot(xx, ss, "o", ms=7); ax[1].plot([0, xx.max()], [0, alpha*xx.max()], "-")
    ax[1].set_xlabel("filling factor nu"); ax[1].set_ylabel("ray slope (V/T)")
    ax[1].set_title(f"alpha_bg={alpha:.5f} -> dn/dV_bg={c_bg/cst.e*1e-4*1e-12:.3f}e12 cm^-2/V")
    ax[1].grid(alpha=0.3)
fig.tight_layout(); plt.show()
