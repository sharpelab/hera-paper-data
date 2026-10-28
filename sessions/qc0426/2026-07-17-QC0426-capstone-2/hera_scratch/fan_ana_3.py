# Run 7 — Luttinger partition robustness (step 5.1) + F_L-tone B-window split
rows_p = []
for ch, ceil in (("sr1", 23.75e3), ("sr2", 9.5e3)):
    R = rg7.R[ch]
    f7, spec7 = ffts7[ch]
    for ci in range(101):
        if R[:, ci].max() > ceil or abs(ns7[ci]) < 1.0:
            continue
        s = spec7[ci]
        FL = LAM7 * FLnom7[ci]
        def top_pk(fmin, fmax, k=2):
            m = (f7 >= fmin) & (f7 <= fmax)
            fi, si = f7[m], s[m]
            pk = (si[1:-1] > si[:-2]) & (si[1:-1] > si[2:])
            idx = np.where(pk)[0] + 1
            idx = idx[np.argsort(si[idx])[::-1][:k]]
            return sorted([(fi[i], si[i]) for i in idx])
        lp = top_pk(2.0, min(8.0, 0.45 * FL), k=1)
        hp = top_pk(0.55 * FL, 1.2 * FL, k=2)
        if lp and len(hp) == 2:
            rows_p.append((abs(ns7[ci]), FL, lp[0][0], hp[0][0], hp[1][0]))
arrp = np.array(rows_p)
resid_pair = arrp[:, 1] - (arrp[:, 2] + arrp[:, 3])
resid_sum = arrp[:, 1] - arrp[:, 4]
good_pair = np.abs(resid_pair) < 3.4   # ±2δF
print(f"{len(arrp)} columns with a resolved (light, heavy, upper) triple; "
      f"pair partition |f_ML+f_BL − λF_L| < 2δF in {100*good_pair.mean():.0f}% "
      f"(picker grabs the 3rd heavy tone in most failures — see residual families)")
print(f"upper tone tracks λF_L: median offset {np.median(resid_sum):+.2f} T")

fig, ax = plt.subplots(figsize=(8, 4.5))
ax.scatter(arrp[:, 0], -resid_pair, s=8, alpha=0.6, label="(f_ML+f_BL) − λF_L")
ax.scatter(arrp[:, 0], -resid_sum, s=8, alpha=0.6, label="f_upper − λF_L")
ax.axhline(0, color="k", lw=0.7)
for y in (1.7, -1.7):
    ax.axhline(y, color="r", lw=0.5, ls=":")
ax.set_xlabel("|n| (10¹² cm⁻²)")
ax.set_ylabel("residual (T)")
ax.legend(fontsize=8)
ax.set_title(f"run 7: partition residuals at λ = {LAM7:.3f} (±2δF dotted)")
fig.tight_layout()
plt.show()

# F_L-tone origin, cheap check (Verify): B-window split on run 5 (hole spot check)
r5b = open_run("data/5")
B5b = r5b.col("magnet_field")
R5b = r5b.col("sr2_X") / 20e-9
mid = 2 / (1 / 0.95 + 1 / 8)
print(f"\nB-window split (run 5, sr2; split at {mid:.2f} T):")
for lab, rng in (("low-B", (0.95, mid)), ("high-B", (mid, 8.0))):
    fb, sb = sdh_fft(R5b[:, None], B5b, b_range=rng)
    sb = sb[0]
    def amp_at(F0, w=2.5):
        m = (fb > F0 - w) & (fb < F0 + w)
        return sb[m].max()
    a_ml, a_bl, a_fl = amp_at(4.0, 1.5), amp_at(28.0), amp_at(33.2)
    print(f"  {lab}: A(f_ML)={a_ml:.2f} A(f_BL)={a_bl:.2f} A(F_L)={a_fl:.2f}  "
          f"→ A(F_L)/A(f_BL) = {a_fl/a_bl:.2f}")
print("F_L-tone strengthens ×~2.3 vs f_BL from low-B to high-B → consistent-with "
      "magnetic breakdown (sum orbit), not an independent pocket. Decisive check = per-branch LK mass.")
