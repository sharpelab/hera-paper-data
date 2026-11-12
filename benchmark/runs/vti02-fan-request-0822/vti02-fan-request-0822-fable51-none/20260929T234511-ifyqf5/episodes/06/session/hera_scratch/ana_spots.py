# Runs 6-7 (sdh-spot-check, e- and h-side at D = 0). Raw first: R(B) = (sr1_X/gain)/I_drain, then the SdH read (onset tool + FFT in 1/B).
import warnings
from hera.analysis import resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency
spots = {6: +3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"run {rid}: n = {n12:+.1f}e12 (F_L = nh/4e = {FL:.1f} T), B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts, R {R.min():.0f}..{R.max():.0f} Ohm, "
          f"I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, interrupted={r.interrupted}")
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx = sr1_X / I_drain (Ohm)")
    ax[0, k].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 (raw)")
    m = B > 1.0
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1, k].plot(1 / B[m], R[m] - bg, lw=0.7); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("dRxx (Ohm), deg-5 bg in B")
    for blo, c in [(1.5, "C0"), (2.5, "C1"), (4.0, "C2")]:
        mm = B >= blo
        f, sp = sdh_fft(R[mm][:, None], B[mm], b_range=(blo, 10.0), nfft=2048, bg_degree=5, log=False)
        sp = sp[0]; sel = (f > 2) & (f < 60)
        ax[2, k].plot(f[sel], sp[sel] / sp[sel].max(), color=c, lw=0.9, label=f"B > {blo} T")
    for x, lab, c in [(FL, "F_L", "r"), (FL / 2, "F_L/2", "orange"), (FL / 4, "F_L/4", "g")]:
        ax[2, k].axvline(x, color=c, ls="--", lw=0.8, label=lab)
    ax[2, k].set_xlabel("F (T)"); ax[2, k].set_ylabel("FFT amp (norm.)"); ax[2, k].legend(fontsize=7)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            on = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except SdhOnsetError as e:
        print(f"  sdh_onset: {e}")
fig.suptitle("vti-02 sdh-spot-check runs 6 (e) / 7 (h): raw R(B), detrended vs 1/B, FFT in 1/B")
fig.tight_layout(); plt.show()
