"""sdh-spot-check read on runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12), D = 0, T = 1.2 K: raw Rxx(B),
background-subtracted vs 1/B, per-window 1/B FFTs against F_L and the fs_count_b0 templates."""
import sys
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, SdhOnsetError

h_e = cst.h / cst.e
SPOTS = [(6, 3.2), (7, -1.2)]
# model templates at the spot densities (fs_count_b0, n in m^-2): (F [T], m*/m_e)
MODEL = {3.2: dict(abab=[(7.31, 0.027), (25.78, 0.061)], abca=(33.08, 0.074)),
         -1.2: dict(abab=[(5.86, 0.074), (6.54, 0.032)], abca=(12.41, 1.122))}

def Rxx(r):
    B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / (-1e6))   # sr1 gain 1, sr0 = -1e6 V/A
    o = np.argsort(B); return B[o], R[o], r.col("T_sample")[o]

fig, axs = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, n12) in enumerate(SPOTS):
    r = run(rid); print(summarize_run(r))
    B, R, T = Rxx(r); FL = h_e / 4 * abs(n12) * 1e16
    print(f"run {rid}: n = {n12:+.1f}e12, F_L = {FL:.2f} T; R {R.min():.0f}..{R.max():.0f} Ohm (max {np.abs(R).max()/5000:.2f} of the 5 kOhm FS); T {T.min():.3f}-{T.max():.3f} K")
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 — raw Rxx = sr1/sr0 (50 uV, 10 nA)")
    # onset (per-tone tracks) — the B_lo lever for the fan
    try:
        on = sdh_onset(R, B, r_full_scale=5000.0); print(on.summary())
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
    # background-subtracted (deg-5 in B, B > 1 T) vs 1/B
    m = B >= 1.0; dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    axs[1, j].plot(1 / B[m], dR, lw=0.7); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_ylabel("dRxx (Ohm)")
    axs[1, j].set_title("background-subtracted (deg-5 in B), B > 1 T")
    # FFT windows: whole record above 1 T (clean 10/20 mT grid), low half, high half
    ax = axs[2, j]
    for (lo, hi, deg) in [(1.0, 2.2, 3), (1.0, 10.0, 3), (3.0, 7.5, 3), (4.0, 10.0, 5)]:
        f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=deg, log=False, nfft=4096); s = s[0]
        p, _ = find_peaks(s, prominence=0.05 * s.max()); p = p[np.argsort(s[p])[::-1]][:6]
        print(f"  FFT [{lo},{hi}] T deg{deg} (dF = {1/(1/lo-1/hi):.2f} T): " + ", ".join(f"{f[i]:.1f} T ({s[i]/s.max():.2f})" for i in p))
        ax.plot(f, s / s.max(), lw=1, label=f"[{lo:.0f},{hi:.0f}] T deg{deg}")
    ax.axvline(FL, color="k", ls="--", lw=1, label=f"F_L = {FL:.1f} T")
    for F, mm in MODEL[n12]["abab"]: ax.axvline(F, color="tab:red", ls=":", lw=1)
    ax.axvline(MODEL[n12]["abca"][0], color="tab:green", ls=":", lw=1)
    ax.plot([], [], "r:", label="model ABAB pair"); ax.plot([], [], "g:", label="model ABCA singleton")
    ax.set_xlim(0, 2.2 * FL); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm.)"); ax.legend(fontsize=7); ax.set_title("1/B FFT per window")
    # QH-regime minima -> filling factors at the run-5 calibration scale
    mm_ = B >= 3.0; p, _ = find_peaks(-R[mm_], prominence=20)
    print("  Rxx minima above 3 T (B / nu at cal scale): " + ", ".join(f"{b:.2f}/{abs(n12)*1e16*h_e/b:.1f}" for b in B[mm_][p]))
fig.tight_layout(); plt.show()
