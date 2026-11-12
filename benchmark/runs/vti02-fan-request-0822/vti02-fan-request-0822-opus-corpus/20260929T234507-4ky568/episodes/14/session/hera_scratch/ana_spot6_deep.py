"""Run 6 deep read: clean-leg onset, Dingle extrapolation, spectrum shape, B-window split.

Run 6's B grid is 50 mT below 1 T and 10 mT above. At B = 0.65 T the 50 mT step
gives d(1/B) = 0.118 /T -> Nyquist 4.2 T: the 7.5 T tone and its comb are ALIASED
below 1 T. So the sub-1 T leg cannot pin an onset. Everything here uses B >= 1.0 T.
"""
import numpy as np, scipy.constants as cst, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft

H, E = cst.h, cst.e
r = open_run("data/6")
mc = r.meta["measurement_config"]
B = r.col("magnet_field"); I = r.col("sr0_X") / mc["sr0_gain"]; R = r.col("sr1_X") / I
o = np.argsort(B); B, R, I = B[o], R[o], I[o]
n12 = 3.2; F_L = H / (4 * E) * n12 * 1e16
r_fs = 50e-6 / np.median(np.abs(I))
print(f"F_L = {F_L:.2f} T; r_full_scale = {r_fs:.0f} Ohm")

m = B >= 1.0
Bc, Rc = B[m], R[m]
print(f"clean leg (10 mT): {len(Bc)} pts, {Bc.min():.2f}-{Bc.max():.2f} T; "
      f"d(1/B) at 1 T = {0.01/1.0**2:.4f} /T -> Nyquist {1/(2*0.01):.0f} T")

on = sdh_onset(Rc, Bc, b_lo=1.0, r_full_scale=r_fs)
print("\n--- sdh_onset on the clean leg (B >= 1.0 T) ---")
print(on.summary())
print(f"noise_sigma = {on.noise_sigma:.4g}")

# Dingle-style extrapolation per tone: log(amp) vs 1/B, extrapolate to snr = 5.
print("\n--- per-tone amplitude tracks, extrapolated to SNR = 5 ---")
for t in on.tones:
    b, s = np.asarray(t.b_centers), np.asarray(t.snr)
    ok = np.isfinite(s) & (s > 0)
    if ok.sum() < 3:
        continue
    x, y = 1.0 / b[ok], np.log(s[ok])
    p = np.polyfit(x, y, 1)          # ln SNR = a/B + c ; a<0 means dying at low B
    x5 = (np.log(5.0) - p[1]) / p[0] if p[0] != 0 else np.nan
    b5 = 1.0 / x5 if x5 > 0 else np.nan
    print(f"  f = {t.freq:6.2f} T  snr {s[ok].min():5.1f}-{s[ok].max():5.1f} over B {b[ok].min():.2f}-{b[ok].max():.2f} T"
          f"  | dlnSNR/d(1/B) = {p[0]:+7.2f}  -> SNR=5 at B = {b5:.2f} T")

# spectrum, full + low/high B halves (F_L-tone-origin B-window split)
fig, ax = plt.subplots(2, 1, figsize=(11, 8))
f, sp = sdh_fft(Rc[:, None], Bc, b_range=(1.5, 10.0), bg_degree=5, nfft=8192)
ax[0].plot(f, sp[0], "k", lw=1.2, label="1.5-10 T")
# split at the 1/B midpoint of the window
b_mid = 1.0 / (0.5 * (1 / 1.5 + 1 / 10.0))
for (lo, hi), c in (((1.5, b_mid), "tab:blue"), ((b_mid, 10.0), "tab:red")):
    fh, sph = sdh_fft(Rc[:, None], Bc, b_range=(lo, hi), bg_degree=5, nfft=8192)
    ax[1].plot(fh, sph[0], c, lw=1.1, label=f"{lo:.2f}-{hi:.2f} T")
for a in ax:
    a.axvline(F_L, color="g", ls="--", label="$F_L$ = 33.1 T")
    for k, fk in enumerate([7.31, 25.78], 1):
        a.axvline(fk, color="tab:orange", ls=":", label="ABAB model" if k == 1 else None)
    for k in (2, 3, 4, 8):
        a.axvline(k * 7.5, color="grey", ls="-.", lw=0.7, label="k x 7.5 T" if k == 2 else None)
    a.set_xlim(0, 70); a.set_xlabel("F [T]"); a.set_ylabel("|FFT| (log)"); a.legend(fontsize=7)
ax[0].set_title(f"run 6 spectrum, n = +3.2e12, D = 0  (b_mid split at {b_mid:.2f} T)")
fig.tight_layout(); fig.savefig("hera_scratch/spot6_spectrum.png", dpi=110)
print("\nwrote hera_scratch/spot6_spectrum.png")

# numeric: amplitude at the candidate frequencies, per half
print("\n--- B-window split: log-amp at candidate tones ---")
print(f"{'window':>16} " + " ".join(f"{q:>8.1f}" for q in (7.5, 15.0, 22.5, 25.8, 30.0, 33.1, 60.0)))
for lo, hi in ((1.5, 10.0), (1.5, b_mid), (b_mid, 10.0), (3.0, 10.0), (5.0, 10.0)):
    fh, sph = sdh_fft(Rc[:, None], Bc, b_range=(lo, hi), bg_degree=5, nfft=8192)
    vals = [sph[0][np.argmin(np.abs(fh - q))] for q in (7.5, 15.0, 22.5, 25.8, 30.0, 33.1, 60.0)]
    print(f"{lo:6.2f}-{hi:5.2f} T " + " ".join(f"{v:8.1f}" for v in vals))
