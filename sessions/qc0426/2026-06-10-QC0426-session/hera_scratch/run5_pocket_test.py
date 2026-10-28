"""ABA two-pocket test: model SdH frequencies vs measured FFT branches (run 5).

B=0 SWMcC H(k) with the ll_spectrum conventions (gamma3=gamma4=0, isotropic):
ML/BL pocket densities vs total n -> predicted f_ML(n), f_BL(n), f_tot(n).
Measured: tracked FFT peaks per n-column. Single global lever-arm gamma:
n_true = gamma * n_cap, fitted by matching f_tot.
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scipy.constants as cst

HBAR, E = cst.hbar, cst.e
A0 = 0.246e-9
g0, g1, g2, g5, delta = 3.1, 0.39, -0.028, 0.01, 0.021
v = np.sqrt(3) / 2 * A0 * (g0 * E) / HBAR

# 6x6 H(k), basis (A1,B1,A2,B2,A3,B3), eV
def bands(k):
    hk = HBAR * v * k / E  # eV
    H = np.zeros((6, 6))
    for s, e0 in [(1, delta), (2, delta), (5, delta)]:  # dimer sites B1,A2,B3
        H[s, s] = e0
    for a, b in [(0, 1), (2, 3), (4, 5)]:               # Dirac in each layer
        H[a, b] = H[b, a] = hk
    H[1, 2] = H[2, 1] = g1
    H[2, 5] = H[5, 2] = g1
    H[0, 4] = H[4, 0] = g2 / 2
    H[1, 5] = H[5, 1] = g5 / 2
    w, vec = np.linalg.eigh(H)
    # mirror parity weight: odd = ML. odd combos: (A1-A3), (B1-B3)
    P = np.zeros((2, 6))
    P[0, 0], P[0, 4] = 1 / np.sqrt(2), -1 / np.sqrt(2)
    P[1, 1], P[1, 5] = 1 / np.sqrt(2), -1 / np.sqrt(2)
    mlw = np.sum(np.abs(P @ vec) ** 2, axis=0)
    return w, mlw

ks = np.linspace(0, 0.6e9, 1200)
Es = np.zeros((len(ks), 6))
MLw = np.zeros((len(ks), 6))
for i, k in enumerate(ks):
    Es[i], MLw[i] = bands(k)

# electron side: for EF grid find k_F per band (bands rising with k)
EFs = np.linspace(0.001, 0.25, 400)
rows = []
for EF in EFs:
    n_ml = n_bl = 0.0
    for b in range(6):
        Eb = Es[:, b]
        if Eb[0] > EF or Eb[-1] < EF:
            # band may dip: find last crossing
            pass
        cross = np.where(np.diff(np.sign(Eb - EF)))[0]
        if len(cross) == 0:
            continue
        kF = ks[cross[-1]]
        dens = kF ** 2 / np.pi  # m^-2, 4-fold (spin x valley)
        if MLw[cross[-1], b] > 0.5:
            n_ml += dens
        else:
            n_bl += dens
    rows.append((n_ml + n_bl, n_ml, n_bl))
rows = np.array(rows)
ntot, nml, nbl = rows.T * 1e-16  # -> 1e12 cm^-2
f_of = lambda n12: 10.34 * n12   # T per 1e12 cm^-2 (4-fold)

# ---- measured branches: track FFT peaks ----
eps0 = 8.8541878128e-12
c_tg = eps0 * 3 / 15.6e-9
NF = 271
m = json.load(open(r"data/5/metadata.json"))
arr = np.loadtxt(r"data/5/data.tsv.gz")
cols = m["columns"]
nr = arr.shape[0] // NF
g = lambda nm: arr[: nr * NF, cols.index(nm)].reshape(nr, NF)
B = g("mag")[:, 0]
n12 = 2 * c_tg * g("DC_bias")[0] / E * 1e-16
I = g("sr0_X") / (-1e6)
R1 = np.abs(g("sr1_X") / I)
sel = (B >= 2.0) & (B <= 6.0)
invB = 1.0 / B[sel]
M = 512
u = np.linspace(invB.min(), invB.max(), M)
freqs = np.fft.rfftfreq(M, u[1] - u[0])
order = np.argsort(invB)
spec = np.zeros((NF, len(freqs)))
for j in range(NF):
    y = np.log10(np.maximum(R1[sel, j], 1))
    yi = np.interp(u, invB[order], y[order])
    yi -= np.polyval(np.polyfit(u, yi, 3), u)
    spec[j] = np.abs(np.fft.rfft(yi * np.hanning(M)))

from scipy.signal import find_peaks
meas = []  # (n_cap, f, amp)
for j in range(NF):
    if n12[j] < 2.0:
        continue
    fsel = (freqs > 4) & (freqs < 110)
    ss = spec[j][fsel]
    ff = freqs[fsel]
    pk, props = find_peaks(ss, prominence=0.12 * ss.max())
    for q in pk:
        meas.append((n12[j], ff[q], ss[q]))
meas = np.array(meas)

# global gamma from the requirement f_low+f_mid ~ f_tot is equivalent to
# matching the STRONG branch to model f_BL — fit gamma by least squares
# against all three branches simultaneously over a gamma grid.
gammas = np.linspace(0.75, 1.2, 91)
best = None
for gam in gammas:
    resid = 0.0
    cnt = 0
    for ncap, f, a in meas:
        ntr = gam * ncap
        i = np.argmin(np.abs(ntot - ntr))
        preds = np.array([f_of(nml[i]), f_of(nbl[i]), f_of(ntot[i])])
        resid += np.min((preds - f) ** 2) * a
        cnt += a
    if best is None or resid / cnt < best[1]:
        best = (gam, resid / cnt)
gam = best[0]
print(f"best global lever-arm gamma = {gam:.3f} (weighted rms {np.sqrt(best[1]):.1f} T)")

fig, ax = plt.subplots(figsize=(11, 6))
sc = ax.scatter(meas[:, 0], meas[:, 1], s=6 + 3 * meas[:, 2], c="k", alpha=0.5,
                label="measured FFT peaks")
ncap_ax = np.linspace(2, 8.2, 100)
ntr = gam * ncap_ax
fml = np.interp(ntr, ntot, f_of(nml))
fbl = np.interp(ntr, ntot, f_of(nbl))
ax.plot(ncap_ax, fml, "r-", lw=2, label="model f_ML (x gamma)")
ax.plot(ncap_ax, fbl, "b-", lw=2, label="model f_BL")
ax.plot(ncap_ax, fml + fbl, "g--", lw=2, label="model f_tot = f_ML + f_BL")
ax.set_xlabel(r"n_cap (10$^{12}$ cm$^{-2}$)")
ax.set_ylabel("SdH frequency (T)")
ax.set_ylim(0, 110)
ax.legend(fontsize=9)
ax.set_title(f"Run 5 — measured FFT peaks vs ABA two-pocket model, gamma={gam:.3f}")
fig.tight_layout()
fig.savefig(r"hera_scratch/run5_pocket_test.png", dpi=120)
print("saved hera_scratch/run5_pocket_test.png")

# pocket-share table
print("\nmodel pocket share along the fit:")
for nc in (3, 4, 5, 6, 7, 8):
    i = np.argmin(np.abs(ntot - gam * nc))
    print(f"  n_cap={nc}: n_true={ntot[i]:.2f}, ML {nml[i]:.2f} ({100*nml[i]/ntot[i]:.0f}%), "
          f"BL {nbl[i]:.2f} -> f_ML {f_of(nml[i]):.1f} T, f_BL {f_of(nbl[i]):.1f} T, "
          f"f_tot {f_of(ntot[i]):.1f} T")
