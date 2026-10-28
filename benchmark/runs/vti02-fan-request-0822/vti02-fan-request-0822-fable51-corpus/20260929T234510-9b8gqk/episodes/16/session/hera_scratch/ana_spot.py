"""Runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12): sdh-spot-check read. Raw first, then per-tone onsets on the
fine-grid segment (B >= 1 T), zero-padded FFT peak positions, and the model's ABAB pair / F_L overlay."""
import warnings, sys
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, SdhOnsetError
sys.path.insert(0, str(Path.home() / "measurement_env" / "hera" / "models" / "tetralayer_fs_count"))
from fs_count_b0 import abab_fs

SR0_GAIN = -1e6; RFS_50UV = 50e-6 / 10e-9     # 5 kOhm full scale at 10 nA (both spot checks ran sr1 at 50 uV)
h_over_4e = cst.h / (4 * cst.e)

def padded_fft(B, R, lo, hi, nfft=2**17):
    m = (B >= lo) & (B <= hi)
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])          # background removed in B, then 1/B
    x = 1 / B[m]; xs = np.linspace(x.min(), x.max(), 4096); y = np.interp(xs, x[::-1], dR[::-1]) * np.hanning(4096)
    sp = np.abs(np.fft.rfft(y, nfft)); f = np.fft.rfftfreq(nfft, xs[1] - xs[0])
    return f, sp / sp.max(), 1 / (x.max() - x.min())

fig, ax = plt.subplots(3, 2, figsize=(14, 12))
spots = {}
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = run(rid); B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / SR0_GAIN); T = r.col("T_sample")
    o = np.argsort(B); B, R, T = B[o], R[o], T[o]
    FL = h_over_4e * abs(n12) * 1e16
    model = [F for F, k in abab_fs(n12 * 1e16)[1]]
    print(f"run {rid}: n = {n12:+.1f}e12, D = 0, {len(B)} pts B {B.min():.2f}-{B.max():.2f} T, T_sample {T.min():.3f}-{T.max():.3f} K, "
          f"R {R.min():.0f}-{R.max():.0f} Ohm (max {R.max()/RFS_50UV:.2f} FS), interrupted={r.interrupted}; F_L = {FL:.2f} T; model ABAB orbits {np.round(model, 2)} T, ABCA {FL:.1f} T")
    # raw
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid} raw: n = {n12:+.1f}e12, D = 0, sr1 50 uV")
    # onset on the fine-grid segment only (run 6 is 50 mT below 1 T: cannot carry a 7 T tone; run 7 is 20 mT throughout)
    m = B >= 1.0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        on = sdh_onset(R[m], B[m], r_full_scale=RFS_50UV, b_lo=1.0)
    print(on.summary())
    cf = np.polyfit(B[m], R[m], 5)
    ax[1, j].plot(1 / B[m], R[m] - np.polyval(cf, B[m]), lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("dRxx (Ohm), deg-5 bg in B, B >= 1 T")
    for t in on.tones[:4]:
        ax[1, j].axvline(1 / t.onset_b, color="r", ls=":", lw=0.8)
    ax[1, j].set_title(f"onset per tone (red): " + ", ".join(f"{t.freq:.1f} T @ {t.onset_b:.2f} T" for t in on.tones[:4]), fontsize=8)
    # FFT windows, zero-padded so peak positions are not quantized to dF
    for (lo, hi) in ((1.4, 10.0), (1.4, 4.0), (4.0, 10.0)):
        f, sp, dF = padded_fft(B, R, lo, hi)
        pk, _ = find_peaks(sp, prominence=0.04); pk = pk[f[pk] > 1.5]; top = sorted(pk[np.argsort(sp[pk])[::-1][:7]], key=lambda p: f[p])
        print(f"  FFT [{lo},{hi}] T dF = {dF:.2f} T: " + ", ".join(f"{f[p]:.1f} ({sp[p]:.2f})" for p in top))
        ax[2, j].plot(f, sp, lw=0.8, label=f"[{lo},{hi}] T, dF {dF:.1f}")
    ax[2, j].axvline(FL, color="k", ls="--", label=f"F_L = {FL:.1f} T (scale 1)")
    for F in model: ax[2, j].axvline(F, color="tab:orange", ls=":", label=f"model ABAB {F:.1f} T")
    ax[2, j].set_xlim(0, 2.0 * FL); ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("|FFT| (norm)"); ax[2, j].legend(fontsize=7)
    spots[rid] = dict(n=n12, FL=FL, onset=on.onset_b, tones=[(round(t.freq, 1), round(t.onset_b, 2), round(t.snr_max, 0)) for t in on.tones[:5]])
fig.suptitle("vti-02 sdh-spot-check: runs 6 (e) and 7 (h) at D = 0 — raw, background-subtracted in 1/B, FFT vs F_L and the model ABAB pair")
fig.tight_layout(); plt.show()
print(spots)
