"""Runs 6 / 7 — sdh-spot-check read (electron n = +3.2e12, hole n = -1.2e12; D = 0, run-5 cal).
Raw R(B) first, then sdh_onset (per-tone onsets, harmonic flags) and sdh_fft in B-windows,
tones read against F_L and the model's ABAB / ABCA F(n)."""
import warnings
from hera.analysis import sdh_onset, SdhOnsetError

SPOTS = {6: dict(n=+3.2, side="electron", abab=(7.3, 25.8), abca=33.1),   # model F(n) at this n (fs_count_b0, ud = 0)
         7: dict(n=-1.2, side="hole",     abab=(5.9, 6.5),  abca=12.4)}
fig, ax = plt.subplots(2, 3, figsize=(17, 8.5))
reads = {}
for k, (rid, sp) in enumerate(SPOTS.items()):
    r = run(rid)
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = r.col("sr1_X") / I     # sr1 gain 1; I from sr0 (Ithaco -1e6)
    o = np.argsort(B); B, I, R = B[o], I[o], R[o]
    FL = float(luttinger_frequency(abs(sp["n"]) * 1e16))
    fs = 50e-6 / np.median(I)                                                        # sr1 at 50 uV -> 5 kOhm FS
    print(f"run {rid} ({sp['side']}, n = {sp['n']:+.2f}e12, F_L = {FL:.1f} T): {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"I_bias {np.median(I)*1e9:.2f} nA, R {R.min():.0f}..{R.max():.0f} Ohm (FS {fs:.0f}), T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, interrupted={r.interrupted}")
    # raw
    ax[k, 0].plot(B, R, lw=0.7); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("Rxx sr1 (Ohm)")
    ax[k, 0].set_title(f"run {rid} raw — {sp['side']} n = {sp['n']:+.1f}e12, D = 0")
    # onset + tones
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=fs, b_lo=0.3); print(on.summary())
        except SdhOnsetError as e:
            on = None; print("SdhOnsetError:", e)
        for ww in w: print("  warn:", ww.message)
    blo = max(on.onset_b, 0.3) if on else 0.5
    m = B >= blo
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[k, 1].plot(1 / B[m], dR, lw=0.7); ax[k, 1].set_xlabel("1/B (1/T)"); ax[k, 1].set_ylabel("dRxx (Ohm)"); ax[k, 1].set_title("bg-subtracted (deg-5 poly in B)")
    # FFT in B-windows (the B-window split: a breakdown / total-density tone strengthens with B relative to the fundamentals)
    for cut, col in [(max(blo, 0.5), "C0"), (1.5, "C1"), (3.0, "C2"), (4.5, "C3")]:
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False, nfft=4096)
        sp_ = spec[0]; sel = (f > 2.0) & (f < 2.5 * FL); norm = sp_[sel].max()
        ax[k, 2].plot(f, sp_ / norm, col, lw=0.9, label=f"B > {cut:.1f} T  (dF {1/(1/cut-1/B.max()):.1f} T)")
        pk = np.argsort(sp_[sel])[::-1]
        tops = []
        for j in pk:
            if all(abs(f[sel][j] - t) > 1.5 for t in tops): tops.append(f[sel][j])
            if len(tops) == 4: break
        print(f"  FFT B > {cut:.1f} T: dF_res = {1/(1/cut-1/B.max()):.2f} T; top peaks (T): " + ", ".join(f"{t:.1f} ({sp_[sel][np.argmin(abs(f[sel]-t))]/norm:.2f})" for t in tops))
    for lab, F in [("F_L", FL), ("ABAB", sp["abab"][0]), ("ABAB", sp["abab"][1])]:
        ax[k, 2].axvline(F, color="k" if lab == "F_L" else "r", ls=":", lw=0.9); ax[k, 2].text(F, 1.03, f"{lab} {F:.1f}", fontsize=7, rotation=90, va="bottom")
    ax[k, 2].set_xlim(0, 2.2 * FL); ax[k, 2].set_ylim(0, 1.15); ax[k, 2].set_xlabel("F (T)"); ax[k, 2].set_ylabel("FFT (norm. per window)")
    ax[k, 2].legend(fontsize=7, loc="upper right"); ax[k, 2].set_title("1/B FFT by low-B cutoff; model ABAB pair (red), F_L (black)")
    reads[rid] = on
fig.tight_layout(); plt.show()
