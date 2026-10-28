from scipy.signal import find_peaks
from hera.analysis import sdh_onset

fig, ax = plt.subplots(2, 2, figsize=(12, 7))
for row, rid in enumerate((6, 7)):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col('magnet_field')
    I = r.col('sr0_X') / ch['sr0'].gain
    R = np.abs((r.col('sr1_X') / ch['sr1'].gain) / I)
    onset = sdh_onset(R, B, r_full_scale=5000)
    print(f'run {rid}: {onset.summary()}')
    k = np.argsort(B)
    ax[row,0].plot(B[k], R[k], lw=.7)
    ax[row,0].set(xlabel='B (T)', ylabel='|Rxx| (Ω)', title=f'run {rid} raw Rxx')
    for blo, ls in ((0.8,'-'),(1.0,'--')):
        f, spec = sdh_fft(R[:,None],B,b_range=(blo,10.0),nfft=4096,log=False,bg_degree=5,window='hann')
        y = spec[0]
        ax[row,1].plot(f,y/y.max(),ls,label=f'{blo}–10 T')
        if blo==0.8:
            peaks,_=find_peaks(y)
            peaks=[p for p in peaks if 3<=f[p]<=40]
            peaks=sorted(peaks,key=lambda p:y[p],reverse=True)[:6]
            print(f'run {rid} FFT 0.8–10 T peaks: '+', '.join(f'{f[p]:.2f} T' for p in peaks))
    ax[row,1].set(xlim=(0,40),xlabel='frequency (T)',ylabel='normalized FFT magnitude',title=f'run {rid} B-detrended FFT')
    ax[row,1].legend()
fig.tight_layout(); plt.show()
