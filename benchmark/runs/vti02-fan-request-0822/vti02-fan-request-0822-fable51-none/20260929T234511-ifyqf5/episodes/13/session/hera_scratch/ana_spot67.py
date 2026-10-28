"""Runs 6 + 7 (sdh-spot-check, e and h side at D = 0): raw R(B), background-subtracted
oscillations, FFT in 1/B, onset. Scratch first."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

here = Path(__file__).resolve().parent.parent
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(here / "data" / str(rid))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.2f}e12, F_L(full, 4-fold) = {FL:.1f} T; T {T.min():.3f}-{T.max():.3f} K; "
          f"I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.0f}..{R.max():.0f} Ohm")
    # point-to-point scatter at low B (noise estimate)
    m = (B > 0.3) & (B < 1.0)
    d = np.diff(R[m]); print(f"  low-B (0.3-1 T) R med {np.median(R[m]):.1f}, pt-pt rms {np.std(d)/np.sqrt(2):.2f} Ohm")
    # filling factors at 10 T
    nB = abs(n12) * 1e16 / (10.0 * 1.602e-19 / 6.626e-34) ; print(f"  nu at 10 T = {nB:.1f}; nu at 5 T = {2*nB:.1f}")
    ax[0, j].plot(B, R, lw=0.8); ax[0, j].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 — raw |Rxx|"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    # 1/B plot with 4-fold LL index guide
    m = B > 1.0
    ax[1, j].plot(1 / B[m], R[m], lw=0.8); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("R (Ohm)")
    for nu in range(4, 80, 4):
        b = abs(n12) * 1e16 * 6.626e-34 / (nu * 1.602e-19)
        if 1.0 < b < 10: ax[1, j].axvline(1 / b, color="0.8", lw=0.5)
    ax[1, j].set_title("vs 1/B; grey = 4-fold LL fillings nu = 4k at the nominal n")
    for b_lo in (1.5, 2.5):
        try:
            freqs, spec = sdh_fft(R[:, None], B, b_range=(b_lo, 10.0), nfft=2048, bg_degree=3, log=False)
            sp = spec[0]; fm = (freqs > 2) & (freqs < 120)
            pk = freqs[fm][np.argsort(sp[fm])[::-1][:6]]
            print(f"  FFT window {b_lo}-10 T (bg deg 3, linear R): top peaks {np.round(np.sort(pk),1)} T")
            ax[2, j].plot(freqs, sp / sp[fm].max(), label=f"{b_lo}-10 T")
        except Exception as e:
            print("  fft fail", e)
    ax[2, j].axvline(FL, color="r", ls="--", label=f"F_L 4-fold {FL:.1f} T"); ax[2, j].axvline(FL / 2, color="r", ls=":", label="F_L/2")
    ax[2, j].set_xlim(0, 80); ax[2, j].set_xlabel("F (T)"); ax[2, j].legend(fontsize=7); ax[2, j].set_title("SdH FFT in 1/B")
    try:
        so = sdh_onset(R, B, b_lo=1.0, r_full_scale=50e-6 / 10e-9, bg_degree=3)
        print(so.summary())
    except SdhOnsetError as e:
        print("  onset:", e)
fig.tight_layout(); fig.savefig(here / "hera_scratch" / "spot67_raw_fft.png", dpi=110)
print("saved")
