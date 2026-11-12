"""sdh-spot-check read, runs 6 (e, n = +3.2e12) and 7 (h, n = -1.2e12), D = 0 (run-5 cal): raw MR first,
then onset (sdh_onset on the Nyquist-valid record), a window/detrend stability sweep of the zero-padded 1/B FFT,
and the peak set against F_L, the tetralayer model (ABAB / ABCA) and the trilayer ABA overlay (adjacent-N)."""
import sys
from scipy.signal import find_peaks
from hera.analysis import sdh_onset
_mdl = Path.home() / "measurement_env" / "hera" / "models"
sys.path.insert(0, str(_mdl / "tetralayer_fs_count")); import fs_count_b0 as fm4
import importlib.util as _ilu
_sp = _ilu.spec_from_file_location("fs3", _mdl / "trilayer_fs_count" / "fs_count_b0.py"); fm3 = _ilu.module_from_spec(_sp); _sp.loader.exec_module(fm3)

FLt = lambda n12: abs(n12) * 1e16 * cst.h / (4 * cst.e)
SENS = 50e-6   # sr1 sensitivity both runs (5 kOhm FS at 10 nA)

def load_R(rid):
    r = run(rid); B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6   # sr0 = drain current, gain -1e6
    R = r.col("sr1_X") / I                                              # sr1 gain 1 (device card)
    o = np.argsort(B); return B[o], R[o], float(np.median(I)), r

def fft_zp(B, R, lo, hi, deg=5, pad=16):
    """bg poly in B (before 1/B), interpolate to uniform 1/B, Hann, zero-pad x16 (sdh_fft does not pad on its uniform-B path)."""
    m = (B >= lo) & (B <= hi); dR = R[m] - np.polyval(np.polyfit(B[m], R[m], deg), B[m])
    u = np.linspace(1 / hi, 1 / lo, 2048); x = 1 / B[m]; o = np.argsort(x); yi = np.interp(u, x[o], dR[o])
    return np.fft.rfftfreq(pad * u.size, u[1] - u[0]), np.abs(np.fft.rfft(yi * np.hanning(u.size), n=pad * u.size))

def peakstr(f, s, fmin=2.0, k=6):
    pk, _ = find_peaks(s, prominence=0.05 * s[f > fmin].max()); pk = sorted([p for p in pk if f[p] > fmin], key=lambda p: -s[p])[:k]
    ref = max(s[p] for p in pk); return ", ".join(f"{f[p]:.1f}({s[p]/ref:.2f})" for p in sorted(pk))

fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, n12, lo_valid, win) in enumerate([(6, 3.2, 0.85, (1.4, 7.3)), (7, -1.2, 0.30, (1.5, 8.0))]):
    B, R, Ib, r = load_R(rid)
    T = r.col("T_sample"); Ig = np.abs(np.r_[r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")])
    print(f"=== run {rid}: n = {n12:+.2f}e12, D = 0; F_L = {FLt(n12):.2f} T | I = {Ib*1e9:.2f} nA | R(0) = {R[B < 0.35].mean():.0f} Ohm, "
          f"R max {R.max():.0f} Ohm @ {B[np.argmax(R)]:.2f} T | peak |V|/FS = {np.abs(r.col('sr1_X')).max()/SENS:.2f} | "
          f"T {T.min():.3f}-{T.max():.3f} K | max |I_gate| {Ig.max()*1e12:.0f} pA")
    ab = fm4.abab_fs(n12 * 1e16)[1]; abm = fm4.abab_mstar(n12 * 1e16); ac = fm4.abca_fs(n12 * 1e16); acm = fm4.abca_mstar(n12 * 1e16)[1]
    print("  model ABAB:", ", ".join(f"{f:.2f} T (m* {m:.3f})" for (f, _), (_, m) in zip(ab, abm)),
          f"| ABCA: {ac[4]:.2f} T ({ac[1]}, m* {acm:.3f})", end="")
    if n12 > 0: print(" | trilayer ABA:", ", ".join(f"{x[0]:.2f}" for x in fm3.aba_fs(n12 * 1e16)[1]), "T")
    else: print()
    # onset on the Nyquist-valid record (run 6: 50 mT steps below 1 T alias any F > 7.2 T below 0.85 T)
    on = sdh_onset(R, B, b_lo=lo_valid, b_hi=win[1], r_full_scale=SENS / Ib); print(on.summary())
    print("  FFT stability (window x bg degree; zero-padded; peaks = F [T] (rel. amp)):")
    for lo, hi in ([(1.0, 7.3), (1.4, 7.3), (1.0, 3.0), (2.0, 7.3), (1.4, 5.5)] if rid == 6 else [(0.8, 8.0), (1.5, 8.0), (1.0, 4.0)]):
        for deg in (4, 5, 7):
            f, s = fft_zp(B, R, lo, hi, deg); print(f"    [{lo:.1f},{hi:.1f}] T deg {deg}, dF = {1/(1/lo-1/hi):.2f} T: {peakstr(f, s)}")
    # raw first
    ax[row, 0].plot(B, R, lw=0.7); ax[row, 0].set_xlabel("B (T)"); ax[row, 0].set_ylabel("Rxx (Ohm)")
    ax[row, 0].set_title(f"run {rid} raw: n = {n12:+.1f}e12, D = 0 (sr1 B_1-B_2)")
    m = (B >= win[0]) & (B <= win[1]); dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[row, 1].plot(1 / B[m], dR, lw=0.7); ax[row, 1].set_xlabel("1/B (1/T)"); ax[row, 1].set_ylabel("dRxx (Ohm), bg5 in B")
    ax[row, 1].set_title(f"background-subtracted, B in [{win[0]}, {win[1]}] T")
    f, s = fft_zp(B, R, *win); ax[row, 2].plot(f, s / s[f > 2].max(), "k", lw=1, label=f"FFT [{win[0]},{win[1]}] T")
    ax[row, 2].axvline(FLt(n12), color="C0", ls="--", label="F_L (scale 1)")
    for i, (fa, _) in enumerate(ab): ax[row, 2].axvline(fa, color="C3", ls=":", label="ABAB model" if i == 0 else None)
    ax[row, 2].axvline(ac[4], color="C2", ls="-.", lw=0.8, label="ABCA model")
    if rid == 6:
        for k in (2, 3, 4, 8): ax[row, 2].axvline(k * 7.35, color="0.6", lw=0.6, ls="-", label="k x 7.35 T" if k == 2 else None)
    ax[row, 2].set_xlim(0, 2 * FLt(n12) if rid == 6 else 3 * FLt(n12)); ax[row, 2].set_xlabel("F (T)"); ax[row, 2].legend(fontsize=7)
fig.tight_layout(); plt.show()
