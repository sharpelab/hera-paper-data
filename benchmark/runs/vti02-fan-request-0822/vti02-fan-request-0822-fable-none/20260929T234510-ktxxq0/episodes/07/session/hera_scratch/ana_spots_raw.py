# Runs 6 & 7 — raw Rxx(B), gains from measurement_config
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, rid in zip(ax, (6, 7)):
    r = open_run(f'data/{rid}')
    B = np.abs(r.col('magnet_field'))
    mc = r.meta['measurement_config']
    I = r.col('sr0_X') / mc['sr0_gain']          # drain current, A (gain -1e6)
    Rxx = (r.col('sr1_X') / 1.0) / I             # sr1 gain 1
    a.plot(B, Rxx, lw=0.6)
    a.set_xlabel('|B| (T)'); a.set_ylabel(r'$R_{xx}$ ($\Omega$)')
    a.set_title(f"run {rid}: {r.tags[0].split(';')[0]}")
    print(f"run {rid}: {r.rows} rows, B {B[0]:.3f}->{B[-1]:.3f} T, I_med {np.median(np.abs(I))*1e9:.2f} nA, "
          f"R {np.nanmin(Rxx):.0f}..{np.nanmax(Rxx):.0f} ohm, interrupted={r.interrupted}")
fig.tight_layout()
