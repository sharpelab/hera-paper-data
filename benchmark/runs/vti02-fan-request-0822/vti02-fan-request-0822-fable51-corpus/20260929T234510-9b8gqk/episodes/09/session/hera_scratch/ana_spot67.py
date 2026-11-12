"""sdh-spot-check read, runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12), D = 0, T = 1.2 K:
raw Rxx(B) first, then sdh_onset per-tone tracks, FFT stability sweep (cutoff x bg_degree), B-window split."""
import warnings
from hera.analysis import sdh_onset, SdhOnsetError

h_4e = cst.h / (4 * cst.e)   # T per m^-2
fig, axes = plt.subplots(2, 3, figsize=(17, 8))
spot = {}
for row, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = run(rid); print(f"===== run {rid} =====\n{summarize_run(r)}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = r.col("sr1_X") / 1.0 / I     # channel arithmetic per device card
    o = np.argsort(B); B, R = B[o], R[o]
    Ib = float(np.nanmedian(I)); fs_R = 50e-6 / abs(Ib)                                 # sr1 sens 50 uV both runs
    FL = h_4e * abs(n12) * 1e16
    print(f"I_bias {Ib*1e9:.2f} nA; R {R.min():.0f}..{R.max():.0f} Ohm (max {np.abs(R).max()/fs_R:.1%} of the {fs_R:.0f} Ohm full scale); "
          f"T_sample {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; F_L(g=4) = {FL:.2f} T")
    ax = axes[row, 0]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx sr1 (Ohm)")
    ax.set_title(f"run {rid} raw: n = {n12:+.1f}e12, D = 0, F_L = {FL:.1f} T")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=fs_R); print(on.summary()); onset = on.onset_b
        except SdhOnsetError as e:
            print("SdhOnsetError:", e); onset = 1.0
        for ww in w: print("WARN:", ww.message)
    bmax = float(B.max()); cut0 = max(onset, float(B.min()) + 0.05)
    ax = axes[row, 1]
    for cut, deg in [(cut0, 5), (cut0 + 0.5, 5), (cut0 + 1.0, 5), (2.0, 5), (cut0, 3), (cut0, 7)]:
        f, s = sdh_fft(R[:, None], B, b_range=(cut, bmax), bg_degree=deg, log=False, nfft=8192); s = s[0] / s[0].max()
        ax.plot(f, s, lw=0.8, label=f"cut {cut:.2f} T, deg {deg}")
        pk = f[(s > 0.15) & np.r_[True, s[1:] > s[:-1]] & np.r_[s[:-1] > s[1:], True]]
        print(f"  FFT [{cut:.2f}, {bmax:.0f}] T deg {deg}: peaks > 15 % at {np.round(pk[pk < 2 * FL], 2)} T   (dF = {1/(1/cut - 1/bmax):.2f} T)")
    for k, lab in [(1, "F_L"), (0.72, "0.72 F_L"), (0.28, "0.28 F_L")]:
        ax.axvline(k * FL, color="k", ls=":", lw=0.8); ax.text(k * FL, 0.97, lab, rotation=90, fontsize=7, va="top")
    ax.set_xlim(0, 1.6 * FL); ax.set_xlabel("F (T)"); ax.set_title("FFT in 1/B (norm.) — stability sweep"); ax.legend(fontsize=6)
    ax = axes[row, 2]; mid = 2 / (1 / cut0 + 1 / bmax)
    for a, b, lab in [(cut0, mid, "low-B half"), (mid, bmax, "high-B half")]:
        f, s = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False, nfft=8192); s = s[0] / s[0].max()
        ax.plot(f, s, lw=0.8, label=f"{lab} [{a:.2f}, {b:.2f}] T")
    for k in (1, 0.72, 0.28): ax.axvline(k * FL, color="k", ls=":", lw=0.8)
    ax.set_xlim(0, 1.6 * FL); ax.set_xlabel("F (T)"); ax.set_title("B-window split (1/B midpoint)"); ax.legend(fontsize=6)
    spot[rid] = dict(FL=FL, onset=onset, fs_R=fs_R)
fig.tight_layout(); plt.show()
