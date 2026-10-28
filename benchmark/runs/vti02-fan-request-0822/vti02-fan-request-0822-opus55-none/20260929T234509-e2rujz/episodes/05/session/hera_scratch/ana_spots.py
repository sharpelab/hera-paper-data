"""Runs 6/7 sdh-spot-check read: raw R(B), sdh_onset tones, FFT, vs model frequencies."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_onset, sdh_fft, luttinger_frequency
out = {}
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = open_run(f"data/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    T = r.col("T_sample"); itg = r.col("k_2400_tg_curr"); ibg = r.col("k_2400_bg_curr")
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"--- run {rid}: n={n12:+.1f}e12, F_L={FL:.1f} T; R(0)={R[0]:.1f}, R(max B)={R[-1]:.1f}, R range {R.min():.1f}-{R.max():.1f} Ohm; "
          f"I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f}; Itg {itg.min()*1e12:.0f}..{itg.max()*1e12:.0f} pA Ibg {ibg.min()*1e12:.0f}..{ibg.max()*1e12:.0f} pA")
    try:
        on = sdh_onset(R, B, r_full_scale=50e-6/10e-9)
        print(on.summary())
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e); on = None
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_title(f"run {rid} raw R(B), n={n12:+.1f}e12 D=0"); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("R (Ohm)")
    for blo in (1.5, 3.0):
        m = B > blo
        f, sp = sdh_fft(R[m][:, None], B[m], nfft=4096, bg_degree=5)
        sp = sp[0]; ok = (f > 2) & (f < 3 * FL)
        pk = f[ok][np.argsort(sp[ok])[::-1][:6]]
        print(f"  FFT B>{blo}: top freqs {np.round(np.sort(pk),1)}")
        ax[1, k].plot(f[ok], sp[ok] / sp[ok].max(), label=f"B>{blo} T")
    ax[1, k].axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f}"); ax[1, k].set_xlabel("F (T)"); ax[1, k].legend(); ax[1, k].set_title(f"run {rid} FFT (log R, poly5 bg)")
    # detrended vs 1/B
    m = B > 1.0
    y = np.log10(R[m]); cf = np.polyfit(B[m], y, 5); d = y - np.polyval(cf, B[m])
    ax[0, 2].plot(1 / B[m], d + 0.05 * k, lw=0.6, label=f"run {rid}")
    out[rid] = (B, R)
ax[0, 2].set_xlabel("1/B (1/T)"); ax[0, 2].set_title("detrended log R vs 1/B"); ax[0, 2].legend()
ax[1, 2].axis("off")
fig.tight_layout(); fig.savefig("hera_scratch/spots_67.png", dpi=90)
