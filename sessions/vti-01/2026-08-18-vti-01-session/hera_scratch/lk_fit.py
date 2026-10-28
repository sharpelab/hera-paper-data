# LK mass fit from ladder runs 12-18 (scratch)
import numpy as np
from hera.analysis import open_run, sdh_fft
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RUNS = list(range(12, 19))
B_EFF = 2.0 / (1 / 2.0 + 1 / 5.0)   # harmonic-ish: 1/B_eff = midpoint of 1/B window = (0.5+0.2)/2 -> B_eff = 2.857
B_EFF = 1 / ((1 / 2.0 + 1 / 5.0) / 2)
C_LK = 14.69 / B_EFF                 # X = C * m* * T

def amp_at(f, s, F0, half=2.0):
    m = (f > F0 - half) & (f < F0 + half)
    return s[m].max() if m.any() else np.nan

rows = []
for rid in RUNS:
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    i_dr = np.abs(r.col("sr0_X")) / 1e6
    T = np.mean(r.col("T_sample"))
    Tdrift = np.ptp(r.col("T_sample"))
    out = {"run": rid, "T": T, "drift": Tdrift}
    for ch in ("sr1", "sr3"):
        R = (r.col(f"{ch}_X") / i_dr)[:, None]
        f, s = sdh_fft(R, B, b_range=(2.0, 5.0), bg_degree=4)
        out[f"{ch}_A"] = amp_at(f, s[0], 16.2)     # branch A
        out[f"{ch}_A2"] = amp_at(f, s[0], 8.1)     # A/2 component
    rows.append(out)
    print(f"run {rid}: T={T:.3f} K (drift {Tdrift:.3f}), "
          f"sr1 A={out['sr1_A']:.3g} A/2={out['sr1_A2']:.3g}, "
          f"sr3 A={out['sr3_A']:.3g} A/2={out['sr3_A2']:.3g}")

T_arr = np.array([o["T"] for o in rows])

def lk(T, m, a0):
    X = C_LK * m * T
    return a0 * X / np.sinh(X)

print(f"\nB_eff = {B_EFF:.2f} T, C_LK = {C_LK:.3f} /K per m*/me")
fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
for ax, key, lbl in ((axs[0], "_A", "branch A (16.2 T)"), (axs[1], "_A2", "A/2 (8.1 T)")):
    for ch, c in (("sr1", "tab:blue"), ("sr3", "tab:green")):
        amps = np.array([o[ch + key] for o in rows])
        ok = np.isfinite(amps)
        try:
            p, cov = curve_fit(lk, T_arr[ok], amps[ok], p0=[0.08, amps[ok][0] * 1.2],
                               bounds=([0.001, 0], [1.0, np.inf]))
            err = np.sqrt(np.diag(cov))[0]
            Tf = np.linspace(1, 16, 200)
            ax.plot(Tf, lk(Tf, *p), color=c, lw=1)
            ax.plot(T_arr[ok], amps[ok], "o", color=c,
                    label=f"{ch}: m* = {p[0]:.3f} ± {err:.3f} me")
            print(f"{lbl} {ch}: m* = {p[0]:.4f} +/- {err:.4f} me "
                  f"(15 K amp / base amp = {amps[ok][-1]/amps[ok][0]:.2f})")
        except Exception as e:
            ax.plot(T_arr[ok], amps[ok], "x", color=c, label=f"{ch}: fit failed {e}")
    ax.set_title(lbl); ax.set_xlabel("T (K)"); ax.set_ylabel("FFT amplitude"); ax.legend(fontsize=7); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("hera_scratch/lk_fit.png", dpi=110)
print("model masses at n=-1.74e12 (hole): ABA {ML 0.010, BL 0.060}, ABC 0.108 me")
print("saved hera_scratch/lk_fit.png")
