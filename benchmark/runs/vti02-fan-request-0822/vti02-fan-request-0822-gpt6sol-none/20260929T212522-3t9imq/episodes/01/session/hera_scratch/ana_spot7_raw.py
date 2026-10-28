g7 = run(7)
ch7 = resolve_channels(g7.meta)
I7 = g7.col(current_channel(ch7).col) / current_channel(ch7).gain
v7 = next(c for c in ch7 if c.cid == 'sr1')
R7 = (g7.col(v7.col) / v7.gain) / I7
B7 = g7.col('magnet_field')
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].plot(B7, R7, lw=.8); ax[0].set_ylabel('raw Rxx (ohm)')
ax[1].plot(B7, I7*1e9, lw=.8); ax[1].set(ylabel='drain I (nA)', xlabel='B (T)')
fig.suptitle('data/7: n=-1.2e12 cm^-2, D=0; raw')
fig.tight_layout(); plt.show()
print(summarize_run(g7))
print(f'Rxx {R7.min():.1f}..{R7.max():.1f} ohm; drain I {I7.min()*1e9:.2f}..{I7.max()*1e9:.2f} nA; T {g7.col("T_sample").min():.3f}..{g7.col("T_sample").max():.3f} K')
