# Runs 6-7 — SdH spot checks (`sdh-spot-check`), D = 0: electron n=+3.2e12 (run 6, B 0->10 T), hole n=-1.2e12 (run 7, B 10->0.3 T)
from hera.analysis import sdh_onset, SdhOnsetError

SENS, BIAS_R, SR1_GAIN = 50e-6, 100e6, 1.0   # both runs: sr1 50 uV, 1 V drive / 100 MOhm -> 10 nA
FL_E, FL_H = 33.1, 12.4                      # Luttinger F_L = (h/4e)n at the two spots (run-5 cal)
# model (fs_count_b0, run in scratch): ABAB @ +3.2e12: 7.4/25.9 T (0.22/0.78 FL); ABCA: 33.1 T singleton
# ABAB @ -1.2e12: 5.9/6.5 T (near-CNP balanced pair); ABCA: 12.4 T (m* 1.1 -> LK-dead at T_e ~ 8 K)
MODEL = {6: dict(FL=FL_E, abab=(7.4, 25.9), abca=33.1), 7: dict(FL=FL_H, abab=(5.9, 6.5), abca=12.4)}

fig, axes = plt.subplots(2, 3, figsize=(15, 7.5))
onsets = {}
for row, (rid, lab) in enumerate([(6, "run 6 — electron n=+3.2e12"), (7, "run 7 — hole n=-1.2e12")]):
    r = run(rid)
    B, Rr = r.col("magnet_field"), (r.col("sr1_X") / SR1_GAIN) / (1.0 / BIAS_R)
    o = np.argsort(B); B, Rr = B[o], Rr[o]
    print(f"=== {lab}: R = {Rr[0]:.0f} Ohm at B_min, max {Rr.max():.0f} Ohm ({Rr.max()/(SENS/1e-8)*100:.0f}% of FS)")
    on = sdh_onset(Rr, B, r_full_scale=SENS / 1e-8)
    print(on.summary()); onsets[rid] = on

    ax = axes[row, 0]                                    # raw FIRST
    ax.plot(B, Rr, lw=0.5); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(lab + " — raw")

    msk = B > 0.5                                        # bg-subtracted
    dR = Rr[msk] - np.polyval(np.polyfit(B[msk], Rr[msk], 5), B[msk])
    ax = axes[row, 1]
    ax.plot(B[msk], dR, lw=0.5); ax.axvline(on.onset_b, color="r", ls="--", label=f"onset(track) {on.onset_b:.2f} T")
    ax.set_xlabel("B (T)"); ax.set_ylabel("dRxx (Ohm)"); ax.set_title("bg-subtracted (deg-5 in B)"); ax.legend(fontsize=8)

    ax = axes[row, 2]                                    # 1/B FFT above 1 T (grid Nyquist-clean band)
    for cut, deg, st in [(1.0, 5, "-"), (1.5, 5, "--"), (1.0, 7, ":")]:
        f, s = sdh_fft(Rr[:, None], B, b_range=(cut, B.max()), bg_degree=deg, log=False, nfft=4096)
        band = f >= 2.5
        ax.plot(f[band], s[0][band] / s[0][band].max(), st, lw=1, label=f"cut {cut} T, deg {deg}")
    m = MODEL[rid]
    ax.axvline(m["FL"], color="k", alpha=0.5, label=f"F_L {m['FL']} T (=ABCA)")
    for fm in m["abab"]:
        ax.axvline(fm, color="tab:green", alpha=0.5, ls="--")
    ax.plot([], [], color="tab:green", ls="--", label=f"ABAB model {m['abab']} T")
    ax.set_xlim(0, m["FL"] * 1.5); ax.set_xlabel("F (T)"); ax.set_ylabel("norm. amp (f>2.5 T)")
    ax.set_title("FFT in 1/B"); ax.legend(fontsize=7)
fig.tight_layout(); plt.show()
