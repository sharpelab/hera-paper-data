# Runs 6-7 tone read: per-trace SdH onset (matched-filter) + FFT in 1/B, vs the
# full-density 4-fold Onsager frequency F_full = |n| h / 4e.
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, (rid, n12) in zip(ax, [(6, +3.2), (7, -1.2)]):
    B, R, I = spots[rid]
    m = B > 0.25
    Bs, Rs = B[m], R[m]
    try:
        on = sdh_onset(Rs, Bs, r_full_scale=50e-6 / np.median(np.abs(I)))
        print(f"=== run {rid} ===\n{on.summary()}")
    except SdhOnsetError as e:
        print(f"run {rid}: SdhOnsetError: {e}")
    F_full = luttinger_frequency(abs(n12) * 1e16)
    for brange, c in [((2.0, 10.0), "C0"), ((4.0, 10.0), "C1")]:
        f, spec = sdh_fft(Rs[:, None], Bs, b_range=brange)
        a.plot(f, spec[0] / spec[0].max(), lw=0.8, color=c, label=f"FFT {brange[0]:.0f}–10 T")
    a.axvline(F_full, color="k", ls="--", lw=0.8, label=f"F_full(4-fold) = {F_full:.1f} T")
    a.set_xlim(0, 120); a.set_xlabel("F (T)"); a.set_ylabel("FFT mag (norm)")
    a.set_title(f"run {rid}: n = {n12:+.1f}e12"); a.legend(fontsize=8)
    print(f"run {rid}: F_full(4-fold, |n|={abs(n12)}e12) = {F_full:.1f} T\n")
plt.tight_layout(); plt.show()
