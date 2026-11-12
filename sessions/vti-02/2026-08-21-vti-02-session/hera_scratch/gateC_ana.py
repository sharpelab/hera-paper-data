"""Gate C digest: per-leg liveness + leakage + timing from the run dirs.
Usage: menv python hera_scratch/gateC_ana.py <id> [<id> ...]
"""
import sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run

DATA = Path(__file__).resolve().parents[1] / "data"
ids = [int(a) for a in sys.argv[1:]]
fig, axs = plt.subplots(len(ids), 3, figsize=(14, 3.2 * len(ids)), squeeze=False)
for row, i in enumerate(ids):
    r = open_run(DATA / str(i))
    print(summarize_run(r))
    mc = r.meta.get("measurement_config", {})
    gain = float(mc.get("sr0_gain", -1e6))
    drive = r.meta.get("instruments", {}).get("sr1", {}).get("amplitude", None)
    ib = 1e-8 if drive is None else float(drive) / float(mc.get("bias_resistor", 1e8))
    x = r.col(r.swept_axis)
    t = r.col("time")
    dt = np.median(np.diff(t))
    itg = r.col("k_2400_tg_curr") if "k_2400_tg_curr" in r.cols else None
    ibg = r.col("k_2400_bg_curr") if "k_2400_bg_curr" in r.cols else None
    i0 = r.col("sr0_X") / gain
    v1 = r.col("sr1_X")
    rxx = v1 / ib
    T = r.col("T_sample") if "T_sample" in r.cols else None
    print(f"run {i}: axis={r.swept_axis} {x.min():+.3f}..{x.max():+.3f} V, rows={r.rows}, dt={dt:.3f} s/pt, interrupted={r.interrupted}")
    print(f"   I_drain(sr0): {np.nanmin(i0)*1e9:.3f}..{np.nanmax(i0)*1e9:.3f} nA (I_bias {ib*1e9:.1f} nA)")
    print(f"   Rxx(sr1):     {np.nanmin(rxx):.1f}..{np.nanmax(rxx):.1f} Ohm (sr1 X {np.nanmin(v1)*1e6:.2f}..{np.nanmax(v1)*1e6:.2f} uV); flat={np.allclose(v1, v1[0])}")
    for nm, arr in (("I_tg", itg), ("I_bg", ibg)):
        if arr is not None:
            print(f"   {nm}: |max|={np.nanmax(np.abs(arr))*1e12:.1f} pA, median={np.nanmedian(arr)*1e12:+.1f} pA, end={arr[-1]*1e12:+.1f} pA")
    if T is not None:
        print(f"   T_sample: {np.nanmin(T):.3f}..{np.nanmax(T):.3f} K")
    a = axs[row]
    a[0].plot(x, rxx); a[0].set_ylabel("Rxx sr1 [Ohm]"); a[0].set_title(f"run {i}: {r.swept_axis}")
    a[1].plot(x, i0 * 1e9); a[1].set_ylabel("I_drain sr0 [nA]")
    if itg is not None: a[2].plot(x, itg * 1e12, label="I_tg")
    if ibg is not None: a[2].plot(x, ibg * 1e12, label="I_bg")
    a[2].set_ylabel("gate I [pA]"); a[2].legend()
    for ax in a: ax.set_xlabel(r.swept_axis + " [V]")
plt.tight_layout()
out = Path(__file__).resolve().parent / f"gateC_{'_'.join(map(str, ids))}.png"
plt.savefig(out, dpi=90)
print("saved", out)
