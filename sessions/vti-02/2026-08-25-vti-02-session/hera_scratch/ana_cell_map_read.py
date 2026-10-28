# Run 4 — ridge extraction, the linearity test, and the (n, D) reprojection.
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

fg4 = fan_grids(run(4))
def G(name): return fg4.data[:, fg4.cols.index(name)].reshape(fg4.nrows, fg4.nfast)
rg4 = resistance_grids(fg4, channels=["sr1"])
Rm = np.abs(rg4.R["sr1"]); tgv = G("k_2400_tg_volt")[0]; vbv = G("k_2400_bg_volt")[:, 0]

def row_peaks(row, prom_frac=0.05, edge=3):
    y = gaussian_filter1d(row, 2.0)
    idx, pr = find_peaks(y, prominence=prom_frac * np.ptp(y))
    return [(tgv[i], y[i]) for i, p in zip(idx, pr["prominences"])
            if edge <= i < len(y) - edge]

# Ridge A simply does not exist below V_bg = -0.32: a second-derivative scan
# finds no shoulder in any row from -1.30 to -0.36. So assignment is by region,
# stated explicitly rather than by a tracker that can silently splice ridges.
Bp, Ap = [], []
for k in range(fg4.nrows):
    ps = row_peaks(Rm[k])
    if not ps:
        continue
    ps = sorted(ps)
    if vbv[k] <= -0.32:
        Bp.append((vbv[k], *max(ps, key=lambda p: p[1])))
    elif vbv[k] <= 0.02:
        Ap.append((vbv[k], *ps[0]))
        if len(ps) > 1:
            Bp.append((vbv[k], *ps[-1]))
    else:
        Ap.append((vbv[k], *max(ps, key=lambda p: p[1])))
Bp, Ap = np.array(Bp), np.array(Ap)

print("=== linearity test: a constant-n locus MUST be a straight line ===")
for nm, T in (("B", Bp), ("A", Ap)):
    x, y = T[:, 0], T[:, 1]
    r1 = y - np.polyval(np.polyfit(x, y, 1), x)
    r2 = y - np.polyval(np.polyfit(x, y, 2), x)
    h = len(x) // 2
    print(f"  ridge {nm}: linear rms {r1.std(ddof=1)*1e3:6.2f} mV | quad rms "
          f"{r2.std(ddof=1)*1e3:6.2f} mV | improvement {r1.std(ddof=1)/r2.std(ddof=1):.2f}x")
    if len(x) > 8:
        print(f"      slope low-V_bg half {np.polyfit(x[:h],y[:h],1)[0]:+.4f}  "
              f"vs high half {np.polyfit(x[h:],y[h:],1)[0]:+.4f}")

W = 0.45   # fit only over the operating window; the recipe's rule for curved ridges
cB4 = np.polyfit(Bp[np.abs(Bp[:,0])<=W,0], Bp[np.abs(Bp[:,0])<=W,1], 1)
cA4 = np.polyfit(Ap[np.abs(Ap[:,0])<=W,0], Ap[np.abs(Ap[:,0])<=W,1], 1)
print(f"\noperating-window slopes: ridge B {cB4[0]:+.4f} (c_bg/c_tg {-cB4[0]:.4f}), "
      f"ridge A {cA4[0]:+.4f} ({-cA4[0]:.4f});  geometry prior {-(-9.5/11):.4f}")

ratio = -cB4[0]
c_tg_v = cst.epsilon_0 * 3.0 / t_tg
c_bg_v = ratio * c_tg_v
nn = (c_tg_v*tgv[None,:] + c_bg_v*vbv[:,None])/cst.e*1e-16
DD = (c_tg_v*tgv[None,:] - c_bg_v*vbv[:,None])/(2*cst.epsilon_0)*1e-9
nB = (c_tg_v*Bp[:,1] + c_bg_v*Bp[:,0])/cst.e*1e-16
DB = (c_tg_v*Bp[:,1] - c_bg_v*Bp[:,0])/(2*cst.epsilon_0)*1e-9
nA = (c_tg_v*Ap[:,1] + c_bg_v*Ap[:,0])/cst.e*1e-16
DA = (c_tg_v*Ap[:,1] - c_bg_v*Ap[:,0])/(2*cst.epsilon_0)*1e-9

fig, ax = plt.subplots(1, 3, figsize=(19, 5.4))
pc = ax[0].pcolormesh(tgv, vbv, np.log10(Rm), shading="nearest", cmap="magma")
fig.colorbar(pc, ax=ax[0], label=r"$\log_{10} R_{xx}$")
ax[0].plot(Bp[:,1], Bp[:,0], "c.", ms=4, label="ridge B")
ax[0].plot(Ap[:,1], Ap[:,0], "s", ms=3, mfc="none", mec="lime", label="ridge A")
ax[0].set_xlabel(r"$V_{tg}$ (V)"); ax[0].set_ylabel(r"$V_{bg}$ (V)")
ax[0].set_title("gate map, log $R_{xx}$"); ax[0].legend(fontsize=8)

ax[1].plot(Bp[:,0], Bp[:,2], "o-", ms=4, label="ridge B")
ax[1].plot(Ap[:,0], Ap[:,2], "s-", ms=4, label="ridge A")
ax[1].set_yscale("log"); ax[1].set_xlabel(r"$V_{bg}$ (V)")
ax[1].set_ylabel(r"ridge $R_{xx}$ ($\Omega$)")
ax[1].set_title("ridge height — opposite D-dependence"); ax[1].grid(alpha=0.3); ax[1].legend(fontsize=8)

ax[2].plot(DB, nB, "o-", ms=4, label="ridge B")
ax[2].plot(DA, nA, "s-", ms=4, label="ridge A")
ax[2].axhline(0, color="k", lw=0.6, ls=":"); ax[2].axvline(0, color="k", lw=0.6, ls=":")
ax[2].set_xlabel(r"$D$ (V/nm)"); ax[2].set_ylabel(r"ridge $n$ ($10^{12}$ cm$^{-2}$)")
ax[2].set_title(f"ridge density vs $D$  ($c_{{bg}}/c_{{tg}}$={ratio:.3f})\n"
                "a constant-$n$ CNP is a horizontal line")
ax[2].grid(alpha=0.3); ax[2].legend(fontsize=8)
fig.tight_layout(); plt.show()
