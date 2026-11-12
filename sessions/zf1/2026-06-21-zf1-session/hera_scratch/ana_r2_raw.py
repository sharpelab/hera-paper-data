import json
from scipy.ndimage import gaussian_filter1d, gaussian_filter
g = run(2); cfg = json.load(open(Path(file_path)/"2"/"metadata.json"))["measurement_config"]
N_bg, N_tg = 121, 81
TG = g.col("k_tg_volt").reshape(N_tg, N_bg)
BG = g.col("k_bg_volt").reshape(N_tg, N_bg)
I  = (g.col("sr830_1_X")/cfg["sr1_gain"]).reshape(N_tg, N_bg)
V4 = (g.col("sr830_3_X")/cfg["sr3_gain"]).reshape(N_tg, N_bg)
RXX = V4 / I                                   # 4T R via ACTUAL current

# (1) raw — Rxx(V_tg,V_bg) and the device current
fig, ax = plt.subplots(1, 3, figsize=(16, 5))
im = ax[0].pcolormesh(BG, TG, np.clip(RXX,0,150), shading='auto', cmap='inferno')
ax[0].set(title="4T Rxx (Ω, clip 150)", xlabel="BG (V)", ylabel="TG (V)"); plt.colorbar(im, ax=ax[0])
im = ax[1].pcolormesh(BG, TG, np.log10(np.clip(RXX,1,1e4)), shading='auto', cmap='inferno')
ax[1].set(title="log10 Rxx", xlabel="BG (V)"); plt.colorbar(im, ax=ax[1])
im = ax[2].pcolormesh(BG, TG, I*1e9, shading='auto', cmap='viridis')
ax[2].set(title="device I (nA) — drops where channel gaps", xlabel="BG (V)"); plt.colorbar(im, ax=ax[2])
plt.tight_layout(); plt.show()
print("diagonal CNP ridge (channel) + vertical ridge BG~0 (back-gated probe) + horizontal TG~0 (top-gated probe)")
