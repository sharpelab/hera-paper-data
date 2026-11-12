"""SdH content of runs 6-7: per-tone low-B onsets (sdh_onset) + FFT in 1/B above 1 T.
Discriminator: tone count and frequency partition vs the full-density 4-fold Onsager
frequency F_full = |n| h / 4e (33.1 T at +3.2e12; 12.4 T at -1.2e12)."""
from hera.analysis import sdh_onset, SdhOnsetError
from scipy.signal import find_peaks

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, (rid, n12) in zip(ax, ((6, +3.2), (7, -1.2))):
    B, R = spot_trace(rid)
    F_full = luttinger_frequency(abs(n12) * 1e16)
    print(f"===== run {rid}: n = {n12:+.1f}e12 -> F_full(4-fold) = {F_full:.1f} T =====")
    try:
        so = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
        print(so.summary())
    except SdhOnsetError as e:
        print(f"sdh_onset failed: {e}")
    freqs, spec = sdh_fft(R[:, None], B, b_range=(1.0, B.max()), nfft=4096, log=False)
    sp = spec[0]
    sel = freqs > 2
    pk, _ = find_peaks(sp[sel], prominence=0.05 * sp[sel].max())
    pkf = sorted(((freqs[sel][p], sp[sel][p]) for p in pk), key=lambda t: -t[1])[:5]
    print("FFT peaks (T): " + ", ".join(f"{f:.1f}" for f, _ in pkf) + "\n")
    a.plot(freqs, sp, lw=0.8)
    a.axvline(F_full, color="r", ls="--", label=f"F_full = {F_full:.1f} T")
    for f, amp in pkf[:4]:
        a.annotate(f"{f:.1f}", (f, amp), fontsize=8)
    a.set(xlabel="F (T)", xlim=(0, 60), ylabel="FFT amp", title=f"run {rid}: FFT in 1/B, B > 1 T")
    a.legend(fontsize=8)
fig.tight_layout()
plt.show()
