import json, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

r = open_run("data/2")
print(summarize_run(r))
cfg = json.load(open("data/2/metadata.json"))["measurement_config"]
Ib = cfg["bias_voltage_1"]/cfg["bias_resistor"]

tg = r.col("k_tg_volt"); bg = r.col("k_bg_volt")
itg = r.col("k_tg_curr"); ibg = r.col("k_bg_curr")
icur = r.col("sr830_1_X")/cfg["sr1_gain"]              # device current (A)
r3 = (r.col("sr830_3_X")/cfg["sr3_gain"])/Ib           # 4T R (Ohm), nominal Ibias
n = len(tg)
print(f"\nrows so far: {n} pts")
print(f"LEAKAGE  |I_tg|max={np.nanmax(np.abs(itg)):.2e} A   |I_bg|max={np.nanmax(np.abs(ibg)):.2e} A")
print(f"  (>100 pA warn, >1 nA abort). I_tg@end={itg[-1]:.2e}  I_bg@end={ibg[-1]:.2e}")
print(f"device current: min={np.nanmin(icur)*1e12:.0f} pA  max={np.nanmax(icur)*1e12:.0f} pA  (I_bias={Ib*1e9:.2f} nA)")
print(f"4T R: min={np.nanmin(r3):.0f}  max={np.nanmax(r3):.0f} Ohm  median={np.nanmedian(r3):.0f}")

# partial 2D map of 4T (reshape what we have into full TG rows)
N_bg = 121
n_full = (n//N_bg)*N_bg
TG = tg[:n_full].reshape(-1, N_bg)
BG = bg[:n_full].reshape(-1, N_bg)
R3 = r3[:n_full].reshape(-1, N_bg)
ITG = itg[:n_full].reshape(-1, N_bg); IBG = ibg[:n_full].reshape(-1, N_bg)
print(f"reshaped {R3.shape[0]} complete TG rows")

fig, ax = plt.subplots(1, 3, figsize=(15, 5))
im0 = ax[0].pcolormesh(BG, TG, np.clip(R3, 0, 300), shading='auto', cmap='inferno')
ax[0].set_title("4T R (Ω, clip 300)"); ax[0].set_xlabel("BG (V)"); ax[0].set_ylabel("TG (V)"); plt.colorbar(im0, ax=ax[0])
im1 = ax[1].pcolormesh(BG, TG, np.abs(ITG)*1e12, shading='auto', cmap='viridis')
ax[1].set_title("|I_tg| leak (pA)"); ax[1].set_xlabel("BG (V)"); plt.colorbar(im1, ax=ax[1])
im2 = ax[2].pcolormesh(BG, TG, np.abs(IBG)*1e12, shading='auto', cmap='viridis')
ax[2].set_title("|I_bg| leak (pA)"); ax[2].set_xlabel("BG (V)"); plt.colorbar(im2, ax=ax[2])
plt.tight_layout(); plt.savefig("hera_scratch/ckpt_run2.png", dpi=100)
print("saved hera_scratch/ckpt_run2.png")
