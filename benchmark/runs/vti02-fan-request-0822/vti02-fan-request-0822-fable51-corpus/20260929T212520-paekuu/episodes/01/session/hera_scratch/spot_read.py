"""sdh-spot-check read on runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw R(B), bg-subtracted dR(B), sdh_onset, sdh_fft windows."""
import sys, warnings, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
from numpy.polynomial import polynomial as P
warnings.simplefilter("always")
for rid, n12 in ((6, 3.2), (7, -1.2)):
    run = open_run(f"data/{rid}"); print("="*80); print(summarize_run(run))
    chs = {c.cid: c for c in resolve_channels(run.metadata)}
    print({k: v.gain for k, v in chs.items()})
    B = run.col("magnet_field"); I = run.col("sr0_X") / chs["sr0"].gain; V = run.col("sr1_X") / chs["sr1"].gain
    R = np.abs(V / I); T = run.col("T_sample")
    o = np.argsort(B); B, R, T = B[o], R[o], T[o]
    print(f"run {rid}: B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts; R min/med/max {R.min():.1f}/{np.median(R):.1f}/{R.max():.1f} Ohm; I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K")
    FL = luttinger_frequency(abs(n12) * 1e16); print(f"F_L = {FL:.2f} T")
    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9, b_lo=0.3)
        print(on.summary())
        for t in on.tones:
            print(f"  tone {t.freq:6.2f} T  onset {t.onset_b:.2f}  censored={t.censored} marginal={t.marginal} harm_of={t.harmonic_of} harmonics={t.harmonics} contrast={t.contrast:.3g}")
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None
    # FFT windows
    fig, ax = plt.subplots(2, 2, figsize=(14, 9))
    ax[0, 0].plot(B, R, lw=0.7); ax[0, 0].set_xlabel("B (T)"); ax[0, 0].set_ylabel("Rxx (Ohm)"); ax[0, 0].set_title(f"run {rid} raw Rxx(B), n={n12:+.1f}e12 D=0")
    lo_c = 1.5 if rid == 6 else 1.0
    m = B >= lo_c
    cf = P.polyfit(B[m], R[m], 5); dR = R[m] - P.polyval(B[m], cf)
    ax[0, 1].plot(1 / B[m], dR, lw=0.7); ax[0, 1].set_xlabel("1/B (1/T)"); ax[0, 1].set_ylabel("dRxx (Ohm), deg-5 bg in B"); ax[0, 1].set_title(f"bg-subtracted, B>{lo_c} T")
    wins = [(lo_c, B.max()), (2.0, B.max()), (3.0, B.max()), (2.0, 6.0), (5.0, B.max())]
    for (a, b) in wins:
        try:
            f, s = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False, nfft=2048)
            ax[1, 0].plot(f, s[0] / s[0].max(), lw=0.8, label=f"[{a},{b:.0f}] T  dF={1/(1/a-1/b):.1f}")
        except Exception as e:
            print("fft fail", a, b, e)
    ax[1, 0].axvline(FL, color="k", ls="--", lw=0.8, label=f"F_L {FL:.1f}")
    ax[1, 0].set_xlim(0, 1.6 * FL); ax[1, 0].set_xlabel("F (T)"); ax[1, 0].set_ylabel("norm |FFT|"); ax[1, 0].legend(fontsize=7); ax[1, 0].set_title("sdh_fft, linear R, deg-5 bg")
    # log-R variant + peak list on main window
    f, s = sdh_fft(R[:, None], B, b_range=(lo_c, B.max()), bg_degree=5, log=True, nfft=2048)
    ax[1, 1].plot(f, s[0] / s[0].max(), lw=0.8, label="log R"); ax[1, 1].axvline(FL, color="k", ls="--", lw=0.8)
    ax[1, 1].set_xlim(0, 1.6 * FL); ax[1, 1].set_xlabel("F (T)"); ax[1, 1].set_title("sdh_fft log-R"); ax[1, 1].legend(fontsize=7)
    from scipy.signal import find_peaks
    f2, s2 = sdh_fft(R[:, None], B, b_range=(lo_c, B.max()), bg_degree=5, log=False, nfft=4096)
    sp = s2[0]; pk, pr = find_peaks(sp, prominence=0.05 * sp.max())
    sel = f2[pk] > 1.0
    print("FFT peaks (linear R, full window):", ", ".join(f"{f2[p]:.2f}T({sp[p]/sp.max():.2f})" for p in pk[sel][:12]))
    fig.tight_layout(); fig.savefig(f"hera_scratch/spot_run{rid}.png", dpi=100); print(f"saved hera_scratch/spot_run{rid}.png")
