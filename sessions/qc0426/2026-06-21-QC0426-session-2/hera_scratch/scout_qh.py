import numpy as np, scipy.constants as cst
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, GateCalibration

r = open_run("data/6")
i = r.col("sr0_X") / (-1e6)
R1 = r.col("sr1_X") / i; R2 = r.col("sr2_X") / i; Rxy = r.col("sr3_X") / i
Vtg = r.col("DC_bias"); Vbg = r.col("k_2400_volt")
t = 15.6e-9
cal = GateCalibration.from_thicknesses(t, t/1.3091, 0.0,
        n_offset=-GateCalibration.from_thicknesses(t, t/1.3091, 0.0).n_D(0.174, 0.0)[0])
n = np.array([cal.n_D(Vtg[k], Vbg[k])[0] for k in range(len(Vtg))])
nu = n * cst.h / (cst.e * 7.95)

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(nu, R1/1e3, "o-", ms=3, label="Rxx sr1")
ax[0].plot(nu, R2/1e3, "s-", ms=3, label="Rxx sr2")
for v in (2, 4, 6, 8):
    ax[0].axvline(v, ls=":", c="grey", lw=0.7)
ax[0].set_xlabel("filling factor nu (=nh/eB, B=7.95T)"); ax[0].set_ylabel("Rxx [kohm]")
ax[0].set_title("Rxx vs nu: monotonic, NO QH minima at integer nu"); ax[0].legend()
ax[1].plot(nu, Rxy/1e3, "o-", ms=3, color="C3", label="Rxy measured")
nn = np.linspace(1, 8, 200); ax[1].plot(nn, 25.813/nn, "k--", lw=1, label="quantized h/nu e^2")
for v in (2, 4, 6, 8):
    ax[1].plot(v, 25.813/v, "k+", ms=10)
ax[1].set_xlabel("filling factor nu"); ax[1].set_ylabel("Rxy [kohm]")
ax[1].set_title("Rxy: classical slope, NO plateaus"); ax[1].legend()
fig.tight_layout(); fig.savefig("hera_scratch/scout_qh.png", dpi=110)
# weak-oscillation check: detrend Rxx vs nu
from numpy.polynomial import polynomial as P
bg = np.polyval(np.polyfit(nu, R1, 6), nu); dR = (R1 - bg)/1e3
print(f"Rxx detrended amplitude (max-min): {dR.max()-dR.min():.2f} kohm on ~{R1.mean()/1e3:.1f} kohm bg "
      f"=> {(dR.max()-dR.min())/(R1.mean()/1e3)*100:.0f}% modulation")
print("saved hera_scratch/scout_qh.png")
