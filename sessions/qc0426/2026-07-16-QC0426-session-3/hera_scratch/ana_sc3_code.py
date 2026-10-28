# Run 10: raw + FFT stability + model comparison at the in-clamp point
r10 = run(10)
B10 = r10.col_at(1)
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for ch, col in (("sr1", "C0"), ("sr2", "C1")):
    R = r10.col(f"{ch}_X") / 20e-9
    axes[0].plot(B10, R, lw=0.7, color=col, label=ch)
    off = 0 if ch == "sr1" else 1.1
    for cut, alpha in ((1.5, 1.0), (1.8, 0.7), (2.2, 0.4)):
        f_, s_ = sdh_fft(R[:, None], B10, b_range=(cut, 8.0), bg_degree=5)
        axes[1].plot(f_, s_[0] / s_[0].max() + off, lw=0.8, alpha=alpha, color=col)
axes[0].set_xlabel("B (T)"); axes[0].set_ylabel("R (Ω)"); axes[0].legend()
axes[0].set_title("raw MR (descending sweep)")
# model predictions at lambda-rescaled density (fs_count_b0, electron side)
for F, lbl, c in ((1.70, "ABA ML (model)", "c"), (30.81, "ABA BL (model)", "r"), (32.51, "ABC single / F_L", "g")):
    axes[1].axvline(F, color=c, lw=1, ls="--")
axes[1].set_xlim(0, 80); axes[1].set_xlabel("F (T)")
axes[1].set_title("FFT (cuts 1.5/1.8/2.2, deg 5) vs model at n·λ = 3.14e12")
axes[1].legend(["sr1", "sr2"], fontsize=7)
fig.suptitle("Run 10 — electron n = +3.0e12")
fig.tight_layout()
print("stable tones: 33.3 T (both ch, = λ·F_L); ~24.5 T (both ch, slides ~1.5 T with cut);")
print("low-F band 6–14 T unstable across extraction — f_ML(model 1.7 T / fraction-scaled ~5 T) unresolvable (δF ≈ 1.9–2.8 T)")
