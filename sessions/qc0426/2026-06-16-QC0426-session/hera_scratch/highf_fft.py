import numpy as np,json,os
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
def fft(F,col,Blo,Bhi,N=8192,deg=6):
    m=json.load(open(f'data/{F}/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
    fn=f'data/{F}/data.tsv.gz' if os.path.exists(f'data/{F}/data.tsv.gz') else f'data/{F}/data.tsv'
    d=np.loadtxt(fn);B=d[:,ci['magnet_mag']];sel=(B>=Blo)&(B<=Bhi)
    x=1/B[sel];r=d[sel,ci[col]]/5e-9;o=np.argsort(x);x,r=x[o],r[o]
    xu=np.linspace(x.min(),x.max(),N);ru=np.interp(xu,x,r);ru=ru-np.polyval(np.polyfit(xu,ru,deg),xu)
    Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);A=np.abs(np.fft.rfft(ru*np.hanning(N)));return Fa,A
F_lutt=abs(8e12*1e4)*6.62607e-34/(4*1.602177e-19)
fig,ax=plt.subplots(1,2,figsize=(14,4.5))
# file 37 electron 50mT, full F range
for col in ['sr1_X','sr2_X','sr3_X']:
    Fa,A=fft(37,col,1.0,4.0);k=(Fa>2)&(Fa<160)
    ax[0].plot(Fa[k],A[k]/A[k].max(),label=col)
ax[0].axvline(F_lutt,color='k',ls='--',lw=1,label=f'Luttinger {F_lutt:.0f}T')
ax[0].set(xlabel='F (T)',ylabel='|FFT|',title='file 37 electron 50mT, B[1,4] (full F)');ax[0].legend(fontsize=8)
# window stability at high F (sr1)
for lo in (1.0,1.5,2.0):
    Fa,A=fft(37,'sr1_X',lo,4.0);k=(Fa>2)&(Fa<160)
    ax[1].plot(Fa[k],A[k]/A[k].max(),label=f'B[{lo},4]')
ax[1].axvline(F_lutt,color='k',ls='--',lw=1)
ax[1].set(xlabel='F (T)',ylabel='|FFT| sr1',title='sr1 window stability (full F)');ax[1].legend(fontsize=8)
fig.suptitle('Electron snake file 37 (50mT) — full frequency range to ~160 T');plt.tight_layout()
fig.savefig('hera_scratch/highf_snake.png',dpi=110);print('saved; Luttinger F_tot=%.0f T'%F_lutt)
