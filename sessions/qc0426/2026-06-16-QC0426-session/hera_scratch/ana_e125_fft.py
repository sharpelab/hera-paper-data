import os
F=38; m=load_meta(F);ci={c:i for i,c in enumerate(m['columns'])}
fn=f"{file_path}/{F}/data.tsv.gz" if os.path.exists(f"{file_path}/{F}/data.tsv.gz") else f"{file_path}/{F}/data.tsv"
d=np.loadtxt(fn); B=d[:,ci['magnet_mag']]; Bhi=B.max()-0.05
from scipy.ndimage import gaussian_filter1d
def fft(col,Blo,N=8192):
    sel=(B>=Blo)&(B<=Bhi);x=1/B[sel];r=d[sel,ci[col]]/5e-9;o=np.argsort(x);x,r=x[o],r[o]
    xu=np.linspace(x.min(),x.max(),N);ru=np.interp(xu,x,r);ru=ru-np.polyval(np.polyfit(xu,ru,6),xu)
    Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);A=np.abs(np.fft.rfft(ru*np.hanning(N)));return Fa,A
F_lutt=83
fig,ax=plt.subplots(1,2,figsize=(14,4.5))
sel=B>0.8;x=1/B[sel];o=np.argsort(x)
for col,lab in [('sr1_X','sr1'),('sr2_X','sr2')]:
    r=(d[sel,ci[col]]/5e-9)[o];ax[0].plot(x[o],r-gaussian_filter1d(r,8),lw=.8,label=lab)
ax[0].set(xlabel='1/B (1/T)',ylabel='ΔRxx (ohm)',title='detrended oscillations vs 1/B');ax[0].legend()
for lo in (1.0,1.5,2.0):
    Fa,A=fft('sr1_X',lo);k=(Fa>2)&(Fa<150);ax[1].plot(Fa[k],A[k]/A[k].max(),label=f'B[{lo},{Bhi:.1f}]')
ax[1].axvline(F_lutt,color='k',ls='--',lw=1,label='Luttinger 83 T')
ax[1].set(xlabel='F (T)',ylabel='|FFT| sr1',title='SdH FFT to 150 T (window-stability)');ax[1].legend(fontsize=8)
fig.suptitle('Electron 12.5 mT SdH FFT (file 38) — full F range');plt.tight_layout();plt.show()
print('main tone stabilizing ~70 T across windows (de-aliased vs 50 mT); low-F band: watch for a stable 2nd tone')
