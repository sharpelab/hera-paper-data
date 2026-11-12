# Run 9 — electron spot check read + cross-side comparison + D=0 locator
from hera.analysis import sdh_onset
g = run(9)
print(summarize_run(g))
plot_raw(g)
B = g.col("magnet_field")
i_dr = np.abs(g.col("sr0_X")) / 1e6
for ch, fs in (("sr1", 200e-6), ("sr3", 200e-6)):
    R = g.col(f"{ch}_X") / i_dr
    try:
        on = sdh_onset(R, B, r_full_scale=fs / 1e-9)
        print(f"--- {ch} ---"); print(on.summary())
    except Exception as e:
        print(f"--- {ch} --- {type(e).__name__}: {e}")

# cross-side FFT comparison (sr1), same window
fig, ax = plt.subplots(figsize=(7, 4.2))
for rid, lbl, c in ((8, "hole n=-1.8e12", "tab:red"), (9, "electron n=+1.7e12", "tab:blue")):
    gg = run(rid)
    Bx = gg.col("magnet_field"); ii = np.abs(gg.col("sr0_X")) / 1e6
    f, s = sdh_fft((gg.col("sr1_X") / ii)[:, None], Bx, b_range=(1.7, 9.0), bg_degree=5)
    ax.plot(f, s[0] / s[0].max(), color=c, lw=1, label=lbl)
ax.axvline(18.6, color="r", ls="--", lw=0.7); ax.axvline(17.6, color="b", ls="--", lw=0.7)
ax.set_xlim(0, 60); ax.set_xlabel("F (T)"); ax.legend(); ax.grid(alpha=0.3)
ax.set_title("sr1: hole vs electron spot check (F_L dashed)")
plt.show()

# D = 0 locator from run 7: R_CNP along the ridge vs nominal D
from scipy.ndimage import gaussian_filter1d
g7 = run(7); NF = 161
gr = lambda c: c[:len(c) // NF * NF].reshape(-1, NF)
VT, VB = gr(g7.col("k_2400_tg_volt")), gr(g7.col("k_2400_bg_volt"))
IDR = gr(np.abs(g7.col("sr0_X")) / 1e6)
fig, ax = plt.subplots(figsize=(6, 4))
for ch in ("sr1", "sr3"):
    R = gr(g7.col(f"{ch}_X")) / IDR
    pts = []
    for j in range(VT.shape[0]):
        sm = gaussian_filter1d(R[j], 3); k = int(np.argmax(sm))
        if 5 < k < NF - 6 and sm[k] > 2 * np.median(sm):
            Dn = cal.displacement_field(VT[j, k], VB[j, 0]) / 1e9
            pts.append((Dn, sm[k]))
    pts = np.array(pts)
    ax.plot(pts[:, 0], pts[:, 1] / 1e3, "o-", ms=3, label=ch)
    print(f"{ch}: R_CNP minimum at nominal D = {pts[np.argmin(pts[:,1]),0]:+.4f} V/nm")
ax.set_xlabel("nominal D (V/nm)"); ax.set_ylabel("R_CNP (kΩ)"); ax.legend(); ax.grid(alpha=0.3)
ax.set_title("run 7: CNP resistance vs D — symmetric minimum locates D = 0")
plt.show()
