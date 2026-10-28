from hera.analysis import resolve_channels, current_channel
g6 = run(6)
ch6 = resolve_channels(g6.meta)
I6 = g6.col(current_channel(ch6).col) / current_channel(ch6).gain
v6 = next(c for c in ch6 if c.cid == 'sr1')
R6 = (g6.col(v6.col) / v6.gain) / I6
B6 = g6.col('magnet_field')
fig, ax = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
ax[0].plot(B6, R6, lw=.8); ax[0].set_ylabel('raw Rxx (ohm)')
ax[1].plot(B6, I6*1e9, lw=.8); ax[1].set(ylabel='drain I (nA)', xlabel='B (T)')
fig.suptitle('data/6: n=+3.2e12 cm^-2, D=0; raw')
fig.tight_layout(); plt.show()
print(summarize_run(g6))
print(f'Rxx {R6.min():.1f}..{R6.max():.1f} ohm; drain I {I6.min()*1e9:.2f}..{I6.max()*1e9:.2f} nA; T {g6.col("T_sample").min():.3f}..{g6.col("T_sample").max():.3f} K')
