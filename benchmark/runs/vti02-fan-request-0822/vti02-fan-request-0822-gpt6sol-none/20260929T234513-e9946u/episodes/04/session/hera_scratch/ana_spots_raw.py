from hera.analysis import resolve_channels
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
spot = {}
for j, rid in enumerate((6, 7)):
    r = run(rid)
    ch = {q.cid: q for q in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    X = r.col('sr1_X') / ch['sr1'].gain
    R = np.abs(X / I)
    spot[rid] = dict(B=B, I=I, X=X, R=R)
    a = ax[0, j]; a.plot(B, R, lw=.65)
    a.set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title=f'data/{rid}: raw B_1–B_2')
    b = ax[1, j]
    b.plot(B, r.col('k_2400_tg_curr')*1e12, lw=.6, label='TG')
    b.plot(B, r.col('k_2400_bg_curr')*1e12, lw=.6, label='BG')
    b.set(xlabel='B (T)', ylabel='gate current (pA)'); b.legend()
    print(f'data/{rid}: {len(B)} rows, B {B[0]:.3f}→{B[-1]:.3f} T, '
          f'R {R.min():.1f}..{R.max():.1f} Ω, max |X| {abs(X).max()*1e6:.2f} µV / 50 µV FS, '
          f'I_drain {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA, '
          f'T_sample {r.col("T_sample").min():.3f}..{r.col("T_sample").max():.3f} K, '
          f'interrupted={r.interrupted}')
fig.tight_layout(); plt.show()
