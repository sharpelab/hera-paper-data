"""sdh-spot-check read on runs 6 (electron, n = +3.2e12 nominal) and 7 (hole, n = -1.2e12): raw R(B) first, then
background-subtracted dR(1/B), per-tone onsets (sdh_onset), FFT stability over cut/degree, B-window split, and the
run-6 QH-minima nu = 4k ladder as an independent density-scale read. Model numbers: hera/models/tetralayer_fs_count."""
import warnings
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
from hera.analysis import sdh_onset, SdhOnsetError

h_e = cst.h / cst.e   # T m^2
FS_OHM = 50e-6 / 10e-9   # sr1 50 uV at I_bias 10 nA -> 5 kOhm full scale
# model F(n) at u_D = 0 (hera/models/tetralayer_fs_count/fs_count_b0.py, SI density):
MODEL = {3.2: dict(abab=(7.31, 25.78), abca=33.08), 2.9: dict(abab=(6.36, 23.63), abca=29.99), -1.2: dict(abab=(5.86, 6.54), abca=12.41)}

def load(i):
    r = run(i); B = r.col("magnet_field"); R = (r.col("sr1_X") / 1.0) / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); return r, B[o], R[o], r.col("T_sample")[o]

spots = [(6, 3.2, "electron, n = +3.2e12 (nominal)"), (7, -1.2, "hole, n = -1.2e12 (nominal)")]

# ---- 0. raw first
fig, ax = plt.subplots(1, 2, figsize=(14, 4))
for a, (i, n12, lab) in zip(ax, spots):
    r, B, R, T = load(i); a.plot(B, R, lw=0.6); a.set_xlabel("B (T)"); a.set_ylabel("R_xx = sr1/I (Ohm, signed)")
    a.set_title(f"run {i} raw — {lab}; T {T.min():.2f}-{T.max():.2f} K; sr1 50 uV (FS {FS_OHM:.0f} Ohm)")
    print(f"run {i}: {len(B)} pts B {B.min():.2f}-{B.max():.2f} T; R(B<0.2) {np.nanmedian(R[B<0.2]) if (B<0.2).any() else float('nan'):.0f} Ohm; "
          f"R max {R.max():.0f} Ohm ({R.max()/FS_OHM*100:.0f}% FS) at {B[np.argmax(R)]:.2f} T; {r.tags}")
fig.tight_layout(); plt.show()

