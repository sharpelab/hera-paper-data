"""Scratch analysis of the CNP band map (multisweep rows of V_bg with a TG window).
usage: menv python hera_scratch/ana_band.py <run_id>
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run
from sharpelab_nb.gates import stack_capacitance, calc_nD

rid = int(sys.argv[1])
r = open_run(f"data/{rid}")
print(summarize_run(r))
mc = r.meta["measurement_config"]
vb = r.col("k_2400_bg_volt"); vt = r.col("k_2400_tg_volt")
I = r.col("sr0_X") / mc["sr0_gain"]; R = np.abs(r.col("sr1_X") / I)
c_tg = stack_capacitance([(9.5, 3)]); c_bg = stack_capacitance([(11, 3), (0, 3.9)])
rows = np.unique(vb)
print("V_bg   V_tg*    R_pk(Ω)  FWHM_tg(mV)  D_geo   n_pts")
out = []
for v in rows:
    m = np.isclose(vb, v)
    x, y = vt[m], R[m]
    j = np.argmax(y); xpk, ypk = x[j], y[j]
    half = ypk / 2 + np.min(y) / 2
    above = x[y >= half]
    fwhm = (above.max() - above.min()) * 1e3 if len(above) > 1 else np.nan
    edge = (j == 0) or (j == len(x) - 1)
    n, D = calc_nD(xpk, v, c_tg, c_bg)
    out.append((v, xpk, ypk, fwhm, D, edge, np.min(y)))
    print(f"{v:+.2f}  {xpk:+.3f}  {ypk:7.0f}  {fwhm:6.0f}{'*' if edge else ' '}     {D:+.3f}  {m.sum()}")
out = np.array(out, dtype=float)
ok = out[:, 5] == 0
p = np.polyfit(out[ok, 0], out[ok, 1], 1)
print(f"CNP line refit (interior peaks): V_tg = {p[1]:+.4f} {p[0]:+.4f}*V_bg -> c_bg/c_tg = {-p[0]:.3f}")
imin = np.argmin(out[ok, 2]); print(f"R_CNP minimum {out[ok][imin,2]:.0f} Ω at V_bg={out[ok][imin,0]:+.2f}, V_tg={out[ok][imin,1]:+.3f} (D_geo {out[ok][imin,4]:+.3f})")
fig, ax = plt.subplots(1, 3, figsize=(17, 5))
ax[0].semilogy(out[ok, 4], out[ok, 2], "o-", label="R_peak"); ax[0].semilogy(out[~ok, 4], out[~ok, 2], "s", mfc="none", label="edge-clipped")
ax[0].semilogy(out[:, 4], out[:, 6], ".", color="gray", label="window min")
ax[0].set_xlabel("D (V/nm, geometry prior)"); ax[0].set_ylabel("R (Ω)"); ax[0].legend(); ax[0].set_title(f"run {rid} R_CNP(D)")
ax[1].plot(out[ok, 4], out[ok, 3], "o-"); ax[1].set_xlabel("D (V/nm)"); ax[1].set_ylabel("FWHM in V_tg (mV)"); ax[1].set_title("peak width")
for v in rows[::5]:
    m = np.isclose(vb, v); ax[2].plot(vt[m] - (p[1] + p[0] * v), R[m], lw=0.8, label=f"V_bg={v:+.2f}")
ax[2].set_xlabel("V_tg − V_tg,line (V)"); ax[2].set_ylabel("|Rxx| (Ω)"); ax[2].legend(fontsize=7); ax[2].set_title("cuts, line-centred")
fig.tight_layout(); fig.savefig(f"hera_scratch/run{rid}_band.png", dpi=100); print("saved")
np.save(f"hera_scratch/run{rid}_band_table.npy", out)
