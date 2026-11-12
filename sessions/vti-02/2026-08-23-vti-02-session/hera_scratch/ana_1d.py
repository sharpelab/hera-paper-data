"""Scratch analysis of a 1D gate sweep run: R (up/down), I, phase, gate currents, T.
usage: menv python hera_scratch/ana_1d.py <run_id> [sr0_col_is_current]
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

rid = int(sys.argv[1])
r = open_run(f"data/{rid}")
print(summarize_run(r))
mc = r.meta["measurement_config"]
print("columns:", r.cols)
x = r.col(r.swept_axis)
sr0 = r.col("sr0_X")
# run 0 stored sr0 already gain-divided (fp gain -1e6); later runs store raw volts.
I = sr0 if abs(np.nanmedian(sr0)) < 1e-6 else sr0 / mc["sr0_gain"]
V = r.col("sr1_X")
Vy = r.col("sr1_Y")
R = V / I
P = r.col("sr0_P")
itg = r.col("k_2400_tg_curr")
ibg = r.col("k_2400_bg_curr")
T = r.col("T_sample")
print(f"I_drain: med {np.median(I)*1e9:.3f} nA  min {I.min()*1e9:.3f} max {I.max()*1e9:.3f}; phase med {np.median(P):.1f}")
print(f"Rxx: med {np.median(R):.1f}  min {R.min():.1f}  max {R.max():.1f} Ohm;  |Y|/|X| med {np.median(np.abs(Vy)/np.abs(V)):.2f}")
print(f"I_tg: med {np.median(itg)*1e12:.0f} pA, std {np.std(itg)*1e12:.0f}; I_bg: med {np.median(ibg)*1e12:.0f} pA, std {np.std(ibg)*1e12:.0f}")
print(f"T_sample: {T.min():.3f}-{T.max():.3f} K")
# split into monotonic legs
dx = np.sign(np.diff(x)); legs = np.split(np.arange(len(x)), np.where(np.diff(dx) != 0)[0] + 1)
fig, ax = plt.subplots(4, 1, figsize=(9, 11), sharex=True)
for k, leg in enumerate(legs):
    if len(leg) < 5: continue
    ax[0].plot(x[leg], np.abs(R[leg]), lw=0.8, label=f"leg {k} ({'up' if dx[leg[0]]>0 else 'down'})")
ax[0].set_ylabel("|Rxx| (Ohm)"); ax[0].legend(fontsize=8)
ax[1].plot(x, I*1e9, lw=0.8); ax[1].set_ylabel("I_drain (nA)")
ax[2].plot(x, P, lw=0.8); ax[2].set_ylabel("sr0 phase (deg)")
ax[3].plot(x, itg*1e12, lw=0.8, label="I_tg"); ax[3].plot(x, ibg*1e12, lw=0.8, label="I_bg"); ax[3].set_ylabel("gate I (pA)"); ax[3].legend()
ax[3].set_xlabel(r.swept_axis)
fig.suptitle(f"run {rid} — {r.recipe}")
fig.tight_layout(); fig.savefig(f"hera_scratch/run{rid}_1d.png", dpi=110)
print("saved", f"hera_scratch/run{rid}_1d.png")
