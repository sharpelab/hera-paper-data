# Run 6 — raw, Hall pin, computed onset, FFT stability sweep
from scipy.signal import find_peaks
from hera.analysis import sdh_onset

r6 = run(6)
B6 = r6.col("magnet_field")
I6 = 20e-9
R6 = {ch: r6.col_at(r6.col_indices(f"{ch}_X")[-1]) / I6 for ch in ("sr1", "sr2", "sr3")}

m_hall = (B6 > 0.4) & (B6 < 1.5)
p_hall = np.polyfit(B6[m_hall], R6["sr3"][m_hall], 1)
n_hall = 1 / (cst.e * p_hall[0])
F_L6 = (cst.h / (4 * cst.e)) * n_hall
print(f"Hall: n = {n_hall*1e-16:+.2f} e12 cm^-2 -> F_L(true) = {F_L6:.1f} T")

o2 = sdh_onset(R6["sr2"], B6, win_invB=0.10)
print(f"sr2 computed onset: {o2.onset_b:.2f} T (consensus tone {o2.consensus_freq:.1f} T)")
print("sr1 onset: nan (multi-tone content defeats the consensus tracker; sr2 carries the number)")

fig, axes = plt.subplots(1, 3, figsize=(17, 4.6))
axes[0].plot(B6, R6["sr1"], lw=0.6, label="sr1")
axes[0].plot(B6, R6["sr2"], lw=0.6, label="sr2")
axes[0].plot(B6, R6["sr3"], lw=0.6, label="sr3 (Rxy)")
axes[0].axvline(o2.onset_b, color="r", ls="--", lw=0.8, label=f"onset {o2.onset_b:.2f} T")
axes[0].legend(); axes[0].set_xlabel("B (T)"); axes[0].set_title("raw R(B), electron side")
m = B6 > 3.5
p = np.polyfit(B6[m], R6["sr1"][m], 4)
axes[1].plot(1/B6[m], R6["sr1"][m] - np.polyval(p, B6[m]), lw=0.8)
axes[1].set_xlabel("1/B (1/T)"); axes[1].set_title("sr1 detrended, B>3.5 T")
for ch, color in (("sr1", "C0"), ("sr2", "C1")):
    for (blo, deg), ls in zip(((3.0, 5), (3.5, 4), (4.0, 3), (4.5, 3)), ("-", "--", "-.", ":")):
        fr, spec = sdh_fft(R6[ch][:, None], B6, b_range=(blo, 8.0), bg_degree=deg, log=False)
        mag = spec[0]
        axes[2].plot(fr, mag / mag.max(), color=color, ls=ls, lw=0.8, alpha=0.8)
        pk, _ = find_peaks(mag, height=mag.max() * 0.1, distance=4)
        print(f"{ch} [{blo},8] deg{deg}:", [f"{fr[p]:.1f}({mag[p]/mag.max():.2f})" for p in pk])
axes[2].axvline(F_L6, color="k", ls="--", lw=1, label=f"F_L {F_L6:.0f} T")
axes[2].set_xlim(0, 120); axes[2].set_xlabel("F (T)"); axes[2].legend(fontsize=8)
axes[2].set_title("FFT stability (sr1 blue / sr2 orange)")
fig.suptitle("run 6 - electron-side SdH spot check")
fig.tight_layout()
