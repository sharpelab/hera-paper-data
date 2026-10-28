"""sdh-spot-check read, runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12), both D = 0 (run-5 cal), sr1 50 uV, 10 tau settle.
Raw Rxx(B) first, then the deg-5-in-B background-subtracted record vs 1/B, sdh_onset (per-tone onsets, harmonic flags),
sdh_fft over several windows against F_L and the model's ABAB / ABCA tones."""
import warnings
from numpy.polynomial import polynomial as P
from scipy.signal import find_peaks
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError

R_FS = 50e-6 / 10e-9                     # sr1 50 uV at 10 nA -> 5 kOhm full scale (soft-clip guard for sdh_onset)
MODEL = {  # fs_count_b0 (u_D = 0): n [1e12] -> (ABAB light, ABAB heavy, ABCA singleton) [T]
    3.2: (7.31, 25.78, 33.08), -1.2: (5.86, 6.54, 12.41)}
reads = {}
for rid, n12, lo_c in ((6, 3.2, 1.5), (7, -1.2, 1.0)):
    r = run(rid); print("=" * 90); print(summarize_run(r))
    chs = {c.cid: c for c in resolve_channels(r.metadata)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / chs["sr0"].gain; V = r.col("sr1_X") / chs["sr1"].gain
    R = np.abs(V / I); T = r.col("T_sample"); o = np.argsort(B); B, R, T = B[o], R[o], T[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T; B {B.min():.2f}-{B.max():.2f} T ({len(B)} pts); "
          f"R {R.min():.1f}/{np.median(R):.0f}/{R.max():.0f} Ohm (min/med/max, {R.max()/R_FS:.2f} of FS); I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=R_FS, b_lo=0.3); print(on.summary())
        except SdhOnsetError as e:
            on = None; print("SdhOnsetError:", e)
        for wi in w: print("  warn:", str(wi.message)[:160])
    fig, ax = plt.subplots(2, 2, figsize=(14, 8.5))
    ax[0, 0].plot(B, R, lw=0.7); ax[0, 0].set_xlabel("B (T)"); ax[0, 0].set_ylabel("Rxx (Ohm)")
    ax[0, 0].set_title(f"run {rid} raw Rxx(B) — n = {n12:+.1f}e12, D = 0, sr1 50 uV")
    m = B >= lo_c; cf = P.polyfit(B[m], R[m], 5); dR = R[m] - P.polyval(B[m], cf)
    ax[0, 1].plot(1 / B[m], dR, lw=0.7); ax[0, 1].set_xlabel("1/B (1/T)"); ax[0, 1].set_ylabel("dRxx (Ohm)")
    ax[0, 1].set_title(f"background-subtracted (deg-5 in B), B > {lo_c} T")
    for (a, b) in [(lo_c, 10.0), (2.0, 10.0), (3.0, 10.0), (2.0, 6.0)]:
        f, s = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False, nfft=2048)
        ax[1, 0].plot(f, s[0] / s[0].max(), lw=0.8, label=f"[{a}, {b:.0f}] T  dF = {1/(1/a-1/b):.1f} T")
    ax[1, 0].axvline(FL, color="k", ls="--", lw=1, label=f"F_L = {FL:.1f} T")
    fl, fh, fa = MODEL[n12]
    for x, c, lab in ((fl, "tab:blue", "ABAB light"), (fh, "tab:blue", "ABAB heavy"), (fa, "tab:red", "ABCA")):
        ax[1, 0].axvline(x, color=c, ls=":", lw=1, label=f"model {lab} {x:.1f} T")
    ax[1, 0].set_xlim(0, 1.6 * FL); ax[1, 0].set_xlabel("F (T)"); ax[1, 0].set_ylabel("norm |FFT|"); ax[1, 0].legend(fontsize=7); ax[1, 0].set_title("sdh_fft (linear R, deg-5 bg), window ladder")
    f2, s2 = sdh_fft(R[:, None], B, b_range=(lo_c, 10.0), bg_degree=5, log=False, nfft=4096); sp = s2[0]
    pk, _ = find_peaks(sp, prominence=0.05 * sp.max()); pk = pk[f2[pk] > 1.0]
    ax[1, 1].plot(f2, sp / sp.max(), lw=0.8); ax[1, 1].plot(f2[pk], sp[pk] / sp.max(), "rv", ms=5)
    for p in pk: ax[1, 1].annotate(f"{f2[p]:.1f}", (f2[p], sp[p] / sp.max()), fontsize=7, ha="center", va="bottom")
    ax[1, 1].axvline(FL, color="k", ls="--", lw=1); ax[1, 1].set_xlim(0, 1.6 * FL); ax[1, 1].set_xlabel("F (T)"); ax[1, 1].set_title(f"peaks, full window [{lo_c}, 10] T")
    fig.tight_layout(); plt.show()
    print("FFT peaks (full window):", ", ".join(f"{f2[p]:.2f} T ({sp[p]/sp.max():.2f})" for p in pk[:12]))
    reads[rid] = dict(FL=FL, onset=on, peaks=[float(f2[p]) for p in pk])
