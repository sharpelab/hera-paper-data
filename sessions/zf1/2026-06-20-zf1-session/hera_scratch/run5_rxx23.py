import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, GateCalibration

g = open_run("data/5")
mc = g.meta["measurement_config"]; Ib = mc["bias_voltage_1"]/mc["bias_resistor"]
vtg = g.col_at(g.col_indices("k_tg_volt")[-1])
vbg = g.col_at(g.col_indices("k_bg_volt")[-1])
R2 = (g.col("sr830_2_X")/mc["sr2_gain"])/Ib      # 4T Rxx (corrected channel)
R3 = (g.col("sr830_3_X")/mc["sr3_gain"])/Ib      # the small-signal channel

cal = GateCalibration.from_thicknesses(23.6e-9, 20e-9, 0)
# n offset from the full-map CNP (Vtg=icpt at Vbg=0); reuse icpt=0.082 from run2+3
n0,_ = cal.n_D(np.array([0.082]), np.array([0.0]))
nn, DD = cal.n_D(vtg, vbg); nn = (nn - n0[0])
print(f"run 5: B=0 ; Vtg {vtg.min():.3f}..{vtg.max():.3f} ; Vbg {vbg.min():.3f}..{vbg.max():.3f}")
print(f"n {nn.min()/1e4/1e12:.3f}..{nn.max()/1e4/1e12:.3f} e12 cm^-2 ; D {DD.mean()/1e9:.3f} V/nm (range {DD.min()/1e9:.3f}..{DD.max()/1e9:.3f})")
print(f"Rxx2 (sr2): {R2.min():.0f}..{R2.max():.0f} Ω, median {np.median(R2):.0f}")
print(f"Rxx3 (sr3): {R3.min():.1f}..{R3.max():.1f} Ω, median {np.median(R3):.1f}")

x = nn/1e4/1e12
fig, ax1 = plt.subplots(figsize=(9, 5.5))
fig.suptitle(f"Run 5 — density cut at B=0, D≈{DD.mean()/1e9:.2f} V/nm — Rxx2 vs Rxx3")
l1, = ax1.plot(x, R2/1e3, ".-", color="C0", label="Rxx2 = sr830_2 (4T, kΩ)")
ax1.set_xlabel("n (e12 cm$^{-2}$)"); ax1.set_ylabel("Rxx2 (kΩ)", color="C0"); ax1.tick_params(axis='y', labelcolor="C0")
ax2 = ax1.twinx()
l2, = ax2.plot(x, R3, ".-", color="C3", label="Rxx3 = sr830_3 (Ω)")
ax2.set_ylabel("Rxx3 (Ω)", color="C3"); ax2.tick_params(axis='y', labelcolor="C3")
ax1.legend(handles=[l1, l2], loc="best", fontsize=9)
ax1.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("hera_scratch/run5_rxx23.png", dpi=120)
print("saved hera_scratch/run5_rxx23.png")
