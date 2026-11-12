"""SdH spot-check read of runs 6 (e-side n=+3.2e12) and 7 (h-side n=-1.2e12): onset, tones, FFT."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, warnings
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
I_BIAS = 10e-9; FS_R = 50e-6 / I_BIAS
out = {}
fig, axs = plt.subplots(2, 3, figsize=(17, 8))
for k, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"data/{rid}")
    print("=" * 30, "run", rid); print(summarize_run(r)); print("columns:", r.metadata["columns"])
    B = r.col("magnet_field"); I = r.col("sr0_X") / (-1e6); R = r.col("sr1_X") / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"n = {n12:+.2f}e12 -> F_L = {FL:.2f} T; R(B~0.3) = {np.interp(0.3, B, R):.1f}, R max {R.max():.1f} Ohm ({R.max()/FS_R*100:.1f} % FS); I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=FS_R, b_lo=0.3)
            print(on.summary()); out[rid] = on
            print("onset_b", on.onset_b, "clip_high_b", getattr(on, "clip_high_b", None))
            for t in on.tones:
                print("  tone", {a: getattr(t, a) for a in dir(t) if not a.startswith("_") and not callable(getattr(t, a)) and a not in ("snr", "amp", "b_centers")})
            print("  untracked", getattr(on, "untracked", None))
        except SdhOnsetError as ex:
            print("SdhOnsetError:", ex); on = None
        for ww in w: print("  WARN:", ww.message)
    # FFT at a few low cutoffs
    ax = axs[k]
    ax[0].plot(B, R, lw=0.6); ax[0].set_xlabel("B (T)"); ax[0].set_ylabel("Rxx (Ohm)"); ax[0].set_title(f"run {rid}: n={n12:+.2f}e12 D=0 raw")
    for cut, c in [(1.5, "C0"), (2.5, "C1"), (4.0, "C2"), (6.0, "C3")]:
        if cut >= B.max() - 1: continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False, nfft=4096)
        sp = spec[0]; sel = (f > 1) & (f < 3 * FL)
        pk, pr = find_peaks(sp[sel], prominence=0.15 * sp[sel].max())
        top = sorted(zip(pr["prominences"], f[sel][pk], sp[sel][pk]), reverse=True)[:6]
        dF = 1 / (1 / cut - 1 / B.max())
        print(f"  FFT window [{cut},{B.max():.1f}] T, dF={dF:.2f} T: peaks (F, F/F_L, amp) " + ", ".join(f"({F:.1f}, {F/FL:.2f}, {a:.2g})" for _, F, a in top))
        ax[2].plot(f, sp / sp[sel].max(), c, lw=0.8, label=f"cut {cut} T")
    # bg-subtracted trace vs 1/B for the window above 1.5 T
    m = B >= 1.5
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    ax[1].plot(1 / B[m], dR, lw=0.6); ax[1].set_xlabel("1/B (1/T)"); ax[1].set_ylabel("dRxx (Ohm), deg-5 bg removed, B>1.5 T")
    for F, lab, c in [(FL, "F_L", "k")]:
        ax[2].axvline(F, color=c, ls="--", lw=0.8, label=lab)
    ax[2].set_xlim(0, 2.2 * FL); ax[2].set_xlabel("F (T)"); ax[2].set_ylabel("FFT amp (norm)"); ax[2].legend(fontsize=7)
fig.tight_layout(); fig.savefig("hera_scratch/spot_runs67.png", dpi=110)
print("saved hera_scratch/spot_runs67.png")
