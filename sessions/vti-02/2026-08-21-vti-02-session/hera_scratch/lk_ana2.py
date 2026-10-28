"""LK masses with per-tone, per-window B_eff: the window-midpoint B_eff biases tones that live at high B (breakdown
sum) low and low-B tones high. Fit A(T) in several 1/B sub-windows, each with its own B_eff = 1/<1/B>, and fit
m* jointly across windows (the LK factor X/sinh X with X = 14.69 m* T / B_eff_window).
Usage: menv python hera_scratch/lk_ana2.py <run_id> ...   (run 5 first = base rung)
"""
import sys, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit
from hera.analysis import open_run, sdh_fft

DATA = Path(__file__).resolve().parents[1] / "data"
ids = [int(a) for a in sys.argv[1:]]
WINDOWS = [(2.4, 4.5), (3.5, 7.0), (5.5, 10.0), (2.4, 10.0)]
TONES = {"light": (6.5, 2.5), "heavy": (22.5, 3.0), "sum": (29.0, 3.0)}   # centre, half-width [T]

def load(rid):
    r = open_run(DATA / str(rid)); mc = r.meta["measurement_config"]
    B = r.col("magnet_field"); I = r.col("sr0_X") / float(mc["sr0_gain"]); R = r.col("sr1_X") / I; T = r.col("T_sample")
    o = np.argsort(B); return B[o], R[o], T[o]

data = {rid: load(rid) for rid in ids}
Ts = np.array([float(np.nanmean(data[rid][2][(data[rid][0] >= 2.4)])) for rid in ids])
print("T rungs:", np.round(Ts, 2))
amp = {name: np.zeros((len(WINDOWS), len(ids))) for name in TONES}
beff = []
for w, (blo, bhi) in enumerate(WINDOWS):
    beff.append(1.0 / (0.5 * (1 / blo + 1 / bhi)))
    for k, rid in enumerate(ids):
        B, R, T = data[rid]; m = (B >= blo) & (B <= bhi)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            freqs, spec = sdh_fft(R[m][:, None], B[m], b_range=(blo, bhi), bg_degree=3, nfft=4096, log=False)
        sp = spec[0]
        for name, (f0, hw) in TONES.items():
            sel = (freqs > f0 - hw) & (freqs < f0 + hw); amp[name][w, k] = sp[sel].max() if sel.any() else float(np.interp(f0, freqs, sp))
beff = np.array(beff)
dF = [1 / (1 / a - 1 / b) for a, b in WINDOWS]
print("windows:", WINDOWS, "B_eff:", np.round(beff, 2), "dF:", np.round(dF, 1))

def lk_joint_factory(beff_local):
    def lk_joint(x, *p):
        wi = x[0].astype(int); T = x[1]; m = p[0]
        X = 14.69 * m * T / beff_local[wi]
        A0 = np.array([p[1 + i] for i in wi])
        return A0 * X / np.sinh(X)
    return lk_joint

fig, axs = plt.subplots(1, len(TONES), figsize=(6 * len(TONES), 4.6))
results = {}
for a, (name, (f0, hw)) in zip(axs, TONES.items()):
    use = [w for w in range(len(WINDOWS)) if dF[w] < 2.2 * hw + 3]   # only windows that can still isolate the tone
    xs = np.array([[w, Ts[k]] for w in use for k in range(len(ids))]).T
    ys = np.array([amp[name][w, k] for w in use for k in range(len(ids))])
    p0 = [0.05] + [amp[name][w, 0] for w in use]
    try:
        xloc = np.array([[use.index(int(w)) for w in xs[0]], xs[1]])
        p, cov = curve_fit(lk_joint_factory(beff[use]), xloc, ys, p0=p0, bounds=([0.005] + [0] * len(use), [1.0] + [np.inf] * len(use)))
        err = np.sqrt(np.diag(cov))[0]
        results[name] = (p[0], err, use)
        print(f"{name:5s}: m* = {p[0]:.4f} +- {err:.4f} m_e  (windows {[WINDOWS[w] for w in use]}, B_eff {np.round(beff[use], 2)})")
        for j, w in enumerate(use):
            X = 14.69 * p[0] * Ts / beff[w]
            a.plot(Ts, amp[name][w] / p[1 + j], "o", label=f"B {WINDOWS[w][0]}-{WINDOWS[w][1]} (B_eff {beff[w]:.1f})")
            Tf = np.linspace(0.5, Ts.max() * 1.1, 80); Xf = 14.69 * p[0] * Tf / beff[w]; a.plot(Tf, Xf / np.sinh(Xf), "-", lw=0.8)
    except Exception as ex:
        print(f"{name}: fit failed: {ex}")
    # per-window masses too
    for w in use:
        try:
            pw, cw = curve_fit(lambda T, A0, m: A0 * (14.69 * m * T / beff[w]) / np.sinh(14.69 * m * T / beff[w]), Ts, amp[name][w], p0=(amp[name][w, 0], 0.05), bounds=([0, 0.005], [np.inf, 1]))
            print(f"     window {WINDOWS[w]} (B_eff {beff[w]:.2f}): m* = {pw[1]:.4f} +- {np.sqrt(cw[1,1]):.4f}")
        except Exception as ex:
            print(f"     window {WINDOWS[w]}: {ex}")
    a.set_title(f"{name} tone ({f0} T)"); a.set_xlabel("T [K]"); a.set_ylabel("A / A0"); a.legend(fontsize=7)
plt.tight_layout(); out = Path(__file__).resolve().parent / "lk_ladder2.png"; plt.savefig(out, dpi=90); print("saved", out)
