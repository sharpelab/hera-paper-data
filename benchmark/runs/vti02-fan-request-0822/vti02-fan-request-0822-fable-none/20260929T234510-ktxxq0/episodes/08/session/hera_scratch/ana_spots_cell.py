# SdH spot checks, runs 6 (e: n=+3.2e12) & 7 (h: n=-1.2e12), D = 0 — raw + onset tones + FFT
from hera.analysis import resolve_channels, sdh_fft, sdh_onset, luttinger_frequency, SdhOnsetError
from scipy.signal import find_peaks

fig, ax = plt.subplots(2, 3, figsize=(15, 8))
for i, (rid, label, n_SI) in enumerate([(6, "electron n=+3.2e12", +3.2e16), (7, "hole n=-1.2e12", -1.2e16)]):
    r = open_run(f"data/{rid}")
    chans = {c.cid: c for c in resolve_channels(r.meta)}
    I = np.abs(r.col("sr0_X") / chans["sr0"].gain)
    R = (r.col("sr1_X") / chans["sr1"].gain) / I
    B = r.col("magnet_field")
    o = np.argsort(B); Bs, Rs = B[o], R[o]
    m = Bs > 0.25; Bs, Rs = Bs[m], Rs[m]
    fs_R = float(r.meta["measurement_config"].get("sr1_sensitivity", 50e-6)) / np.median(I)
    F_L = luttinger_frequency(np.array([n_SI]))[0]

    ax[i, 0].plot(Bs, Rs, lw=0.6)
    ax[i, 0].set(xlabel="B (T)", ylabel="R_xx (Ω)", title=f"run {rid} — {label} (raw)")

    print(f"=== run {rid} ({label}): F_L = {F_L:.1f} T, R fs {fs_R:.0f} Ω ===")
    try:
        print(sdh_onset(Rs, Bs, r_full_scale=fs_R).summary())
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)

    for j, blo in enumerate([1.5, 3.0]):
        freqs, spec = sdh_fft(Rs[:, None], Bs, b_range=(blo, Bs.max()), nfft=4096)
        sp = spec[0]
        a = ax[i, 1 + j]
        a.plot(freqs, sp / sp.max())
        a.axvline(F_L, color="r", ls="--", lw=1, label=f"F_L = {F_L:.1f} T")
        a.set(xlim=(0, 60), xlabel="F (T)", title=f"run {rid} FFT in 1/B, B > {blo} T")
        a.legend(fontsize=8)
        pk, _ = find_peaks(sp, height=sp.max() * 0.05, distance=8)
        top = sorted(zip(sp[pk], freqs[pk]))[::-1][:6]
        print(f"  FFT peaks (B>{blo} T): " + ", ".join(f"{f:.1f} T" for _, f in top if f > 1))
fig.tight_layout()
plt.show()