# ---- 1. onsets + FFT stability + B-window split
fig, ax = plt.subplots(2, 3, figsize=(17, 8))
reads = {}
for row, (i, n12, lab) in enumerate(spots):
    r, B, R, T = load(i); Ra = np.abs(R); FL = float(luttinger_frequency(abs(n12) * 1e16))
    cuts = (1.5, 2.0, 3.0) if i == 6 else (1.0, 1.5, 2.5)
    # onset on the 10 mT record (run 6: >= 1.0 T; the 50 mT leg below aliases a 7 T tone)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(Ra, B, r_full_scale=FS_OHM, b_lo=1.0)
            print(f"\n== run {i} {lab}: F_L = {FL:.2f} T\n{on.summary()}")
        except SdhOnsetError as e:
            on = None; print(f"\n== run {i}: sdh_onset failed: {str(e)[:300]}")
        for wi in w: print("   warn:", str(wi.message)[:150])
    # dR(1/B), background deg 5 in B above the lowest cut
    m = B >= cuts[0]; cf = np.polyfit(B[m], Ra[m], 5); dR = Ra[m] - np.polyval(cf, B[m])
    a = ax[row, 0]; a.plot(1 / B[m], dR, lw=0.6); a.set_xlabel("1/B (1/T)"); a.set_ylabel("dR (Ohm)"); a.set_title(f"run {i}: R - poly5(B), B >= {cuts[0]} T")
    # FFT stability
    a = ax[row, 1]; tab = []
    for cut in cuts:
        for deg in (3, 5, 7):
            fr, sp = sdh_fft(Ra[:, None], B, b_range=(cut, B.max()), bg_degree=deg, log=False, nfft=4096)
            s = sp[0]; sel = fr > 2.0; pk, pr = find_peaks(s[sel], prominence=0.08 * s[sel].max())
            top = sorted(zip(pr["prominences"] / s[sel].max(), fr[sel][pk]), reverse=True)[:5]
            tab.append((cut, deg, [(round(f, 1), round(p, 2)) for p, f in top]))
            if deg == 5: a.plot(fr, s / s[sel].max(), lw=0.8, label=f"cut {cut} T (dF {1/(1/cut-1/B.max()):.1f} T)")
    for cut, deg, top in tab: print(f"   FFT cut {cut} T deg {deg}: {top}")
    a.axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L(nominal) {FL:.1f} T")
    key = n12 if n12 in MODEL else None
    if key:
        for f in MODEL[key]["abab"]: a.axvline(f, color="tab:red", ls=":", lw=0.8)
        a.axvline(MODEL[key]["abca"], color="tab:green", ls=":", lw=0.8)
        a.plot([], [], "tab:red", ls=":", label=f"ABAB model {MODEL[key]['abab']}"); a.plot([], [], "tab:green", ls=":", label=f"ABCA model {MODEL[key]['abca']}")
    a.set_xlim(0, 2.2 * FL); a.set_xlabel("F (T)"); a.set_ylabel("|FFT| (norm)"); a.legend(fontsize=7); a.set_title(f"run {i}: FFT in 1/B, poly-5 bg in B")
    # B-window split at equal 1/B halves above cuts[1]
    a = ax[row, 2]; cut = cuts[1]; Bm = 2 / (1 / cut + 1 / B.max())
    for lo, hi, name in ((cut, Bm, "low-B half"), (Bm, B.max(), "high-B half")):
        fr, sp = sdh_fft(Ra[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
        s = sp[0]; sel = fr > 2; a.plot(fr, s / s[sel].max(), lw=0.8, label=f"{name} {lo:.2f}-{hi:.2f} T (dF {1/(1/lo-1/hi):.1f} T)")
    a.axvline(FL, color="k", ls="--", lw=0.8); a.set_xlim(0, 2.2 * FL); a.legend(fontsize=7); a.set_title(f"run {i}: B-window split")
    reads[i] = dict(FL=FL, onset=None if on is None else on.onset_b)
fig.tight_layout(); plt.show()

# ---- 2. run 6: QH minima as a nu = 4k ladder -> independent density scale
r, B, R, T = load(6); Ra = gaussian_filter1d(np.abs(R), 2)
sel = B > 3.0; pk, pr = find_peaks(-Ra[sel], prominence=25)
Bmin = B[sel][pk]; print(f"\nrun 6 R minima (B > 3 T, prominence > 25 Ohm): {np.round(Bmin, 2)} T")
best = None
for n12 in np.arange(2.4, 3.8, 0.005):
    nu = n12 * 1e16 * h_e / Bmin; res = nu - 4 * np.round(nu / 4)
    score = np.sqrt(np.mean(res ** 2))
    if best is None or score < best[0]: best = (score, n12, nu)
score, n_qh, nu = best
print(f"best nu = 4k assignment: n = {n_qh:.3f}e12 (nominal 3.20 -> scale {n_qh/3.2:.3f}); nu at minima = {np.round(nu, 1)}; rms(nu - 4k) = {score:.2f}")
print(f"-> F_L at the QH-scale density = {luttinger_frequency(n_qh*1e16):.1f} T (the observed 29.5-30.0 T tone); ABAB model at 2.9e12: {MODEL[2.9]['abab']} (sum {sum(MODEL[2.9]['abab']):.1f})")
fig, a = plt.subplots(figsize=(12, 3.5)); a.plot(B, np.abs(R), lw=0.6)
for b, v in zip(Bmin, nu): a.axvline(b, color="tab:red", ls=":", lw=0.8); a.text(b, np.abs(R).max() * 0.9, f"nu={v:.1f}", rotation=90, fontsize=7, ha="right")
a.set_xlabel("B (T)"); a.set_ylabel("|R_xx| (Ohm)"); a.set_title(f"run 6 QH minima; best nu=4k ladder at n = {n_qh:.2f}e12 (scale {n_qh/3.2:.2f})"); plt.show()
