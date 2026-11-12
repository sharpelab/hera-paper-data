# Runs 4-7 vs runs 0-3 — post-excursion health comparison (reentry-baseline).
# Pairs: (health, reference): TG+ (4,0), TG- (5,1), BG+ (6,2), BG- (7,3).
# Reference restricted to the health leg's V range.
pairs = [(4, 0, 'TG +', 'k_2400_tg_curr'), (5, 1, 'TG −', 'k_2400_tg_curr'),
         (6, 2, 'BG +', 'k_2400_bg_curr'), (7, 3, 'BG −', 'k_2400_bg_curr')]

fig, axes = plt.subplots(2, 4, figsize=(15, 6.5))
print(f"{'leg':6} {'leak_new':>9} {'leak_ref':>9} {'d_peak1':>8} {'d_peak2':>8} {'shape r1/r2':>12} {'scale r1/r2':>12}")
for j, (hid, rid, leg, icol) in enumerate(pairs):
    h, rr = run(hid), run(rid)
    vh, vr = h.col_at(1), rr.col_at(1)
    m = np.abs(vr) <= np.abs(vh).max() + 1e-6          # in-range slice of reference
    # 1) leakage above own offset
    def leak(r, v, i0mask):
        i = r.col(icol)
        i0 = np.median(i[np.abs(v) < 0.5])
        return np.abs(i - i0).max()
    lk_h, lk_r = leak(h, vh, None), np.abs(rr.col(icol)[m] - np.median(rr.col(icol)[np.abs(vr) < 0.5])).max()
    row = [f'{leg:6} {lk_h*1e12:8.0f}p {lk_r*1e12:8.0f}p']
    stats = []
    for k, ch in enumerate(('sr1_X', 'sr2_X')):
        xh, xr = np.abs(h.col(ch)), np.abs(rr.col(ch)[m])
        vrm = vr[m]
        # 2) feature position: |X| max within |V|<2 (CNP-adjacent feature)
        mh, mr = np.abs(vh) < 2, np.abs(vrm) < 2
        dpk = vh[mh][xh[mh].argmax()] - vrm[mr][xr[mr].argmax()]
        # 3) shape: correlation of log|X| on common grid
        xi = np.interp(vh, vrm[np.argsort(vrm)], xr[np.argsort(vrm)])
        ok = (xh > 1e-7) & (xi > 1e-7)
        shape = np.corrcoef(np.log(xh[ok]), np.log(xi[ok]))[0, 1]
        # 4) scale: median ratio where reference is above noise
        scale = np.median(xh[ok] / xi[ok])
        stats.append((dpk, shape, scale))
        ax = axes[k, j]
        ax.plot(vrm, xr, lw=0.8, label=f'ref (run {rid})')
        ax.plot(vh, xh, lw=0.8, ls='--', label=f'new (run {hid})')
        ax.set_yscale('log')
        if k == 0: ax.set_title(f'{leg}: run {hid} vs {rid}', fontsize=10)
        ax.set_ylabel(f'|{ch}| (V)') if j == 0 else None
        ax.legend(fontsize=6)
        if k == 1: ax.set_xlabel('gate V')
    print(row[0] + f' {stats[0][0]:+7.2f}V {stats[1][0]:+7.2f}V '
          f'{stats[0][1]:5.2f}/{stats[1][1]:4.2f} {stats[0][2]:5.2f}/{stats[1][2]:4.2f}')
fig.suptitle('Health re-check (runs 4–7, dashed) vs pre/peri-excursion reference (runs 0–3, solid), in-range')
fig.tight_layout()
