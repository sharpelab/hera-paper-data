# Run 6: raw MR, FFT (stability sweep), bg-subtracted 1/B trace, B-window split
r6 = run(6)
B6 = r6.col_at(1)
FL_NOM = 62.0
fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for ch, col in (("sr1", "C0"), ("sr2", "C1")):
    R = r6.col(f"{ch}_X") / 20e-9
    axes[0, 0].plot(B6, R, lw=0.7, color=col, label=ch)
    off = 0 if ch == "sr1" else 1.1
    for deg, ls in ((3, ":"), (5, "-"), (7, "--")):
        for cut, alpha in ((1.8, 1.0), (2.3, 0.5)):
            f_, s_ = sdh_fft(R[:, None], B6, b_range=(cut, 8.0), bg_degree=deg)
            axes[0, 1].plot(f_, s_[0] / s_[0].max() + off, ls, lw=0.8, alpha=alpha, color=col)
    msk = B6 >= 1.8
    dR = R[msk] - np.polyval(np.polyfit(B6[msk], R[msk], 5), B6[msk])
    axes[1, 0].plot(1 / B6[msk], dR + (0 if ch == "sr1" else 120), lw=0.6, color=col)
axes[0, 0].set_xlabel("B (T)"); axes[0, 0].set_ylabel("R (Ω)"); axes[0, 0].legend()
axes[0, 0].set_title("raw MR (Hall n from sr3: 6.1–6.6e12)")
for F, lbl in ((11.1, "f_ML 11.1"), (55.3, "f_BL 55.3"), (66.3, "sum 66.3"), (FL_NOM, "F_L nom 62")):
    axes[0, 1].axvline(F, color="k", lw=0.5, ls=":" if F != FL_NOM else "--")
axes[0, 1].set_xlim(0, 110); axes[0, 1].set_xlabel("F (T)")
axes[0, 1].set_title("FFT, deg 3/5/7 × cut 1.8/2.3 T (stability sweep)")
axes[1, 0].set_xlabel("1/B (1/T)"); axes[1, 0].set_ylabel("ΔR (Ω, offset)")
axes[1, 0].set_title("bg-subtracted — non-sinusoidal at high B → harmonic comb")
# B-window split (F_L-tone origin, investigation Verify)
ax = axes[1, 1]
R = r6.col("sr1_X") / 20e-9
for rng, col2 in (((1.8, 4.0), "C2"), ((4.0, 8.0), "C3")):
    f_, s_ = sdh_fft(R[:, None], B6, b_range=rng, bg_degree=5)
    ax.plot(f_, s_[0] / s_[0].max(), color=col2, lw=1, label=f"sr1 {rng[0]}–{rng[1]} T")
    for F in (11.1, 55.3, 66.3):
        j = int(np.argmin(np.abs(f_ - F)))
        print(f"B {rng}: A({F})={s_[0][max(0,j-1):j+2].max():.3g}")
ax.axvline(66.3, color="k", lw=0.5, ls=":")
ax.set_xlim(0, 110); ax.set_xlabel("F (T)"); ax.legend(fontsize=7)
ax.set_title("B-window split: 66.3 strengthens with B → breakdown/mixing")
fig.suptitle("Run 6 — hole-side SdH: {11.1, 55.3} pair + 66.3 ≈ sum")
fig.tight_layout()
