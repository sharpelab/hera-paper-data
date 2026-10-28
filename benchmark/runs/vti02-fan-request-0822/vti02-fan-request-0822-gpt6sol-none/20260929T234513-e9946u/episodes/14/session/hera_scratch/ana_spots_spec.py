from scipy.signal import find_peaks
fig, ax = plt.subplots(1, 2, figsize=(11, 4))
for j, rid in enumerate((6, 7)):
    r = run(rid)
    ch = {x.cid: x for x in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / I)
    order = np.argsort(B)
    f, spec = sdh_fft(R[order,None], B[order], b_range=(2,9.8), nfft=2048, bg_degree=5)
    y = spec[0] / np.max(spec[0])
    pk,_ = find_peaks(y,prominence=.07)
    pk = sorted((p for p in pk if 2 < f[p] < 60),key=lambda p:y[p],reverse=True)[:7]
    print(f'data/{rid}: strongest exploratory FFT peaks (2–9.8 T): '+', '.join(f'{f[p]:.1f} T ({y[p]:.2f} rel.)' for p in pk))
    ax[j].plot(f,y,lw=1); ax[j].set_xlim(0,60); ax[j].set_ylim(0,1.05); ax[j].set_xlabel('SdH frequency (T)'); ax[j].set_ylabel('relative FFT amplitude'); ax[j].set_title(f'data/{rid}')
    for p in pk[:4]: ax[j].axvline(f[p],color='k',alpha=.2,lw=.7)
fig.tight_layout(); plt.show()
