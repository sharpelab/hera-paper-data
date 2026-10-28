# Run 7: raw MR + FFT stability + peaks vs F_L (electron side)
r7 = run(7)
B7 = r7.col_at(1)
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for ch, col in (("sr1", "C0"), ("sr2", "C1")):
    R = r7.col(f"{ch}_X") / 20e-9
    axes[0].plot(B7, R, lw=0.7, color=col, label=ch)
    off = 0 if ch == "sr1" else 1.1
    for deg, ls in ((3, ":"), (5, "-"), (7, "--")):
        for cut, alpha in ((1.5, 1.0), (1.9, 0.5)):
            f_, s_ = sdh_fft(R[:, None], B7, b_range=(cut, 8.0), bg_degree=deg)
            axes[1].plot(f_, s_[0] / s_[0].max() + off, ls, lw=0.8, alpha=alpha, color=col)
axes[0].set_xlabel("B (T)"); axes[0].set_ylabel("R (Ω)"); axes[0].legend()
axes[0].set_title("raw MR (sr3 Hall +755 Ω @ 7.9 T → n ≈ +6.6e12)")
for F in (9.8, 55.0, 64.8):
    axes[1].axvline(F, color="k", lw=0.5, ls=":")
axes[1].axvline(62.0, color="k", lw=0.8, ls="--")
axes[1].set_xlim(0, 110); axes[1].set_xlabel("F (T)")
axes[1].set_title("FFT stability — pair {9.3–10.2, 54.6–55.5} + 64.8 = sum")
fig.suptitle("Run 7 — electron-side SdH")
fig.tight_layout()
