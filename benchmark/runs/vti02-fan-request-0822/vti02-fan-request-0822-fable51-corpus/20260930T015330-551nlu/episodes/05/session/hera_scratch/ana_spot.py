"""Runs 6 + 7 — sdh-spot-check read (electron n = +3.2e12, hole n = -1.2e12; D = 0, run-5 cal).
Raw R(B) first, then onset (sdh_onset) and the 1/B FFT (sdh_fft) on the Nyquist-valid record, tones vs F_L and the model table."""
import warnings
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, sdh_fft, SdhOnsetError

H4E = 4.135667e-15 / 4                                   # h/4e: F_L = H4E * n  (n in m^-2)
MODEL = {6: dict(n=3.2, abab=(7.31, 25.78), abca=33.08),   # fs_count_b0 at u_D = 0 (ana-side call, this session)
         7: dict(n=-1.2, abab=(5.86, 6.54), abca=12.41)}
# Nyquist-valid low edge of each record for the fastest observed tone: run 6 sampled 50 mT below 1 T (7.3 T tone
# aliased below ~0.86 T) then 10 mT; run 7 sampled 20 mT throughout (fine for its tones down to ~0.5 T).
B_LO_VALID = {6: 0.9, 7: 0.71}

fig, axes = plt.subplots(2, 3, figsize=(17, 8.5))
reads = {}
for row, rid in enumerate((6, 7)):
    r = run(rid); B = r.col("magnet_field"); I = r.col("sr0_X") / (-1e6); R = r.col("sr1_X") / 1.0 / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    n12 = MODEL[rid]["n"]; F_L = H4E * abs(n12) * 1e16
    nu_lines = [abs(n12) * 1e16 * 4.135667e-15 / nu for nu in range(4, 80, 4)]
    # raw
    ax = axes[row, 0]; ax.plot(B, R, lw=0.7, color="C0")
    for b in nu_lines:
        if B.min() < b < B.max(): ax.axvline(b, color="gray", lw=0.4, alpha=0.5)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx = sr1_X / (sr0_X/-1e6)  (Ohm)")
    ax.set_title(f"run {rid} raw — n = {n12:+.1f}e12, D = 0 (grey: nu = 4k from the run-5 cal)")
    # onset on the Nyquist-valid record
    blo = B_LO_VALID[rid]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            on = sdh_onset(R, B, b_lo=blo, r_full_scale=50e-6 / 10e-9)
            print(f"===== run {rid}: n = {n12:+.2f}e12, F_L = {F_L:.1f} T; record B >= {blo} T (Nyquist-valid) =====")
            print(on.summary())
            tones = sorted([(t.freq, t.onset_b, t.censored, t.snr.max() if hasattr(t.snr, 'max') else np.nan) for t in on.tones])
        except SdhOnsetError as e:
            print(f"run {rid}: SdhOnsetError: {e}"); tones = []; on = None
    # bg-subtracted dRxx vs 1/B
    m = B >= blo; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax = axes[row, 1]; ax.plot(1 / B[m], dR, lw=0.7, color="C0"); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm), deg-5 bg in B")
    ax.set_title(f"run {rid} background-subtracted, B >= {blo} T")
    # FFT: full valid record + B-window split (equal halves in 1/B)
    ax = axes[row, 2]
    inv_hi, inv_lo = 1 / blo, 1 / B.max(); inv_mid = 0.5 * (inv_hi + inv_lo)
    wins = [("full", blo, B.max()), ("low-B half", blo, 1 / inv_mid), ("high-B half", 1 / inv_mid, B.max())]
    for k, (lab, lo, hi) in enumerate(wins):
        f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
        s = s[0]; s = s / s[f > 1.5].max()
        pk, _ = find_peaks(s, height=0.08, distance=6); pk = pk[f[pk] > 1.5]
        print(f"  FFT {lab:12s} [{lo:.2f}, {hi:.2f}] T  dF = {1/(1/lo-1/hi):.2f} T  peaks (T, rel): " + ", ".join(f"{f[p]:.1f} ({s[p]:.2f})" for p in pk[:9]))
        ax.plot(f, s + 1.1 * k, lw=0.8, label=f"{lab} [{lo:.2f}, {hi:.1f}] T")
    ax.axvline(F_L, color="k", ls="--", lw=1, label=f"F_L = {F_L:.1f} T")
    for fm, c, lab in ((MODEL[rid]["abab"][0], "r", "ABAB light/heavy (model)"), (MODEL[rid]["abab"][1], "r", None)):
        ax.axvline(fm, color=c, ls=":", lw=1, label=lab)
    ax.set_xlim(0, 2.0 * F_L); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm., offset)"); ax.legend(fontsize=7, loc="upper right")
    ax.set_title(f"run {rid} FFT in 1/B — full + B-window split")
    reads[rid] = dict(F_L=F_L, tones=tones, onset=None if on is None else on.onset_b)
fig.tight_layout(); plt.show()
for rid, d in reads.items():
    print(f"run {rid}: F_L {d['F_L']:.1f} T; onset_b {d['onset']}; tones (F, onset, censored): " +
          ", ".join(f"{f:.1f} T @ {ob:.2f}{'c' if c else ''}" for f, ob, c, _ in d["tones"]))
