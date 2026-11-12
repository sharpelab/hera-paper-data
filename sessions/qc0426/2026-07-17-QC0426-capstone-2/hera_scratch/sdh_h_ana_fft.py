# Run 5 — onset, 1/B FFT, peak table, harmonic screen, partition check
from hera.analysis import sdh_onset
F_L5 = luttinger_frequency(3.0e16)  # h*n/(4e), n in m^-2
print(f"F_L(3.0e12 cm^-2) = {F_L5:.2f} T")

def peaks_of(f, s, fmin=1.5, k=8):
    pk = (s[1:-1] > s[:-2]) & (s[1:-1] > s[2:])
    idx = np.where(pk)[0] + 1
    idx = idx[f[idx] > fmin]
    idx = idx[np.argsort(s[idx])[::-1][:k]]
    out = []
    for i in sorted(idx):
        # quadratic interpolation for sub-bin frequency
        a, b, c = s[i - 1], s[i], s[i + 1]
        df = 0.5 * (a - c) / (a - 2 * b + c)
        out.append((f[i] + df * (f[1] - f[0]), b))
    return out

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
peak_tables = {}
for ax, ch in zip(axes, ("sr1_X", "sr2_X")):
    on = sdh_onset(R5[ch], B5)
    # sr1 soft-clips above ~7.5 T (topped 2.73 kΩ on nominal 2.5 kΩ) — cap its window
    bmax = 7.4 if ch == "sr1_X" else 8.0
    print(f"{ch}: onset_b = {on.onset_b:.2f} T; FFT window [{1.3*on.onset_b:.2f}, {bmax}] T")
    for mult, style in ((1.15, "-"), (1.3, "--"), (1.5, ":")):
        f, spec = sdh_fft(R5[ch][:, None], B5, b_range=(mult * on.onset_b, bmax))
        ax.plot(f, spec[0], style, lw=0.9, label=f"cutoff {mult:.2f}×onset")
    peak_tables[ch] = peaks_of(f, spec[0])
    ax.axvline(F_L5, color="r", lw=0.8)
    ax.text(F_L5, ax.get_ylim()[1] * 0.93, " F_L", color="r", fontsize=8)
    ax.set_xlim(0, 60)
    ax.set_xlabel("F (T)")
    ax.set_title(ch)
    ax.legend(fontsize=7)
fig.suptitle("run 5: 1/B FFT (log amp), cutoff-stability overlay")
fig.tight_layout()
plt.show()

# δF and the harmonic screen against the strongest fundamental
dF = 1 / (1 / 0.77 - 1 / 8.0)
print(f"δF = 1/(1/B_onset - 1/B_max) = {dF:.2f} T (trust splits > ~{2*dF:.1f} T)")
for ch, tbl in peak_tables.items():
    f0 = tbl[np.argmax([a for _, a in tbl])][0] if tbl else np.nan
    f0 = min(tbl, key=lambda t: -t[1])[0]
    print(f"\n{ch} peaks (F [T], log-amp) — strongest fundamental f0 = {f0:.2f} T:")
    for fp_, amp in tbl:
        kh = fp_ / f0
        tag = f"~{round(kh)}×f0 (Δ={abs(fp_-round(kh)*f0):.2f} T)" if abs(kh - round(kh)) < 0.25 else "NOT a f0 multiple"
        print(f"  F={fp_:6.2f}  amp={amp:5.2f}  {tag}")
    print(f"  partition check: f0 + (F_L - f0) -> BL partner predicted at {F_L5 - f0:.2f} T")
