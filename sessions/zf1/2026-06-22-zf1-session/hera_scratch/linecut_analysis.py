import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

rid = sys.argv[1] if len(sys.argv)>1 else "3"
run = open_run(f"data/{rid}"); print(summarize_run(run)); print("interrupted:", run.interrupted)
lc = np.load("hera_scratch/linecut_vectors.npz")
Dl = lc["D"]; nl = lc["n"]; Ds = lc["Ds"]; Nexp = len(Dl)

I  = run.col("sr830_1_X")/(-1e6)
v3 = run.col("sr830_3_X")/100.0
Rxx = np.abs(v3/I)
itg = run.col("k_tg_curr"); ibg = run.col("k_bg_curr")
print(f"rows: {len(Rxx)} (expected {Nexp})")
print(f"leakage: |I_tg|max={np.abs(itg).max():.2e}  |I_bg|max={np.abs(ibg).max():.2e} A")
print(f"current: med={np.median(I)*1e9:.3f} nA min={I.min()*1e9:.3f}")

m = min(len(Rxx), Nexp)
Rxx, Dl2, nl2 = Rxx[:m], Dl[:m], nl[:m]
fig, ax = plt.subplots(figsize=(8,5))
print("\n--- per-D-line Rxx(n) ---")
for D0 in Ds:
    sel = np.isclose(Dl2, D0)
    if sel.sum()==0: continue
    n_s = nl2[sel]; R_s = Rxx[sel]; o = np.argsort(n_s)
    n_s, R_s = n_s[o], R_s[o]
    print(f"  D={D0:+.2f}: Rxx min={R_s.min():.1f} @ n={n_s[np.argmin(R_s)]:+.2f}e11 | med={np.median(R_s):.1f} | max={R_s.max():.1f} Ω")
    ax.plot(n_s, R_s, marker=".", ms=4, label=f"D={D0:+.2f}")
ax.set_xlabel("n (1e11 cm⁻²)"); ax.set_ylabel("R_4T (Ω)")
ax.set_title(f"Run {rid}: fine n-linecuts — Rxx(n) at fixed D")
ax.axhline(0, color="k", lw=0.5); ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(f"hera_scratch/linecut_run{rid}.png", dpi=120)
print(f"\nglobal Rxx min across all linecuts = {Rxx.min():.1f} Ω")
print(f"saved hera_scratch/linecut_run{rid}.png")
