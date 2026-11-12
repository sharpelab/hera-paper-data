# Runs 6 & 7 — SdH content: Rxx(B), FFT in 1/B (B in [1.5, 10] T), per-tone onsets.
from hera.analysis import resolve_channels, current_channel, sdh_onset, SdhOnsetError
from scipy.signal import find_peaks

H_OVER_E = cst.h / cst.e

def rxx_vs_B(i):
    g = run(i)
    ch = resolve_channels(g.meta)
    cur = current_channel(ch)
    I = g.col(cur.col) / cur.gain
    v = [c for c in ch if c.cid == "sr1"][0]
    R = (g.col(v.col) / v.gain) / I
    B = g.col("magnet_field")
    o = np.argsort(B)
    return B[o], R[o], np.median(np.abs(I))

fig, axs = plt.subplots(2, 2, figsize=(13, 8))
for row, (i, n12, tag) in enumerate([(6, +3.2, "electron"), (7, -1.2, "hole")]):
    B, R, Imed = rxx_vs_B(i)
    F_full = H_OVER_E * abs(n12) * 1e16 / 4  # single 4-fold FS carrying all of n
    ax = axs[row, 0]
    ax.plot(B, R, lw=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ω)")
    ax.set_title(f"run {i} — {tag}, n = {n12:+.1f}e12, D = 0 (I ≈ {Imed*1e9:.2f} nA)")
    freqs, spec = sdh_fft(R[:, None], B, b_range=(1.5, 10.0), nfft=4096, bg_degree=5, log=False)
    sp = spec[0]
    ax2 = axs[row, 1]
    ax2.plot(freqs, sp / sp.max(), lw=0.8)
    ax2.axvline(F_full, color="tab:red", ls="--", lw=1, label=f"F_full(deg 4) = {F_full:.1f} T")
    ax2.set_xlim(0, 80); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT mag (norm)"); ax2.legend()
    ax2.set_title(f"run {i} SdH FFT in 1/B, B ∈ [1.5, 10] T")
    pk, _ = find_peaks(sp, height=0.05 * sp.max(), distance=5)
    top = sorted(zip(freqs[pk], sp[pk]), key=lambda t: -t[1])[:6]
    print(f"run {i} FFT peaks (F, rel amp): " + ", ".join(f"({f:.1f} T, {a/sp.max():.2f})" for f, a in top))
    try:
        so = sdh_onset(R, B, b_lo=0.3, r_full_scale=50e-6 / Imed)
        print(so.summary())
    except SdhOnsetError as e:
        print(f"run {i} sdh_onset: {e}")
    print()
fig.tight_layout()
