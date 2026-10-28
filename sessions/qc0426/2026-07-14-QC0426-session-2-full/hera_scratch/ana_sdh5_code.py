# Run 5 — raw record, Hall density pin, SdH FFT stability sweep
from scipy.signal import find_peaks

r5 = run(5)
B5 = r5.col("magnet_field")
I5 = 20e-9
R5 = {ch: r5.col_at(r5.col_indices(f"{ch}_X")[-1]) / I5 for ch in ("sr1", "sr2", "sr3")}

# Hall density pin (independent of lever arm): n = B / (e * R_xy), low-B slope
m_hall = (B5 > 0.4) & (B5 < 1.5)
p_hall = np.polyfit(B5[m_hall], -R5["sr3"][m_hall], 1)
n_hall = 1 / (cst.e * p_hall[0])
F_L_true = (cst.h / (4 * cst.e)) * n_hall
print(f"Hall slope {p_hall[0]:.1f} Ohm/T -> |n| = {n_hall*1e-16:.2f} e12 cm^-2 "
      f"(target 6.00; geometry scale ~{(n_hall/6e16-1)*100:+.0f}%)")
print(f"F_L(true n) = {F_L_true:.1f} T   [F_L(design n) = 62.0 T]")

fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
axes[0].plot(B5, R5["sr1"], lw=0.6, label="sr1")
axes[0].plot(B5, R5["sr2"], lw=0.6, label="sr2")
axes[0].plot(B5, -R5["sr3"], lw=0.6, label="-sr3 (Rxy)")
axes[0].set_xlabel("B (T)"); axes[0].legend(); axes[0].set_title("raw R(B)")

m = B5 > 3.5
p = np.polyfit(B5[m], R5["sr1"][m], 4)
axes[1].plot(1/B5[m], R5["sr1"][m] - np.polyval(p, B5[m]), lw=0.8)
axes[1].set_xlabel("1/B (1/T)"); axes[1].set_title("sr1 detrended, B>3.5 T (onset ~3.5 T)")

for ch, color in (("sr1", "C0"), ("sr2", "C1")):
    for (blo, deg), ls in zip(((3.0, 5), (3.5, 4), (4.0, 3), (4.5, 3)),
                              ("-", "--", "-.", ":")):
        fr, spec = sdh_fft(R5[ch][:, None], B5, b_range=(blo, 8.0), bg_degree=deg, log=False)
        mag = spec[0]
        axes[2].plot(fr, mag / mag.max(), color=color, ls=ls, lw=0.8, alpha=0.8)
        if ch == "sr1":
            pk, _ = find_peaks(mag, height=mag.max() * 0.1, distance=4)
            print(f"sr1 FFT [{blo},8] deg{deg}: peaks", [f"{fr[p]:.1f} T ({mag[p]/mag.max():.2f})" for p in pk])
axes[2].axvline(F_L_true, color="k", ls="--", lw=1, label=f"F_L(true) {F_L_true:.0f} T")
axes[2].set_xlim(0, 120); axes[2].set_xlabel("F (T)")
axes[2].set_title("FFT stability sweep (sr1 blue / sr2 orange)"); axes[2].legend(fontsize=8)
fig.suptitle("run 5 - hole-side SdH spot check")
fig.tight_layout()
