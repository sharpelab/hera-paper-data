# SdH spot-check analysis — runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D = 0
# Raw traces + sdh_onset tone tables + FFT spectra; compare against Luttinger expectations.
import json
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_fft, sdh_onset, luttinger_frequency, SdhOnsetError

CAL = json.load(open("hera_scratch/cal_run5.json"))

runs = {6: ("electron n=+3.2e12", +3.2e16), 7: ("hole n=-1.2e12", -1.2e16)}  # n in m^-2
fig, ax = plt.subplots(2, 3, figsize=(15, 8))

for i, (rid, (label, n_SI)) in enumerate(runs.items()):
    r = open_run(f"data/{rid}")
    chans = resolve_channels(r.meta)
    print(f"--- run {rid}: {label}")
    print("channels:", [(c.cid, c.label, c.gain, c.is_current) for c in chans])
    B = r.col("magnet_field")
    sr1 = next(c for c in chans if c.cid == "sr1")
    sr0 = next(c for c in chans if c.cid == "sr0")
    I = np.abs(r.col("sr0_X") / sr0.gain)
    R = (r.col("sr1_X") / sr1.gain) / I  # measured current per point
    sens1 = float(r.meta["measurement_config"].get("sr1_sensitivity", 50e-6))
    fs_R = sens1 / np.median(I)
    print(f"I median {np.median(np.abs(I))*1e9:.3f} nA, R range {R.min():.1f}..{R.max():.1f} Ohm, R_fs {fs_R:.0f} Ohm")

    # sort ascending in B for analysis
    o = np.argsort(B)
    Bs, Rs = B[o], R[o]
    m = Bs > 0.25
    Bs, Rs = Bs[m], Rs[m]

    F_L = luttinger_frequency(np.array([n_SI]))[0]
    print(f"Luttinger full-degeneracy F = {F_L:.1f} T")

    try:
        onset = sdh_onset(Rs, Bs, r_full_scale=fs_R)
        print(onset.summary())
    except SdhOnsetError as e:
        onset = None
        print("SdhOnsetError:", e)

    # FFT over the high-B window (above ~1.5 T; and a conservative >3 T variant)
    for j, blo in enumerate([1.5, 3.0]):
        freqs, spec = sdh_fft(Rs[:, None], Bs, b_range=(blo, Bs.max()), nfft=4096)
        sp = spec[0]
        a = ax[i, 1 + j]
        a.plot(freqs, sp / sp.max())
        a.axvline(F_L, color="r", ls="--", lw=1, label=f"F_L={F_L:.1f} T")
        for frac, c in [(0.5, "orange")]:
            a.axvline(F_L * frac, color=c, ls=":", lw=1)
        a.set_xlim(0, 60)
        a.set_xlabel("F (T)")
        a.set_title(f"run {rid} FFT, B>{blo} T")
        a.legend(fontsize=7)
        # print top peaks
        from scipy.signal import find_peaks

        pk, props = find_peaks(sp, height=sp.max() * 0.05, distance=8)
        top = sorted(zip(sp[pk], freqs[pk]))[::-1][:8]
        print(f"FFT peaks (B>{blo} T): " + ", ".join(f"{f:.1f} T (a={a_:.2g})" for a_, f in top if f > 1))

    a = ax[i, 0]
    a.plot(Bs, Rs, lw=0.6)
    a.set_xlabel("B (T)")
    a.set_ylabel("R_xx (Ohm)")
    a.set_title(f"run {rid} — {label}")

fig.tight_layout()
fig.savefig("hera_scratch/sdh_spots.png", dpi=110)
print("saved hera_scratch/sdh_spots.png")
