from hera.analysis import sdh_onset
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for row, rid in enumerate((6, 7)):
    r = run(rid)
    B = r.col('magnet_field')
    I = r.col('sr0_X') / r.meta['measurement_config']['sr0_gain']
    R = np.abs(r.col('sr1_X') / I)
    ax[row, 0].plot(B, R, '.', ms=1.3)
    ax[row, 0].set(xlabel='B (T)', ylabel='|Rxx| (Ohm)', title=f'data/{rid}: raw resistance')
    ax[row, 1].plot(B, I * 1e9, '.', ms=1.3, label='drain current')
    ax[row, 1].set(xlabel='B (T)', ylabel='I (nA)', title=f'data/{rid}: raw current')
    print(f'data/{rid}: {r.rows} rows, R={R.min():.1f}–{R.max():.1f} Ω, I={I.min()*1e9:.2f}–{I.max()*1e9:.2f} nA, T={r.col("T_sample").min():.3f}–{r.col("T_sample").max():.3f} K')
fig.tight_layout(); plt.show()
