from hera.analysis import resolve_channels
fig, ax = plt.subplots(2, 3, figsize=(13, 7))
for row, rid in enumerate((6, 7)):
    r = run(rid)
    channels = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / channels['sr0'].gain
    R = np.abs((r.col('sr1_X') / channels['sr1'].gain) / I)
    ax[row, 0].plot(B, R, lw=.8)
    ax[row, 1].plot(B, I * 1e9, lw=.8)
    ax[row, 2].plot(B, r.col('k_2400_tg_curr') * 1e12, lw=.8, label='TG')
    ax[row, 2].plot(B, r.col('k_2400_bg_curr') * 1e12, lw=.8, label='BG')
    ax[row, 0].set(ylabel='|Rxx| (Ω)', title=f'data/{rid}: raw Rxx')
    ax[row, 1].set(ylabel='drain current (nA)', title='measured current')
    ax[row, 2].set(ylabel='gate current (pA)', title='gate leakage')
    for a in ax[row]: a.set_xlabel('B (T)'); a.grid(alpha=.2)
    ax[row, 2].legend()
    print(f'data/{rid}: {r.rows} rows, interrupted={r.interrupted}; B {B[0]:.2f}→{B[-1]:.2f} T; '
          f'|Rxx| {R.min():.1f}–{R.max():.1f} Ω; I {I.min()*1e9:.3f}–{I.max()*1e9:.3f} nA; '
          f'T {r.col("T_sample").min():.3f}–{r.col("T_sample").max():.3f} K; '
          f'max |I_TG| {np.max(np.abs(r.col("k_2400_tg_curr")))*1e12:.0f} pA; '
          f'max |I_BG| {np.max(np.abs(r.col("k_2400_bg_curr")))*1e12:.0f} pA')
fig.tight_layout(); plt.show()
