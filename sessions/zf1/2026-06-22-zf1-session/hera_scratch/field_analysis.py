import sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run

rid = sys.argv[1] if len(sys.argv)>1 else "6"
run = open_run(f"data/{rid}"); print(summarize_run(run)); print("interrupted:", run.interrupted)
# magnet_field appears twice: setpoint (swept) + measured (fp). Use measured (last).
mf_idx = [i for i,c in enumerate(run.cols) if c=="magnet_field"]
B_set = run.col_at(mf_idx[0])*1e3                       # mT (setpoint)
B = (run.col_at(mf_idx[-1]) if len(mf_idx)>1 else run.col_at(mf_idx[0]))*1e3   # mT (measured)
Iac = run.col("sr830_1_X")/(-1e6)
Rxx = np.abs((run.col("sr830_3_X")/100.0)/Iac)
T = run.col("T")*1e3
o=np.argsort(B); B,Rxx,T,B_set=B[o],Rxx[o],T[o],B_set[o]
print(f"T during sweep: {T.min():.1f}–{T.max():.1f} mK (base check: {'OK' if T.max()<60 else 'ELEVATED — increase settle'})")
print(f"B measured range: {B.min():.2f}–{B.max():.2f} mT (setpoint 0–80); remanence at setpoint-0 visible if B_min>0")

Rn = Rxx[np.abs(B)>0.7*B.max()].mean()                 # normal-state (high-B) Rxx
Rmin = Rxx.min(); Bmin = B[np.argmin(Rxx)]
print(f"normal-state Rxx (high B) = {Rn:.1f} Ω  (cf. run5 normal ~55–62 Ω)")
print(f"Rxx min = {Rmin:.2f} Ω at B = {Bmin:+.2f} mT  (effective-zero hint)")
half = 0.5*Rn
above = B[Rxx>=half]
Bc = above.min() if (above>0).any() else np.nan       # lowest +B reaching half-normal
print(f"B_c⊥ (Rxx=half-normal={half:.1f}Ω) ≈ {Bc:.1f} mT" + ("" if np.isfinite(Bc) and Bc<B.max() else "  -> not reached within range / >range"))
flat = np.std(Rxx[np.abs(B)>0.7*B.max()])/Rn
print(f"normal-state flatness (std/mean, high B) = {flat:.2f}  ({'flat -> field-kill clean' if flat<0.2 else 'sloping -> generic-MR caveat'})")

fig, ax = plt.subplots(1,2,figsize=(13,5))
ax[0].plot(B, Rxx, ".-", ms=4); ax[0].axhline(Rn,color="grey",ls=":",lw=.8,label=f"normal {Rn:.0f}Ω")
ax[0].axhline(half,color="orange",ls=":",lw=.8,label=f"half {half:.0f}Ω")
if np.isfinite(Bc): ax[0].axvline(Bc,color="r",ls="--",lw=.8,label=f"B_c⊥≈{Bc:.0f}mT")
ax[0].set_xlabel("B measured (mT)"); ax[0].set_ylabel("Rxx (Ω)"); ax[0].set_title(f"Run {rid}: field-kill Rxx(B) at SC optimum"); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot(B_set, T, ".-", ms=3, color="green"); ax[1].axhline(40,color="grey",ls=":",lw=.8)
ax[1].set_xlabel("B setpoint (mT)"); ax[1].set_ylabel("T (mK)"); ax[1].set_title("T during sweep (ramp-heating check)"); ax[1].grid(alpha=.3)
fig.tight_layout(); fig.savefig(f"hera_scratch/field_run{rid}.png", dpi=120)
print(f"saved hera_scratch/field_run{rid}.png")
