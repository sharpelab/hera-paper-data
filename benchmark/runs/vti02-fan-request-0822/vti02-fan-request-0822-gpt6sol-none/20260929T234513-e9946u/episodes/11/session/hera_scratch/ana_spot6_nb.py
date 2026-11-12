from scipy.signal import find_peaks
from hera.analysis import resolve_channels, current_channel, sdh_onset
g6 = run(6)
ch6 = resolve_channels(g6.meta)
ic6 = current_channel(ch6)
vc6 = next(ch for ch in ch6 if ch.cid == 'sr1')
B6 = g6.col('magnet_field')
I6 = g6.col(ic6.col) / ic6.gain
V6 = g6.col(vc6.col) / vc6.gain
R6 = np.abs(V6 / I6)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
ax[0].plot(B6, V6*1e6, '.', ms=1.5); ax[0].set_ylabel('raw sr1 X (µV)')
ax[1].plot(B6, I6*1e9, '.', ms=1.5); ax[1].set_ylabel('raw drain I (nA)')
for a in ax: a.set_xlabel('B (T)')
fig.suptitle('run 6 raw channels — B_1–B_2, A n=+3.2e12, D=0'); fig.tight_layout(); plt.show()
fig, ax = plt.subplots(1, 2, figsize=(11, 3.5))
ax[0].plot(B6, R6, lw=.8); ax[0].set(xlabel='B (T)',ylabel='|Rxx| (Ω)',title='run 6 |V/I|')
for lo, color in [(2,'C0'),(3,'C1'),(4,'C2')]:
    ff, spec = sdh_fft(R6[:,None], B6, b_range=(lo,9.8), nfft=2048, bg_degree=5, log=False)
    m = (ff>=2)&(ff<=45); yy=spec[0,m]
    ax[1].plot(ff[m], yy/yy.max(), color=color, label=f'{lo}–9.8 T')
    pk,_=find_peaks(yy, prominence=.1); top=sorted(pk,key=lambda p: yy[p],reverse=True)[:4]
    print(f'FFT {lo}–9.8 T:', [(round(float(ff[m][p]),1),round(float(yy[p]/yy.max()),2)) for p in top])
ax[1].set(xlabel='F (T)',ylabel='normalized FFT',title='window-dependent spectrum'); ax[1].legend()
fig.tight_layout(); plt.show()
print('R range/median Ω:',R6.min(),np.median(R6),R6.max(),'I nA:',np.min(I6)*1e9,np.median(I6)*1e9,np.max(I6)*1e9)
print('T range K:',np.min(g6.col('T_sample')),np.max(g6.col('T_sample')))
print('gate max |I| pA:',max(abs(g6.col('k_2400_tg_curr')))*1e12,max(abs(g6.col('k_2400_bg_curr')))*1e12)
print(sdh_onset(R6,B6,b_lo=.3,b_hi=10,r_full_scale=5000).summary())
