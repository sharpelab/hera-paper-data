from hera.analysis import resolve_channels
fig, ax = plt.subplots(4, 2, figsize=(12, 10), sharex='col')
for j, rid in enumerate((6, 7)):
    r = run(rid)
    ch = {x.cid: x for x in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / I)
    tgI, bgI = r.col('k_2400_tg_curr'), r.col('k_2400_bg_curr')
    T = r.col('T_sample')
    print(f'data/{rid}: {len(B)} points, interrupted={r.interrupted}; |Rxx| {R.min():.1f}–{R.max():.1f} Ω; I {I.min()*1e9:.3f}–{I.max()*1e9:.3f} nA; TG {tgI.min()*1e12:.0f}–{tgI.max()*1e12:.0f} pA, BG {bgI.min()*1e12:.0f}–{bgI.max()*1e12:.0f} pA; T {T.min():.3f}–{T.max():.3f} K')
    ax[0,j].plot(B,R,lw=.8); ax[0,j].set_ylabel('|Rxx| (Ω)')
    ax[1,j].plot(B,I*1e9,lw=.8); ax[1,j].set_ylabel('drain I (nA)')
    ax[2,j].plot(B,tgI*1e12,lw=.6,label='TG'); ax[2,j].plot(B,bgI*1e12,lw=.6,label='BG'); ax[2,j].legend(); ax[2,j].set_ylabel('gate I (pA)')
    ax[3,j].plot(B,T,lw=.8); ax[3,j].set_ylabel('sample T (K)'); ax[3,j].set_xlabel('B (T)')
    ax[0,j].set_title(f'data/{rid} — '+('electron' if rid==6 else 'hole'))
fig.tight_layout(); plt.show()
