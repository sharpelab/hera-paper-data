import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

run = open_run("data/0")
print(summarize_run(run))
print("recipe:", run.recipe, " kind:", run.kind, " interrupted:", run.interrupted)

tg = np.asarray(run.col("DC_bias"))
I = np.asarray(run.col("sr0_X")) / 1e6          # |gain| 1e6 -> current (A)
def R(name):
    return np.asarray(run.col(name)) / I        # V / I
labels = {"sr1_X": "sr1 T3-T4", "sr2_X": "sr2 B4-B5", "sr3_X": "sr3 T5-B6 (Rxy)"}

fig, ax = plt.subplots(2, 1, figsize=(7, 7), sharex=True)
ax[0].plot(tg, I*1e9, ".-", ms=3)
ax[0].set_ylabel("I_meas (nA)"); ax[0].grid(alpha=.3)
ax[0].set_title("Run 0 — 1D CNP locator: TG sweep at BG=0, Si=0, B=0")
for nm, lab in labels.items():
    r = R(nm)
    ax[1].plot(tg, np.abs(r)/1e3, ".-", ms=3, label=f"{lab}: |R|")
ax[1].set_xlabel("V_tg (DC_bias, V)"); ax[1].set_ylabel("|R| (kohm)")
ax[1].legend(); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig("hera_scratch/cnp_locator_run0.png", dpi=110)

# CNP = argmax |Rxx| on the two four-terminal Rxx channels
for nm, lab in (("sr1_X","sr1 T3-T4"),("sr2_X","sr2 B4-B5")):
    r = np.abs(R(nm))
    k = int(np.argmax(r))
    print(f"{lab:14s}: CNP at V_tg={tg[k]:+.3f} V  |R|_max={r[k]/1e3:.2f} kohm  "
          f"|R|@edges=({r[0]/1e3:.2f},{r[-1]/1e3:.2f}) kohm  edge-clipped={k in (0,len(tg)-1)}")
print("I range (nA):", f"{I.min()*1e9:.2f} .. {I.max()*1e9:.2f}",
      " | leak BG max(A):", f"{np.abs(run.col('k_2400_curr')).max():.2e}",
      " Si max(A):", f"{np.abs(run.col('k_2410_curr')).max():.2e}")
