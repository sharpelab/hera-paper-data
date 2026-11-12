from hera.analysis import resolve_channels
r = run(6)
ch = {x.cid: x for x in resolve_channels(r.meta)}
B = r.col('magnet_field')
I = r.col('sr0_X') / ch['sr0'].gain
R = (r.col('sr1_X') / ch['sr1'].gain) / I
fig, ax = plt.subplots(2, 2, figsize=(10, 6))
ax[0,0].plot(B, R, lw=.8); ax[0,0].set(xlabel='B (T)', ylabel='signed Rxx (ohm)')
ax[0,1].plot(1/B[B>0], R[B>0], lw=.8); ax[0,1].set(xlim=(0,1), xlabel='1/B (1/T)', ylabel='signed Rxx (ohm)')
ax[1,0].plot(B, I*1e9); ax[1,0].set(xlabel='B (T)', ylabel='drain current (nA)')
ax[1,1].plot(B, r.col('k_2400_tg_curr')*1e12, label='TG')
ax[1,1].plot(B, r.col('k_2400_bg_curr')*1e12, label='BG')
ax[1,1].set(xlabel='B (T)', ylabel='gate current (pA)'); ax[1,1].legend()
fig.suptitle('data/6 raw: n_A=+3.2e12 cm^-2, D_A=0, B 0 to 10 T')
fig.tight_layout(); plt.show()
print(f"data/6: Rxx {R.min():.1f}..{R.max():.1f} ohm, I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, T median {np.median(r.col('T_sample')):.3f} K, max |X|/sensitivity {np.max(np.abs(r.col('sr1_X')))/50e-6:.2f}")
