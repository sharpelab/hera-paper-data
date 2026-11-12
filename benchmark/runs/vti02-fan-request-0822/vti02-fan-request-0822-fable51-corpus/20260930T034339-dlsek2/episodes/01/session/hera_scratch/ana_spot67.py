"""Runs 6/7 — sdh-spot-check read (Step 3): raw R(B) both sides, onset (valid-sampling record), 1/B FFT vs F_L and the model templates."""
import warnings
from scipy.signal import find_peaks
from hera.analysis import resolve_channels, sdh_onset, sdh_fft, SdhOnsetError
FL = lambda n: cst.h/(4*cst.e)*abs(n)*1e16          # T, g = 4, n in 1e12 cm^-2
MODEL = {6: dict(abab=(7.31, 25.78), abca=33.08), 7: dict(abab=(5.86, 6.54), abca=12.41)}   # fs_count_b0 at n = +3.2 / -1.2
spots = {6: 3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(14, 12))
tones = {}
for j, (rid, n) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.metadata)}
    B = r.col("magnet_field"); I = r.col("sr0_X")/ch["sr0"].gain; R = (r.col("sr1_X")/ch["sr1"].gain)/I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]; T = r.col("T_sample")
    print(f"run {rid}: n = {n:+.1f}e12, D = 0, F_L = {FL(n):.2f} T; B {B.min():.2f}-{B.max():.2f} T ({len(B)} pts); R {R.min():.0f}..{R.max():.0f} Ohm "
          f"(fs max {R.max()/5000:.2f} of 5 kOhm); I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K; interrupted={r.interrupted}")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm, signed)"); ax[0, j].set_title(f"run {rid}: n = {n:+.1f}e12, D = 0 — raw R(B)")
    # onset on the uniformly-sampled record only (run 6: 50 mT below 1 T under-samples the 7 T tone -> b_lo = 1.0)
    blo = 1.0 if rid == 6 else 0.3
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, b_lo=blo, r_full_scale=50e-6/10e-9); print(on.summary()); onset = on.onset_b
        except SdhOnsetError as e:
            print("SdhOnsetError:", e); onset = None
        for ww in w: print("  warn:", str(ww.message)[:160])
    m = B >= blo; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1/B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dRxx (Ohm), deg-5 bg in B removed")
    ax[1, j].set_title(f"run {rid}: dR vs 1/B, B >= {blo} T; onset_b = {onset} T" + (" (censored: record edge)" if rid == 6 else ""))
    wins = [(max(blo, 1.2), B.max()), (2.5, B.max()), (4.0, B.max())]
    tones[rid] = {}
    for (lo, hi), col in zip(wins, ("k", "C1", "C2")):
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
        s = sp[0]/sp[0].max(); dF = 1/(1/lo - 1/hi)
        pk, _ = find_peaks(s, prominence=0.05); pk = sorted(pk, key=lambda p: -s[p])[:7]
        tones[rid][(lo, hi)] = [(round(float(f[p]), 1), round(float(s[p]), 2)) for p in sorted(pk)]
        print(f"  FFT [{lo:.1f},{hi:.0f}] T, dF = {dF:.2f} T: " + ", ".join(f"{f[p]:.1f} T ({s[p]:.2f})" for p in sorted(pk)))
        ax[2, j].plot(f, s, color=col, lw=0.9, label=f"B {lo:.1f}-{hi:.0f} T (dF {dF:.1f} T)")
    for k, lab in ((1, "F_L"), (0.9, "0.9 F_L")):
        ax[2, j].axvline(k*FL(n), color="gray", ls=":" if k == 1 else "--", lw=0.8); ax[2, j].text(k*FL(n), 1.02, lab, fontsize=7, ha="center")
    for F in MODEL[rid]["abab"]: ax[2, j].axvline(F, color="C3", ls="-.", lw=0.8)
    ax[2, j].text(MODEL[rid]["abab"][0], 0.9, "ABAB model pair", color="C3", fontsize=7)
    ax[2, j].set_xlim(0, 2.1*FL(n)); ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("|FFT| (norm)"); ax[2, j].legend(fontsize=7); ax[2, j].set_title(f"run {rid}: 1/B FFT; F_L = {FL(n):.1f} T; ABAB model {MODEL[rid]['abab']}, ABCA {MODEL[rid]['abca']} T")
fig.suptitle("vti-02 sdh-spot-check: run 6 electron n = +3.2e12 (left), run 7 hole n = -1.2e12 (right); D = 0, T = 1.2 K, sr1 50 uV"); fig.tight_layout(); plt.show()
