# LK mass fit — runs 8-13, per branch (ML ~4.3, BL ~28, FL ~32.4), per channel
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from hera.analysis import open_run, sdh_fft

RUNS = [8, 9, 10, 11, 12, 13]
B_RANGE = (1.7, 8.0)
B_EFF = 2 / (1 / B_RANGE[0] + 1 / B_RANGE[1])   # 2.80 T (1/B-window harmonic mean)
ALPHA = 14.694                                   # X = ALPHA * (m*/me) * T / B

tones = {"ML": (4.3, 1.5), "BL": (28.0, 2.0), "FL": (32.4, 1.6)}
data = {ch: {k: [] for k in tones} for ch in ("sr1_X", "sr2_X")}
Ts = []
for fid in RUNS:
    r = open_run(f"data/{fid}")
    o = np.argsort(r.col("magnet_field"))
    B = r.col("magnet_field")[o]
    Ts.append(r.col("T_sample").mean())
    for ch in data:
        R = (r.col(ch) / 20e-9)[o]
        f, spec = sdh_fft(R[:, None], B, b_range=B_RANGE, log=False)
        s = spec[0]
        for k, (F0, w) in tones.items():
            m = (f > F0 - w) & (f < F0 + w)
            data[ch][k].append(s[m].max())
Ts = np.array(Ts)

def lk(T, m, A0):
    X = ALPHA * m * T / B_EFF
    return A0 * X / np.sinh(X)

print(f"B_eff = {B_EFF:.2f} T; rungs T = {np.round(Ts,2)}")
print(f"{'ch':6s} {'tone':4s} {'m*/me':>8s} {'±':>7s}  base-point check")
fits = {}
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=False)
for ax, ch in zip(axes, data):
    for k, marker in (("ML", "o"), ("BL", "s"), ("FL", "^")):
        A = np.array(data[ch][k])
        # fit rungs >= 6 K (T_e floor ~8 K makes the base rung's effective T ambiguous)
        Tf, Af = Ts[1:], A[1:]
        try:
            p, cov = curve_fit(lk, Tf, Af, p0=[0.05, Af[0] * 2], maxfev=20000)
            m_err = np.sqrt(cov[0, 0])
            # base-point consistency: implied effective T at base from the fit
            fits[(ch, k)] = (p[0], m_err)
            base_pred = lk(Ts[0], *p)
            print(f"{ch:6s} {k:4s} {p[0]:8.4f} {m_err:7.4f}  A(base) obs {A[0]:.3g} vs "
                  f"fit@T_lattice {base_pred:.3g} (ratio {A[0]/base_pred:.2f})")
        except Exception as e:
            print(f"{ch} {k}: fit failed {e}")
            continue
        ax.semilogy(Ts, A, marker, label=f"{k} (m*={p[0]:.3f})")
        Tg = np.linspace(1, 33, 200)
        ax.semilogy(Tg, lk(Tg, *p), "-", lw=0.8, alpha=0.6)
    ax.set_xlabel("T (K)")
    ax.set_title(ch)
    ax.legend(fontsize=8)
axes[0].set_ylabel("FFT amplitude (arb)")
fig.suptitle("LK mass fit, runs 8–13 (fit on T ≥ 6 K rungs; B_eff = 2.8 T)")
fig.tight_layout()
fig.savefig("hera_scratch/lk_fit.png", dpi=110)

# the discriminator: m(FL) vs m(ML)+m(BL)
for ch in data:
    try:
        mml, mbl, mfl = fits[(ch, "ML")][0], fits[(ch, "BL")][0], fits[(ch, "FL")][0]
        print(f"{ch}: m_ML={mml:.4f}, m_BL={mbl:.4f}, sum={mml+mbl:.4f}, m_FL={mfl:.4f} "
              f"-> m_FL/(m_ML+m_BL) = {mfl/(mml+mbl):.2f}")
    except KeyError:
        pass
print("saved lk_fit.png")
