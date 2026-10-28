# SdH spot checks: run 6 (electron, n=+3.2e12, B 0->10 T) and run 7 (hole, n=-1.2e12, B 10->0.3 T)
# Raw traces + sdh_onset tone tables + FFT spectra; compare against Luttinger expectations.
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel, sdh_fft, sdh_onset, SdhOnsetError

FS_OHM = 50e-6 / 10e-9  # 50 uV sensitivity / 10 nA = 5 kOhm full scale

fig, axes = plt.subplots(2, 2, figsize=(12, 7))
for row, (rid, tag, n12) in enumerate([(6, "electron n=+3.2e12", 3.2), (7, "hole n=-1.2e12", -1.2)]):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    I = r.col(cur.col) / cur.gain
    vch = [c for c in chans if not c.is_current][0]
    R = (r.col(vch.col) / vch.gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B)
    B, R = B[o], R[o]

    # Luttinger expectation: F_full = |n| h/(4e), single full-density FS
    from scipy.constants import h, e
    F_full = abs(n12) * 1e16 * h / (4 * e)

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ω)")
    ax.set_title(f"run {rid} raw — {tag}")

    print(f"\n===== run {rid} ({tag}); F_full(Luttinger) = {F_full:.1f} T =====")
    try:
        ons = sdh_onset(R, B, r_full_scale=FS_OHM)
        print(ons.summary())
        tones = [(t.freq, t.contrast, t.onset_b, t.harmonic_of) for t in ons.tones]
    except SdhOnsetError as ex:
        print("sdh_onset FAILED:", ex)
        tones = []

    freqs, spec = sdh_fft(R[:, None], B, b_range=(1.5, 10.0), nfft=4096)
    sp = spec[0]
    ax = axes[row, 1]
    ax.plot(freqs, sp, lw=0.8)
    ax.axvline(F_full, color="k", ls="--", lw=0.8, label=f"F_full {F_full:.1f} T")
    for f, c, ob, hof in tones:
        ax.axvline(f, color="C3", ls=":", lw=0.8)
    ax.set_xlim(0, 80); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT|")
    ax.set_title(f"run {rid} SdH FFT (1.5–10 T window)")
    ax.legend(fontsize=8)

fig.tight_layout()
fig.savefig("hera_scratch/spots_fft.png", dpi=120)
print("\nsaved hera_scratch/spots_fft.png")
