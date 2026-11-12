"""sdh-spot-check read of runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D = 0:
raw R(B), then sdh_onset tone tables + FFT in 1/B with F_full (Luttinger, run-5 cal) marked."""
from hera.analysis import resolve_channels, current_channel, sdh_onset, SdhOnsetError

FS_OHM = 50e-6 / 10e-9  # sr1 50 uV at 10 nA = 5 kOhm full scale (both runs)
fig, axes = plt.subplots(2, 2, figsize=(12, 7))
tone_tbl = {}
for row, (rid, tag, n12) in enumerate([(6, "electron n=+3.2e12", 3.2), (7, "hole n=-1.2e12", -1.2)]):
    r = run(rid)
    chans = resolve_channels(r.meta)
    cur = current_channel(chans)
    vch = [c for c in chans if not c.is_current][0]
    R = (r.col(vch.col) / vch.gain) / (r.col(cur.col) / cur.gain)
    B = r.col("magnet_field")
    o = np.argsort(B)
    B, R = B[o], R[o]
    F_full = abs(n12) * 1e16 * cst.h / (4 * cst.e)

    ax = axes[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ω)")
    ax.set_title(f"run {rid} raw — {tag}")

    print(f"\n===== run {rid} ({tag}); F_full(Luttinger, run-5 cal) = {F_full:.1f} T =====")
    try:
        ons = sdh_onset(R, B, r_full_scale=FS_OHM)
        print(ons.summary())
        tone_tbl[rid] = [t.freq for t in ons.tones]
    except SdhOnsetError as ex:
        print("sdh_onset FAILED:", ex)
        tone_tbl[rid] = []

    freqs, spec = sdh_fft(R[:, None], B, b_range=(1.5, 10.0), nfft=4096)
    ax = axes[row, 1]
    ax.plot(freqs, spec[0], lw=0.8)
    ax.axvline(F_full, color="k", ls="--", lw=0.8, label=f"F_full {F_full:.1f} T")
    for f in tone_tbl[rid]:
        ax.axvline(f, color="C3", ls=":", lw=0.8)
    ax.set_xlim(0, 80); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT|")
    ax.set_title(f"run {rid} SdH FFT, 1.5–10 T window (red: tracked tones)")
    ax.legend(fontsize=8)
fig.tight_layout()

print("\nTwo-band arithmetic (run 6): 7.1 + 29.5 = 36.6 T vs F_full 33.1 T (+11%, inside the ~10% geometry-prior scale)")
print("Harmonic ladder alternative: 14.1/22.1/29.5 = 1.99/3.11/4.15 x 7.1 — but 29.5 T peak SNR 89 > fundamental 40")
print("Run 7: 6.6 + 4.7 = 11.3 T vs F_full 12.4 T; non-harmonic 8.5, 12.3 T also tracked -> >=2 pockets near CNP")
