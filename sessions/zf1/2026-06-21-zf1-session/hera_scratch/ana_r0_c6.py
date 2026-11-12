import json
from pathlib import Path
from scipy.ndimage import gaussian_filter1d

g = run(0)
print(summarize_run(g))
cfg = json.load(open(Path(file_path) / "0" / "metadata.json"))["measurement_config"]
Ibias = cfg["bias_voltage_1"] / cfg["bias_resistor"]
bg   = g.col_at(1)                         # swept k_bg_volt (recorded twice)
r2   = (g.col("sr830_2_X") / cfg["sr2_gain"]) / Ibias
r3   = (g.col("sr830_3_X") / cfg["sr3_gain"]) / Ibias
icur =  g.col("sr830_1_X") / cfg["sr1_gain"]   # device current (A)

# (1) raw
fig, ax = plt.subplots(3, 1, figsize=(6, 8), sharex=True)
ax[0].plot(bg, r2/1e3, '.-', ms=3); ax[0].set_ylabel("2T R (kΩ)")
ax[0].set_title(f"Run 0 — BG cut, TG=0, I_bias={Ibias*1e12:.0f} pA")
ax[1].plot(bg, r3, '.', ms=3, alpha=.5); ax[1].set_ylabel("4T R (Ω)"); ax[1].axhline(0, c='gray', lw=.5)
ax[2].plot(bg, icur*1e12, '.-', ms=3); ax[2].set_ylabel("I (pA)"); ax[2].set_xlabel("BG (V)")
plt.tight_layout(); plt.show()
