# Gate C — device-init/gate-current-sanity-check, runs 0-3. RAW FIRST.
# Top row: lock-in |X| (raw volts, no division — sr0 rides Ithaco output).
# Bottom row: both gate currents (pA).
legs = [(0, 'k_2400_tg_volt', 'TG 0→+7 V'), (1, 'k_2400_tg_volt', 'TG 0→−6 V'),
        (2, 'k_2400_bg_volt', 'BG 0→+4.5 V'), (3, 'k_2400_bg_volt', 'BG 0→−4.5 V')]
fig, axes = plt.subplots(2, 4, figsize=(15, 6.5))
for j, (rid, vcol, leg) in enumerate(legs):
    r = run(rid)
    v = r.col_at(1)  # swept axis (also fp'd -> duplicate name; col_at disambiguates)
    ax = axes[0, j]
    for ch in ('sr0_X', 'sr1_X', 'sr2_X', 'sr3_X'):
        ax.plot(v, np.abs(r.col(ch)), lw=0.8, label=ch[:3])
    ax.set_yscale('log')
    ax.set_title(f'run {rid}: {leg}', fontsize=10)
    ax.legend(fontsize=6)
    if j == 0:
        ax.set_ylabel('|X| (V, raw)')
    ax = axes[1, j]
    ax.plot(v, r.col('k_2400_tg_curr') * 1e12, lw=0.8, label='I_tg')
    ax.plot(v, r.col('k_2400_bg_curr') * 1e12, lw=0.8, label='I_bg')
    ax.axhline(0, color='k', lw=0.3)
    ax.legend(fontsize=6)
    ax.set_xlabel(vcol + ' (V)')
    if j == 0:
        ax.set_ylabel('gate I (pA)')
fig.suptitle('Gate C — gate-current-sanity-check, raw traces (runs 0–3)')
fig.tight_layout()
