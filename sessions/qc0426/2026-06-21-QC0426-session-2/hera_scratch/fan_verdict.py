import sys
sys.path.insert(0, r"C:\Users\DGG\measurement_env\hera\models\trilayer_fs_count")
import numpy as np, scipy.constants as cst
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import fan_grids, resistance_grids, sdh_fft
import fs_count_b0 as fsc

fan = fan_grids("data/5"); ci = {c: i for i, c in enumerate(fan.cols)}
G = fan.data.reshape(fan.nrows, fan.nfast, len(fan.cols))
Bax = G[:, 0, ci["magnet_field"]]
rg = resistance_grids(fan); R1 = rg.R["sr1"]; R2 = rg.R["sr2"]
n_vec = np.linspace(0.5e16, 3.5e16, 40); F_L = cst.h / (4 * cst.e) * n_vec
order = np.argsort(Bax); Bs = Bax[order]
print(f"fan {fan.nrows} B-rows, B {Bs.min():.2f}..{Bs.max():.2f} T, full-res df~{1/(1/1.5-1/Bs.max()):.2f} T")

def fpk(R, cutoff=1.5, fmin=3.0):
    Rs = R[order, :]; f, mag = sdh_fft(Rs, Bs, b_range=(cutoff, Bs.max()), bg_degree=5)
    mag = np.asarray(mag)
    out = []
    for j in range(mag.shape[0]):
        sel = f > fmin; out.append(f[sel][np.argmax(mag[sel, ] if False else mag[j, sel])])
    return np.array(out)
F1 = fpk(R1); F2 = fpk(R2)

# Model Onsager curves (D=0): ABA ML+BL, ABC single — over the clean fan range
ns = np.linspace(1.5e16, 3.5e16, 16)
aba_lo, aba_hi, abc_f = [], [], []
for n in ns:
    try:
        _, fs = fsc.aba_fs(n); Fs = sorted(F for F, k in fs)
        aba_lo.append(Fs[0]); aba_hi.append(Fs[-1])
    except Exception as e:
        aba_lo.append(np.nan); aba_hi.append(np.nan)
    try:
        res = fsc.abc_fs(n); abc_f.append(res[4])
    except Exception:
        abc_f.append(np.nan)
aba_lo, aba_hi, abc_f = map(np.array, (aba_lo, aba_hi, abc_f))
print("model @ n=2.5e12: ABA(ML,BL)=(%.1f,%.1f)T  ABA sum=%.1f  ABC=%.1f  F_L=%.1f"
      % (np.interp(2.5e16, ns, aba_lo), np.interp(2.5e16, ns, aba_hi),
         np.interp(2.5e16, ns, aba_lo)+np.interp(2.5e16, ns, aba_hi),
         np.interp(2.5e16, ns, abc_f), cst.h/(4*cst.e)*2.5e16))

# Global rescale: best-fit single density scale so measured matches ABC curve
m = n_vec >= 1.5e16
def resc_cost(lam):  # measured F(n) vs ABC F(lam*n)
    pred = np.interp(lam*n_vec[m], ns, abc_f); return np.nanmean((F1[m]-pred)**2)
lams = np.linspace(0.8, 1.2, 41); lam = lams[np.argmin([resc_cost(l) for l in lams])]
print(f"best global density rescale (ABC fit) lambda={lam:.3f}")

fig, ax = plt.subplots(1, 2, figsize=(14, 5.5))
for a in ax:
    a.plot(ns/1e16, abc_f, "g-", lw=2, label="ABC (single pocket)")
    a.plot(ns/1e16, aba_hi, "b-", lw=1.5, label="ABA BL")
    a.plot(ns/1e16, aba_lo, "b--", lw=1.5, label="ABA ML")
    a.plot(n_vec/1e16, F_L, "k:", lw=0.8, label="F_L")
    a.plot(n_vec[m]/1e16, F1[m], "o", color="C3", ms=5, label="sr1 meas")
    a.plot(n_vec[m]/1e16, F2[m], "s", color="C1", ms=4, label="sr2 meas")
    a.set_xlabel("n [10^12 cm^-2]"); a.set_ylabel("F [T]")
ax[0].legend(fontsize=8); ax[0].set_title("Fan F(n) vs Onsager model (measured n)")
ax[1].plot(lam*n_vec[m]/1e16, F1[m], "D", color="C3", ms=5, label=f"sr1 (n x {lam:.2f})")
ax[1].legend(fontsize=8); ax[1].set_title(f"after global rescale lambda={lam:.2f}")
ax[1].set_xlim(0.5, 4)
fig.tight_layout(); fig.savefig("hera_scratch/fan_verdict.png", dpi=110)
print("saved hera_scratch/fan_verdict.png")

# Luttinger / partition diagnostic per column
print("\n n[e12]  F_L   sr1   sr2   sr1/F_L  (ABC: dom~F_L single; ABA: dom=BL<F_L + ML partner)")
for j in range(len(n_vec)):
    if n_vec[j] >= 1.5e16 and j % 3 == 0:
        print(f"  {n_vec[j]/1e16:.2f}  {F_L[j]:5.1f}  {F1[j]:5.1f}  {F2[j]:5.1f}   {F1[j]/F_L[j]:.2f}")
