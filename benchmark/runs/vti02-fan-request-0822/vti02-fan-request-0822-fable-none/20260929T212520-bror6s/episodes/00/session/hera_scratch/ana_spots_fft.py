# Runs 6-7: SdH tone content. Per-trace FFT in 1/B (B > 1 T) + sdh_onset
# tone tracking; red dashes = one-pocket full-density F_L = |n| h / 4e.
from hera.analysis import sdh_fft, sdh_onset

fig, ax = plt.subplots(1, 2, figsize=(12, 3.6))
for a, (rid, n12) in zip(ax, [(6, 3.2), (7, -1.2)]):
    B, R, Ib = spot_trace(rid)
    m = B > 1.0
    freqs, spec = sdh_fft(R[m][:, None], B[m], nfft=4096, log=False)
    a.plot(freqs, spec[0], lw=0.8)
    FL = luttinger_frequency(abs(n12) * 1e16)  # 1e12 cm^-2 -> m^-2
    a.axvline(FL, color="r", ls="--", lw=0.8, label=f"F_L = {FL:.1f} T (1 pocket, g=4)")
    a.set_xlim(0, 80); a.set_xlabel("F (T)"); a.set_ylabel("FFT mag")
    a.set_title(f"run {rid} FFT, B > 1 T (n = {n12:+.1f}e12)")
    a.legend(fontsize=8)
    o = sdh_onset(R[B > 0.29], B[B > 0.29], r_full_scale=50e-6 / Ib)
    print(f"=== run {rid}")
    print(o.summary())
fig.tight_layout()
