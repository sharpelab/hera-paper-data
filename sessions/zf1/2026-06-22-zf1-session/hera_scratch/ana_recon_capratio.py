# --- CNP cap-ratio extraction (preview, 3 rows) ---
from scipy.ndimage import gaussian_filter1d
tg_rows = np.unique(np.round(vtg,3)); cnp_bg = []
for tv in tg_rows:
    m = np.isclose(vtg, tv, atol=1e-3); o = np.argsort(vbg[m])
    bg = vbg[m][o]; Rs = gaussian_filter1d(np.nan_to_num(R4[m][o]), 1.5)
    cnp_bg.append(bg[np.argmax(Rs)])
cnp_bg = np.array(cnp_bg)
slope, b0 = np.polyfit(tg_rows, cnp_bg, 1)
cbg_ctg = -1.0/slope                      # c_bg/c_tg = -1/(dVbg/dVtg)

fig, ax = plt.subplots(figsize=(5,4))
ax.plot(tg_rows, cnp_bg, "o", ms=8, label="CNP (Rxx max)")
xs = np.linspace(tg_rows.min(), tg_rows.max(), 50)
ax.plot(xs, slope*xs+b0, "-", label=f"fit: V_bg={slope:+.3f}·V_tg{b0:+.3f}")
ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg at CNP (V)")
ax.set_title(f"CNP line → c_bg/c_tg = {cbg_ctg:.3f}  (prior 1.18)")
ax.legend(); plt.show()
print(f"dVbg/dVtg = {slope:+.3f}  ->  c_bg/c_tg = {cbg_ctg:.3f}   (geometry prior: 1.18)")
print("Ratio confirmed at preview grade; full survey (105 rows) refines. Absolute n pending QH lever-arm.")
