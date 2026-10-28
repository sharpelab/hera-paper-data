import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

run = open_run("data/0")
print(summarize_run(run))
print("cols:", run.cols)

bg = run.col_at(1)  # swept k_bg_volt (appears twice; idx 1)
Ibias = 0.004/1e8
# current channel: sr830_1 X / gain -> current (gain already current via Ithaco -1e6)
i_x = run.col("sr830_1_X")
# voltage channels: R = (X/gain)/Ibias
r2 = (run.col("sr830_2_X")/100.0)/Ibias
r3 = (run.col("sr830_3_X")/100.0)/Ibias
# raw 4T voltage in nV
v3_nV = (run.col("sr830_3_X")/100.0)*1e9
# leakage
itg = run.col("k_tg_curr"); ibg = run.col("k_bg_curr")

print(f"\nI(sr1) median={np.median(i_x):.3e}  (gain-divided current col)")
print(f"R2(2T) min={np.nanmin(r2):.0f}  max={np.nanmax(r2):.0f} Ohm  @CNP")
print(f"R3(4T) min={np.nanmin(r3):.0f}  max={np.nanmax(r3):.0f} Ohm")
print(f"V3(4T) raw: min={np.nanmin(v3_nV):.1f}  max={np.nanmax(v3_nV):.1f} nV")
print(f"leak: |I_tg|max={np.nanmax(np.abs(itg)):.2e}  |I_bg|max={np.nanmax(np.abs(ibg)):.2e} A")

# CNP location from 2T
icnp = int(np.nanargmax(r2))
print(f"\n2T CNP at BG={bg[icnp]:.3f} V  (R2={r2[icnp]:.0f} Ohm)")

# smooth 4T to see if a peak survives
from scipy.ndimage import gaussian_filter1d
r3s = gaussian_filter1d(r3, 3)
i3 = int(np.nanargmax(r3s))
print(f"4T smoothed peak at BG={bg[i3]:.3f} V  (R3s={r3s[i3]:.0f} Ohm)")
print(f"4T noise (std away from CNP, |BG|>2.5): {np.nanstd(r3[np.abs(bg)>2.5]):.0f} Ohm")

fig, ax = plt.subplots(3,1, figsize=(7,9), sharex=True)
ax[0].plot(bg, r2/1e3, '.-', ms=3); ax[0].set_ylabel("2T R (kΩ)"); ax[0].set_title("Run 0 — BG cut, TG=0, I_bias=40 pA")
ax[0].axvline(bg[icnp], color='r', ls=':', lw=1)
ax[1].plot(bg, r3, '.', ms=3, alpha=.4, label="raw"); ax[1].plot(bg, r3s, '-', color='k', label="smooth σ=3")
ax[1].set_ylabel("4T R (Ω)"); ax[1].legend(); ax[1].axhline(0, color='gray', lw=.5)
ax[2].plot(bg, i_x*1e12, '.-', ms=3); ax[2].set_ylabel("I sr1 (pA)"); ax[2].set_xlabel("BG (V)")
plt.tight_layout(); plt.savefig("hera_scratch/run0.png", dpi=110)
print("saved hera_scratch/run0.png")
