"""LK ladder read: per-rung FFT amplitudes of the named tones vs T; fit X/sinh(X) per tone for m*."""
from scipy.optimize import curve_fit
from hera.analysis import resolve_channels

runs = [9, 10, 11, 12, 13, 14]   # LK ladder rungs: base, 6, 10, 15, 22, 30 K
TONES = {"light": (5.5, 9.5), "2xlight": (12.5, 17), "heavy": (19.5, 25), "sum": (27, 32)}
rows = []
for rid in runs:
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = (r.col("sr1_X") / ch["sr1"].gain) / I; T = r.col("T_sample")
    o = np.argsort(B); B, R = B[o], R[o]
    lo, hi = max(B.min(), 2.0), min(B.max(), 7.0)
    f, spec = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096); s = spec[0]
    amps = {k: s[(f >= a) & (f <= b)].max() for k, (a, b) in TONES.items()}
    fpk = {k: f[(f >= a) & (f <= b)][np.argmax(s[(f >= a) & (f <= b)])] for k, (a, b) in TONES.items()}
    Tm = float(np.nanmean(T)); rows.append((rid, Tm, float(np.nanstd(T)), amps, fpk, lo, hi, r.tags))
    print(f"run {rid}: T = {Tm:.2f} ± {np.nanstd(T):.2f} K, window [{lo:.1f},{hi:.1f}] T, " + ", ".join(f"{k} {fpk[k]:.1f}T:{amps[k]:.3g}" for k in TONES))
B_eff = 1 / ((1 / rows[0][5] + 1 / rows[0][6]) / 2)
print(f"B_eff = {B_eff:.2f} T")
def lk(T, A, m):
    X = 14.69 * m * T / B_eff; return A * X / np.sinh(X)
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
Ts = np.array([x[1] for x in rows])
for k in TONES:
    A = np.array([x[3][k] for x in rows]); ax[0].semilogy(Ts, A / A[0], "o-", label=k)
    try:
        sel = Ts > 3.0  # heated rungs only (base T_e unknown)
        if sel.sum() >= 3:
            p, cov = curve_fit(lk, Ts[sel], A[sel], p0=(A[sel][0] * 1.2, 0.05), bounds=([0, 0.005], [np.inf, 1.0]))
            Tfit = np.linspace(1, Ts.max(), 100); ax[1].semilogy(Tfit, lk(Tfit, *p) / lk(1.2, *p), "-", label=f"{k}: m* = {p[1]:.3f} ± {np.sqrt(cov[1,1]):.3f}")
            ax[1].semilogy(Ts, A / lk(1.2, *p), "o")
            print(f"LK fit {k} (heated rungs, B_eff {B_eff:.2f}): m* = {p[1]:.4f} ± {np.sqrt(cov[1,1]):.4f} m_e; base-rung amplitude implies T_e = "
                  + (f"{np.interp(A[0] / p[0], lk(np.linspace(30, 0.5, 500), 1, p[1])[::1], np.linspace(30, 0.5, 500)):.1f} K" if A[0] < p[0] else "n/a"))
    except Exception as e:
        print("fit", k, "failed:", e)
ax[0].set_xlabel("T_sample (K)"); ax[0].set_ylabel("FFT amp / base"); ax[0].legend(); ax[0].set_title("tone amplitudes vs T")
ax[1].set_xlabel("T (K)"); ax[1].set_ylabel("amp (norm to fit at 1.2 K)"); ax[1].legend(fontsize=8); ax[1].set_title("LK fits (heated rungs)")
fig.tight_layout(); plt.show()

# --- window-resolved LK for the heavy and sum tones (>= 3 periods per window): [2,3.5] and [3.5,7] T ---
print("\nwindow-resolved LK (heated rungs):")
for (wlo, whi) in [(2.0, 3.5), (3.5, 7.0), (2.0, 7.0)]:
    Beff_w = 1 / ((1 / wlo + 1 / whi) / 2)
    def lk_w(T, A, m, _B=Beff_w):
        X = 14.69 * m * T / _B; return A * X / np.sinh(X)
    res = {}
    for k, (a, b) in TONES.items():
        if k == "light" and whi - wlo < 4: continue
        A = []
        for rid in runs:
            r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
            B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain; R = (r.col("sr1_X") / ch["sr1"].gain) / I
            o = np.argsort(B); B, R = B[o], R[o]
            f, spec = sdh_fft(R[:, None], B, b_range=(wlo, whi), bg_degree=4, log=False, nfft=4096); s = spec[0]
            A.append(s[(f >= a) & (f <= b)].max())
        A = np.array(A); sel = Ts > 3.0
        try:
            p, cov = curve_fit(lk_w, Ts[sel], A[sel], p0=(A[sel][0] * 1.2, 0.05), bounds=([0, 0.005], [np.inf, 1.0]))
            res[k] = (p[1], np.sqrt(cov[1, 1]))
        except Exception as e:
            res[k] = (np.nan, np.nan)
    print(f"  window [{wlo},{whi}] T (B_eff {Beff_w:.2f}, dF {1/(1/wlo-1/whi):.1f} T): " + ", ".join(f"{k} m* = {v[0]:.3f} ± {v[1]:.3f}" for k, v in res.items()))
