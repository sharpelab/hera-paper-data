"""Runs 6/7 — sdh-spot-check (electron n = +3.2e12, hole n = -1.2e12; D = 0, run-5 cal). Raw first, then onset + FFT in 1/B vs F_L,
then the model templates (ABAB pair / ABCA singleton) and the QH filling-factor density pin."""
import warnings
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, SdhOnsetError

I_BIAS = 1.0 / 100e6                      # 1 V drive / 100 MOhm
H_4E = cst.h / (4 * cst.e)                # F_L = (h/4e) n
SPOTS = [(6, +3.2), (7, -1.2)]
MODEL = {  # hera/models/tetralayer_fs_count/fs_count_b0.py at the calibrated densities: (ABAB light, ABAB heavy, ABCA singleton) [T]
    6: (7.31, 25.78, 33.08), 7: (5.86, 6.54, 12.41)}

# --- 1. raw, both runs
fig, ax = plt.subplots(1, 2, figsize=(13, 3.8))
traces = {}
for a, (rid, n12) in zip(ax, SPOTS):
    r = run(rid); B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS
    o = np.argsort(B); traces[rid] = (B[o], R[o])
    a.plot(B[o], R[o], lw=0.7); a.set_xlabel("B (T)"); a.set_ylabel("Rxx = sr1_X / 10 nA (Ohm)")
    a.set_title(f"run {rid} raw — n_cal = {n12:+.1f}e12, D = 0, sr1 50 uV (5 kOhm FS)")
    print(summarize_run(r))
plt.tight_layout(); plt.show()

# --- 2. onset (hera.analysis.sdh_onset) + FFT in 1/B over several low-B cutoffs, tones vs F_L
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for c, (rid, n12) in enumerate(SPOTS):
    B, R = traces[rid]; FL = H_4E * abs(n12) * 1e16
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            on = sdh_onset(R, B, r_full_scale=50e-6 / I_BIAS); onset = on.onset_b; print(f"\nrun {rid}: F_L = {FL:.2f} T\n" + on.summary())
        except SdhOnsetError as e:
            onset = None; print(f"run {rid}: SdhOnsetError {e}")
    m = B >= 1.0; dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[0, c].plot(1 / B[m], dR, lw=0.7); ax[0, c].set_xlabel("1/B (1/T)"); ax[0, c].set_ylabel("dRxx (Ohm), deg-5 bg in B, B > 1 T")
    ax[0, c].set_title(f"run {rid}: background-subtracted, onset_b = {onset if onset is None else round(onset, 2)} T")
    for lo in [x for x in ([onset] if onset else []) + [2.0, 3.0] if x and x < 8]:
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False, nfft=4096); S = S[0]
        sel = (f > 2) & (f < 100); pk, _ = find_peaks(S[sel], prominence=0.08 * S[sel].max())
        ax[1, c].plot(f[sel], S[sel] / S[sel].max(), lw=0.8, label=f"B > {lo:.2f} T (dF {1/(1/lo-1/B.max()):.1f} T)")
        print(f"  window [{lo:.2f}, {B.max():.0f}] T: " + ", ".join(f"{f[sel][p]:.1f} T ({f[sel][p]/FL:.2f} F_L)" for p in pk))
    lt, hv, sg = MODEL[rid]
    for x, ls, lab in [(FL, ":", f"F_L = {FL:.1f} T"), (lt, "--", f"ABAB light {lt:.1f}"), (hv, "--", f"ABAB heavy {hv:.1f}")]:
        ax[1, c].axvline(x, color="k" if ls == ":" else "g", ls=ls, lw=1, label=lab)
    ax[1, c].set_xlabel("F (T)"); ax[1, c].set_ylabel("|FFT| (norm)"); ax[1, c].legend(fontsize=7); ax[1, c].set_title(f"run {rid}: SdH FFT in 1/B vs F_L and the ABAB template")
plt.tight_layout(); plt.show()

# --- 3. model-free density pin from the QH minima of run 6 (nu = n h / e B)
B6, R6 = traces[6]; m = B6 > 4.0; mins, _ = find_peaks(-R6[m], prominence=40)
print("\nrun 6 Rxx minima above 4 T (B, R):", ", ".join(f"({B6[m][i]:.2f} T, {R6[m][i]:.0f} Ohm)" for i in mins))
for nu, Bm in [(20, 6.0), (16, 7.2)]:
    print(f"  if nu = {nu} at {Bm} T: n = {nu*cst.e*Bm/cst.h/1e16:.2f}e12 (n_cal 3.2 -> scale {nu*cst.e*Bm/cst.h/1e16/3.2:.2f}); F_L(that n) = {H_4E*nu*cst.e*Bm/cst.h:.1f} T")
