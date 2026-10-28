import json
from scipy.ndimage import gaussian_filter1d

def _load(i):
    g = run(i)
    cfg = json.load(open(Path(file_path) / str(i) / "metadata.json"))["measurement_config"]
    Ib = cfg["bias_voltage_1"] / cfg["bias_resistor"]
    return g, cfg, Ib, g.col_at(1)

g1, c1, Ib1, bg1 = _load(1)
g0, c0, Ib0, bg0 = _load(0)
print(summarize_run(g1), "  I_bias =", Ib1)

R2_1 = (g1.col("sr830_2_X") / c1["sr2_gain"]) / Ib1
R3_1 = (g1.col("sr830_3_X") / c1["sr3_gain"]) / Ib1
R2_0 = (g0.col("sr830_2_X") / c0["sr2_gain"]) / Ib0

# (1) raw — 2T (run0 vs run1) and 4T (run1)
fig, ax = plt.subplots(2, 1, figsize=(6.5, 7), sharex=True)
ax[0].plot(bg0, R2_0/1e3, '.-', ms=2, label='2T run0 (40 pA)')
ax[0].plot(bg1, R2_1/1e3, '.-', ms=2, label='2T run1 (1 nA, railed)')
ax[0].set_ylabel("2T R (kΩ)"); ax[0].legend(); ax[0].set_title("Run 1 — 1 nA")
ax[1].plot(bg1, R3_1, '.-', ms=2, label='4T run1 (1 nA)'); ax[1].axhline(0, c='gray', lw=.5)
ax[1].set_ylabel("4T R (Ω)"); ax[1].set_xlabel("BG (V)"); ax[1].legend()
plt.tight_layout(); plt.show()

# (2) analysis — 4T SNR + CNP, 2T rail
R3s = gaussian_filter1d(R3_1, 2); ip = int(np.nanargmax(R3s))
noise = np.nanstd(R3_1[bg1 > 2.5])
print(f"4T CNP BG={bg1[ip]:+.3f} V  peak={R3s[ip]:.0f} Ω; metallic σ={noise:.2f} Ω -> SNR~{R3s[ip]/noise:.0f}")
print(f"2T run1 X flat at {np.median(g1.col('sr830_2_X'))*1e6:.1f} µV "
      f"(std {np.std(g1.col('sr830_2_X'))*1e9:.2f} nV) -> railed / over-range")
print(f"leak |I_tg|={np.nanmax(np.abs(g1.col('k_tg_curr'))):.1e}  "
      f"|I_bg|={np.nanmax(np.abs(g1.col('k_bg_curr'))):.1e} A")
