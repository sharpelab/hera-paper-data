# nu-line extraction and absolute n calibration (same as hera_scratch/ana_fan_nu.py)
import scipy.constants as cst
from scipy.signal import argrelmin
from sharpelab_nb.gates import stack_capacitance, calc_nD
mc = g.meta["measurement_config"]
vt, vb, B = g.col("k_2400_tg_volt"), g.col("k_2400_bg_volt"), g.col("magnet_field")
I = g.col("sr0_X") / mc["sr0_gain"]; R = np.abs(g.col("sr1_X") / I)
nfast = len(g.meta["fast_setpoints"][0]); nrows = len(R) // nfast
c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3), (0, 3.9)])
n_geo, _ = calc_nD(vt, vb, c_tg, c_bg)
Rg = R[:nrows*nfast].reshape(nrows, nfast); Bg = B[:nrows*nfast].reshape(nrows, nfast); ng = n_geo[:nrows*nfast].reshape(nrows, nfast)
pts = []
for i in range(nrows):
    ls = np.convolve(np.log10(np.maximum(Rg[i], 1e-1)), np.ones(3)/3, mode="same")
    for j in argrelmin(ls, order=3)[0]:
        prom = max(ls[max(0, j-6):j+7]) - ls[j]
        if prom > 0.25 and 3 < j < nfast-4 and abs(ng[i, j]) > 0.12:
            pts.append((Bg[i, j], ng[i, j]))
pts = np.array(pts)
nu_geo = pts[:, 1] * 1e16 / (cst.e * pts[:, 0] / cst.h)
best = min(((sc, np.mean(np.minimum(np.abs(nu_geo*sc - np.round(nu_geo*sc/4)*4), 1.0)**2)) for sc in np.arange(0.7, 1.45, 0.005)), key=lambda t: t[1])
scale = best[0]; nu = nu_geo * scale
print(f"absolute n calibration from the nu fan: n = {scale:.3f} x n_geo (minima cluster at multiples of 4)")
for t in [-12, -8, -4, 4, 8, 12, 16, 20]:
    sel = np.abs(nu - t) < 1.2
    if sel.sum():
        print(f"  nu={t:+3d}: {sel.sum():3d} minima, B {pts[sel,0].min():.1f}-{pts[sel,0].max():.1f} T")
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
pm = ax[0].pcolormesh(ng*scale, Bg, np.log10(Rg), shading="nearest", cmap="magma"); fig.colorbar(pm, ax=ax[0], label="log10 |Rxx| (Ω)")
ax[0].plot(pts[:, 1]*scale, pts[:, 0], "c.", ms=2.5)
for t in [-12, -8, -4, 4, 8, 12, 16, 20]:
    bb = np.linspace(0.5, Bg.max(), 40); ax[0].plot(t*cst.e*bb/cst.h*1e-16, bb, "w--", lw=0.4)
ax[0].set_xlim((ng*scale).min(), (ng*scale).max()); ax[0].set_xlabel("n (1e12 cm^-2, calibrated)"); ax[0].set_ylabel("B (T)")
ax[0].set_title("run 6 — fan at D≈0, minima + ν lines")
i0 = np.argmin(np.abs(ng - 0.0), axis=1)
ax[1].semilogy(Bg[np.arange(nrows), i0], Rg[np.arange(nrows), i0], "o-")
ax[1].set_xlabel("B (T)"); ax[1].set_ylabel("R at ν=0 (Ω)"); ax[1].set_title("ν=0 growth — note dips ≈2.4 T and ≈7.2 T")
