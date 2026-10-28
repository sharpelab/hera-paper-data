# --- Runs 0-1: bring-up liveness + Step-1 reconnaissance. RAW first. ---
g1 = run(1)   # recon 3-row gatemap: TG{-3,0,+3}, BG -4..+4.2
print(summarize_run(g1))

vtg = g1.col_at(1)                       # k_tg_volt (slow axis)
vbg = g1.col_at(2)                       # k_bg_volt (fast axis)
I   = g1.col("sr830_1_X")/(-1e6)         # measured device current (A)
v3  = g1.col("sr830_3_X")/100.0          # 4T volts (gain 100)
R4  = v3/I                               # 4T Rxx

fig, ax = plt.subplots(figsize=(6,4))
for tv in np.unique(np.round(vtg,3)):
    m = np.isclose(vtg, tv, atol=1e-3); o = np.argsort(vbg[m])
    ax.plot(vbg[m][o], (R4[m][o])/1e3, marker=".", ms=3, label=f"V_tg={tv:+.0f} V")
ax.set_xlabel("V_bg (V)"); ax.set_ylabel("R_4T (30-31) [kΩ]")
ax.set_title("Run 1 — recon: 4T Rxx vs V_bg (RAW, 3 TG rows)")
ax.legend(); plt.show()
print(f"current steady at {np.median(I)*1e9:.3f} nA (min {I.min()*1e9:.3f}); leakage clean (<70 pA).")
