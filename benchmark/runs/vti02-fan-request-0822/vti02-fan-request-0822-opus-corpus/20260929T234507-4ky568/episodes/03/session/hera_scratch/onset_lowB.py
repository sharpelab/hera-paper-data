"""Run 6 low-field: where does the 7.25 T tone actually die, and where is the grid trustworthy?

The run-6 B grid is 50 mT below 1 T and 10 mT above. A 7.25 T tone has
1/B period 0.138 T^-1; the 50 mT leg samples 1/B at 0.05/B^2 -> the low leg
is aliased below ~1 T. So read the onset twice: over the whole record, and
over the trustworthy 10 mT leg only.
"""
import numpy as np, warnings, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset

I_BIAS = 10e-9
r = open_run("data/6")
B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS
o = np.argsort(B); B, R = B[o], R[o]

dinvB = np.abs(np.diff(1.0 / B[B > 0.05]))
Bm = B[B > 0.05][:-1]
for probe in (0.3, 0.5, 0.7, 0.9, 1.0, 1.5, 3.0):
    i = np.argmin(abs(Bm - probe))
    print(f"  B={Bm[i]:.2f} T: d(1/B)={dinvB[i]:.4f} /T -> samples per 7.25T period = {0.1379/dinvB[i]:.1f}"
          f" ; Nyquist F_max = {1/(2*dinvB[i]):.1f} T")

print("\n--- onset over the full record (50 mT leg included, aliased) ---")
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    print(sdh_onset(R, B, b_lo=0.15, r_full_scale=5000.0).summary())
    for x in w: print("  [warn]", str(x.message)[:200])

print("\n--- onset over the trustworthy 10 mT leg only (B >= 1.0 T) ---")
m = B >= 1.0
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    s1 = sdh_onset(R[m], B[m], b_lo=1.0, r_full_scale=5000.0)
    print(s1.summary())
    for x in w: print("  [warn]", str(x.message)[:200])

# by-eye support: background-subtracted trace on the low leg
fig, ax = plt.subplots(2, 1, figsize=(11, 7))
mm = (B > 0.15) & (B < 2.0)
c = np.polyfit(B[mm], R[mm], 4)
ax[0].plot(B[mm], R[mm] - np.polyval(c, B[mm]), ".-", ms=3, lw=0.7)
ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("dRxx (Ohm)")
ax[0].set_title("run 6 low field, background removed (dots = actual samples; 50 mT below 1 T)")
ax[0].axvline(1.0, color="r", ls="--", label="10 mT leg starts"); ax[0].legend(fontsize=8)
ax[1].plot(1 / B[mm], R[mm] - np.polyval(c, B[mm]), ".-", ms=3, lw=0.7)
ax[1].set_xlabel("1/B (1/T)"); ax[1].set_title("same vs 1/B — periodicity visible where sampling supports it")
plt.tight_layout(); plt.savefig("hera_scratch/run6_lowB.png", dpi=110)
print("\nwrote hera_scratch/run6_lowB.png")
