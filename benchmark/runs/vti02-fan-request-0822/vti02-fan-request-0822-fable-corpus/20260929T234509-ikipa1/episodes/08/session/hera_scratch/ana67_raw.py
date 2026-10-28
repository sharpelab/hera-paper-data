# Runs 6-7 raw: Rxx(B) and drain current, gain-divided, no background removal
runs67 = {}
fig, axs = plt.subplots(2, 2, figsize=(12, 7), sharex='col')
for i, (rid, nlab) in enumerate(((6, '+3.2e12 (electron)'), (7, '-1.2e12 (hole)'))):
    r = run(rid)
    B = r.col('magnet_field'); o = np.argsort(B); B = B[o]
    I = r.col('sr0_X')[o] / (-1e6)          # drain current, A (Ithaco -1e6 V/A)
    R = r.col('sr1_X')[o] / np.abs(I)       # Rxx, ohm (sr1 gain 1)
    runs67[rid] = (B, R, I)
    print(summarize_run(r))
    print(f'run {rid}: I_drain median {np.median(np.abs(I))*1e9:.2f} nA; '
          f'R(B_lo) {R[:5].mean():.0f} ohm, R(B_hi) {R[-5:].mean():.0f} ohm, Rmax {R.max():.0f} ohm '
          f'({R.max()/5.05e3*100:.0f}% of 5 kOhm FS - no clip)')
    axs[0, i].plot(B, R, lw=0.6)
    axs[0, i].set_ylabel('Rxx (ohm)'); axs[0, i].set_title(f'run {rid}: n = {nlab}, D = 0, T = 1.2-1.3 K')
    axs[1, i].plot(B, np.abs(I)*1e9, lw=0.6, color='tab:orange')
    axs[1, i].set_ylabel('|I_drain| (nA)'); axs[1, i].set_xlabel('B (T)')
plt.tight_layout(); plt.show()
