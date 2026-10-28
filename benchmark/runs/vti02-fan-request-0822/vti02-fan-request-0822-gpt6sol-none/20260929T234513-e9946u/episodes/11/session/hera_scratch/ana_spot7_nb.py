from scipy.signal import find_peaks
from hera.analysis import resolve_channels, current_channel, sdh_onset
g7 = run(7)
ch7 = resolve_channels(g7.meta)
ic7 = current_channel(ch7)
vc7 = next(ch for ch in ch7 if ch.cid == 'sr1')
B7 = g7.col('magnet_field')
I7 = g7.col(ic7.col) / ic7.gain
V7 = g7.col(vc7.col) / vc7.gain
R7 = np.abs(V7 / I7)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
ax[0].plot(B7, V7*1e6, '.', ms=1.5); ax[0].set_ylabel('raw sr1 X (µV)')
ax[1].plot(B7, I7*1e9, '.', ms=1.5); ax[1].set_ylabel('raw drain I (nA)')
for a in ax: a.set_xlabel('B (T)')
fig.suptitle('run 7 raw channels — B_1–B_2, A n=−1.2e12, D=0'); fig.tight_layout(); plt.show()
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
ax[0].plot(B7, R7, lw=.8); ax[0].set(xlabel='B (T)',ylabel='|Rxx| (Ω)',title='run 7 |V/I|')
for lo, color in [(2,'C0'),(3,'C1'),(4,'C2')]:
    ff, spec = sdh_fft(R7[:,None], B7, b_range=(lo,9.8), nfft=2048, bg_degree=5, log=False)
    m = (ff>=2)&(ff<=45); yy=spec[0,m]
    ax[1].plot(ff[m], yy/yy.max(), color=color, label=f'{lo}–9.8 T')
    pk,_=find_peaks(yy, prominence=.1); top=sorted(pk,key=lambda p: yy[p],reverse=True)[:4]
    print(f'FFT {lo}–9.8 T:', [(round(float(ff[m][p]),1),round(float(yy[p]/yy.max()),2)) for p in top])
ax[1].set(xlabel='F (T)',ylabel='normalized FFT',title='window-dependent spectrum'); ax[1].legend()
fig.tight_layout(); plt.show()
print('R range/median Ω:',R7.min(),np.median(R7),R7.max(),'I nA:',np.min(I7)*1e9,np.median(I7)*1e9,np.max(I7)*1e9)
print('T range K:',np.min(g7.col('T_sample')),np.max(g7.col('T_sample')))
print('gate max |I| pA:',max(abs(g7.col('k_2400_tg_curr')))*1e12,max(abs(g7.col('k_2400_bg_curr')))*1e12)
print(sdh_onset(R7,B7,b_lo=.3,b_hi=10,r_full_scale=5000).summary())
