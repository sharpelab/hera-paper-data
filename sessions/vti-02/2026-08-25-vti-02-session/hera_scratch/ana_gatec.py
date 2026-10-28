"""Gate C analysis: four gate-current-sanity-check legs.

Reads each leg off disk, checks gate leakage and channel health, and asks the
campaign question: is there a CNP inside the committed gate window?
"""
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import open_run, summarize_run

RUNS = [int(a) for a in sys.argv[1:]] or [0, 1, 2, 3]
BASE = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/data"


def leg(run_id):
    r = open_run(f"{BASE}/{run_id}")
    print("=" * 72)
    print(f"run {run_id}")
    print(summarize_run(r))
    cols = list(r.cols)
    print(f"  cols: {cols}")

    # swept gate = the *_volt column that actually varies most
    volt_cols = [c for c in cols if c.endswith("_volt")]
    spans = {c: np.ptp(r.col(c)) for c in volt_cols}
    xcol = max(spans, key=spans.get)
    V = r.col(xcol)

    I = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    Vxx = r.col("sr1_X")
    Rxx = Vxx / I

    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    T = r.col("T_sample") if "T_sample" in cols else None

    # health
    sens1 = 5e-4
    load = np.abs(Vxx) / sens1
    print(f"  swept: {xcol}  {V.min():+.4f} -> {V.max():+.4f} V, {len(V)} pts")
    print(f"  I         : {np.median(I):.4e} A  (min {I.min():.4e}, max {I.max():.4e})")
    print(f"  R_xx      : med {np.median(Rxx):8.2f}  min {Rxx.min():8.2f}  max {Rxx.max():8.2f} ohm")
    print(f"  sr1 load  : max {load.max():.3f} of full scale  "
          f"{'** RAILED **' if load.max() > 0.9 else 'ok'}")
    print(f"  I_tg      : baseline {itg[0]:+.3e}  excess max {np.abs(itg - itg[0]).max():.3e} A")
    print(f"  I_bg      : baseline {ibg[0]:+.3e}  excess max {np.abs(ibg - ibg[0]).max():.3e} A")
    if T is not None:
        print(f"  T_sample  : {T.min():.3f} - {T.max():.3f} K")
    for ch in ("sr2_X", "sr3_X"):
        if ch in cols:
            x = r.col(ch)
            print(f"  {ch:<9}: med {np.median(x):+.3e} V (n.c. pickup floor)")

    # CNP question: is R_xx rising toward either end, and by how much?
    imax = int(np.argmax(Rxx))
    print(f"  R_xx max at {xcol} = {V[imax]:+.4f} V  ->  {Rxx[imax]:.2f} ohm "
          f"({Rxx[imax]/np.median(Rxx):.2f}x median)")
    interior = 0 < imax < len(V) - 1
    print(f"  peak is {'INTERIOR (candidate CNP ridge crossing)' if interior else 'AT AN EDGE (no CNP crossed on this leg)'}")
    return dict(run=run_id, xcol=xcol, V=V, Rxx=Rxx, itg=itg, ibg=ibg, I=I, load=load)


legs = [leg(i) for i in RUNS]

fig, axes = plt.subplots(2, len(legs), figsize=(4.2 * len(legs), 7), squeeze=False)
for k, d in enumerate(legs):
    ax = axes[0][k]
    ax.plot(d["V"], d["Rxx"], ".-", ms=3, lw=0.8)
    ax.set_xlabel(f"{d['xcol']} (V)")
    ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {d['run']}: {d['xcol'].replace('k_2400_','').replace('_volt','')} "
                 f"0 → {d['V'][-1]:+g} V")
    ax.grid(alpha=0.3)

    ax = axes[1][k]
    ax.plot(d["V"], d["itg"] * 1e12, ".-", ms=3, lw=0.8, label="I_tg")
    ax.plot(d["V"], d["ibg"] * 1e12, ".-", ms=3, lw=0.8, label="I_bg")
    ax.set_xlabel(f"{d['xcol']} (V)")
    ax.set_ylabel("gate current (pA)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
fig.suptitle("Gate C — vti-02, B=0, V_si=0, T=1.18 K, I_bias=49.2 nA", y=0.99)
fig.tight_layout()
out = "C:/Users/DGG/VTI_local_data/zack/20260825-vti-02/hera_scratch/gatec.png"
fig.savefig(out, dpi=120)
print(f"\nwrote {out}")
