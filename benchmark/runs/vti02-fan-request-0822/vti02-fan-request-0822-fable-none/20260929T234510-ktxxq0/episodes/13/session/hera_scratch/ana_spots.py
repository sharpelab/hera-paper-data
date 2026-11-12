"""SdH spot checks, runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw traces, onsets, FFT tones."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, sdh_onset, SdhOnsetError, luttinger_frequency

IB = 10e-9  # A

out = {}
fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for i, (rid, side, n12) in enumerate([(6, "electron", 3.2), (7, "hole", -1.2)]):
    r = open_run(f"data/{rid}")
    B = r.col("magnet_field")
    R = r.col("sr1_X") / 1.0 / IB
    o = np.argsort(B)
    B, R = B[o], R[o]
    F_full = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n===== run {rid} ({side}, n={n12:+.1f}e12, F_full={F_full:.1f} T) =====")
    ax[i, 0].plot(B, R, lw=0.6)
    ax[i, 0].set_xlabel("B (T)"); ax[i, 0].set_ylabel("R_xx (Ohm)")
    ax[i, 0].set_title(f"run {rid} {side} n={n12:+.1f}e12 raw")
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / IB)
        print(so.summary())
        out[rid] = so
    except SdhOnsetError as e:
        print(f"sdh_onset FAILED: {e}")
        so = None
    # FFT over the high-B window
    for blo, sty in [(1.5, "-"), (3.0, "--")]:
        m = B >= blo
        if m.sum() < 50:
            continue
        freqs, spec = sdh_fft(R[m][:, None], B[m], nfft=4096, log=False)
        sp = spec[0]
        ax[i, 1].plot(freqs, sp / sp[freqs > 3].max(), sty, lw=0.8, label=f"B>{blo}")
        # top peaks
        from scipy.signal import find_peaks
        sel = freqs > 3
        pk, _ = find_peaks(sp[sel], height=0.15 * sp[sel].max())
        fpk = freqs[sel][pk]; hpk = sp[sel][pk]
        srt = np.argsort(hpk)[::-1][:6]
        print(f"  FFT B>{blo}: peaks (T, rel amp): " +
              ", ".join(f"{fpk[j]:.1f} ({hpk[j]/hpk[srt[0]]:.2f})" for j in srt))
    ax[i, 1].axvline(F_full, color="k", ls=":", lw=1, label=f"F_full {F_full:.1f} T")
    ax[i, 1].set_xlim(0, 60); ax[i, 1].set_xlabel("F (T)"); ax[i, 1].set_ylabel("norm FFT")
    ax[i, 1].legend(fontsize=7); ax[i, 1].set_title(f"run {rid} SdH FFT (1/B)")
fig.tight_layout()
fig.savefig("hera_scratch/spots_sdh.png", dpi=110)
print("\nsaved hera_scratch/spots_sdh.png")
