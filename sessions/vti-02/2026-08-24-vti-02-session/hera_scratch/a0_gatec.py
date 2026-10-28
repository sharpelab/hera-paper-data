"""Scratch read of the Gate C liveness sweep (run 0): locate the CNP from the
two-terminal drain current, check leakage, check railing."""
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import open_run, summarize_run

rid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
here = Path(__file__).resolve().parent.parent
r = open_run(here / "data" / str(rid))

print(summarize_run(r))
print("\ncolumns:", r.cols)
print("comments:", r.meta.get("comments"))
mc = r.meta["measurement_config"]
print("meas_config:", {k: v for k, v in mc.items() if k != "comments"})

vbg = r.col("k_2400_bg_volt")
I = r.col("sr0_X") / mc["sr0_gain"]          # amps
Vxx = r.col("sr1_X")                          # raw volts (gain 1)
itg = r.col("k_2400_tg_curr")
ibg = r.col("k_2400_bg_curr")
T = r.col("T_sample")

Ibias = 10e-9
R2t = np.where(np.abs(I) > 1e-13, 1.0 / np.abs(np.where(I == 0, np.nan, I)), np.nan)

print(f"\nrows            : {len(vbg)}")
print(f"V_bg            : {vbg.min():+.3f} .. {vbg.max():+.3f} V")
print(f"I (drain)       : {I.min()*1e9:+.3f} .. {I.max()*1e9:+.3f} nA  (I_bias {Ibias*1e9:.1f} nA)")
print(f"|I| min         : {np.abs(I).min()*1e9:.4f} nA at V_bg = {vbg[np.argmin(np.abs(I))]:+.3f} V")
print(f"Vxx raw         : {Vxx.min()*1e6:+.4f} .. {Vxx.max()*1e6:+.4f} uV  (sens 2.00 uV -> rails ~2.18 uV)")
print(f"  frac railed   : {np.mean(np.abs(Vxx) > 0.95*2e-6):.2%}")
print(f"leak TG         : {itg.min()*1e12:+.1f} .. {itg.max()*1e12:+.1f} pA")
print(f"leak BG         : {ibg.min()*1e12:+.1f} .. {ibg.max()*1e12:+.1f} pA")
print(f"T_sample        : {T.min():.3f} .. {T.max():.3f} K")

# CNP = the minimum of |I| (max two-terminal resistance) at V_tg = 0
k = int(np.argmin(np.abs(I)))
print(f"\nCNP (min |I|)   : V_bg = {vbg[k]:+.4f} V, |I| = {abs(I[k])*1e9:.4f} nA, "
      f"R_2T = {1/abs(I[k]) if abs(I[k])>0 else np.inf:.4g} ohm (at I_bias-driven V unknown)")
print(f"I/I_bias at CNP : {abs(I[k])/Ibias:.4f}")
print(f"I/I_bias at ends: {abs(I[0])/Ibias:.4f} (V_bg={vbg[0]:+.2f})  "
      f"{abs(I[-1])/Ibias:.4f} (V_bg={vbg[-1]:+.2f})")

fig, ax = plt.subplots(4, 1, figsize=(8, 11), sharex=True)
ax[0].plot(vbg, I * 1e9, ".-", ms=3)
ax[0].axhline(Ibias * 1e9, ls=":", c="gray", label="I_bias 10 nA")
ax[0].axvline(vbg[k], ls="--", c="r", lw=0.8, label=f"min|I| @ {vbg[k]:+.3f} V")
ax[0].set_ylabel("I_drain (nA)"); ax[0].legend(fontsize=7)
ax[1].plot(vbg, np.abs(1 / np.where(I == 0, np.nan, I)) / 1e3, ".-", ms=3)
ax[1].set_ylabel("1/|I|  (GOhm per A)  ~ R_2T scale"); ax[1].set_yscale("log")
ax[2].plot(vbg, Vxx * 1e6, ".-", ms=3)
ax[2].axhline(2.0, ls=":", c="r"); ax[2].axhline(-2.0, ls=":", c="r")
ax[2].set_ylabel("sr1 X (uV)  [sens 2 uV]")
ax[3].plot(vbg, itg * 1e12, ".-", ms=3, label="TG")
ax[3].plot(vbg, ibg * 1e12, ".-", ms=3, label="BG")
ax[3].set_ylabel("gate leakage (pA)"); ax[3].set_xlabel("V_bg (V)"); ax[3].legend(fontsize=7)
for a in ax:
    a.axvline(vbg[k], ls="--", c="r", lw=0.6)
fig.suptitle(f"run {rid} — gatec-liveness, V_tg = 0, B = 0, T = base")
fig.tight_layout()
out = here / "hera_scratch" / f"a0_run{rid}.png"
fig.savefig(out, dpi=110)
print(f"\nwrote {out}")
