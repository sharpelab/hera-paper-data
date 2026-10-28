import numpy as np,json,os
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
F='38';m=json.load(open(f'data/{F}/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
fn=f'data/{F}/data.tsv.gz' if os.path.exists(f'data/{F}/data.tsv.gz') else f'data/{F}/data.tsv'
d=np.loadtxt(fn);B=d[:,ci['magnet_mag']]
def fft(col,Blo,Bhi,N=8192):
    sel=(B>=Blo)&(B<=Bhi);x=1/B[sel];r=d[sel,ci[col]]/5e-9;o=np.argsort(x);x,r=x[o],r[o]
    xu=np.linspace(x.min(),x.max(),N);ru=np.interp(xu,x,r);ru=ru-np.polyval(np.polyfit(xu,ru,6),xu)
    Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);A=np.abs(np.fft.rfft(ru*np.hanning(N)));return Fa,A
Bhi=B.max()-0.05;F_lutt=83
fig,ax=plt.subplots(1,2,figsize=(14,4.5))
for col in ['sr1_X','sr2_X','sr3_X']:
    Fa,A=fft(col,1.0,Bhi);k=(Fa>2)&(Fa<150);ax[0].plot(Fa[k],A[k]/A[k].max(),label=col)
ax[0].axvline(F_lutt,color='k',ls='--',lw=1,label='Luttinger 83T')
ax[0].set(xlabel='F (T)',ylabel='|FFT|',title=f'file38 12.5mT B[1,{Bhi:.1f}] (full F)');ax[0].legend(fontsize=8)
for lo in (1.0,1.5,2.0):
    Fa,A=fft('sr1_X',lo,Bhi);k=(Fa>2)&(Fa<150);ax[1].plot(Fa[k],A[k]/A[k].max(),label=f'B[{lo},{Bhi:.1f}]')
ax[1].axvline(F_lutt,color='k',ls='--',lw=1)
ax[1].set(xlabel='F (T)',ylabel='|FFT| sr1',title='sr1 window stability');ax[1].legend(fontsize=8);ax[1].set_xlim(0,150)
fig.suptitle(f'12.5mT electron PARTIAL ({(B>=1).sum()} pts B>=1T) — de-aliasing check');plt.tight_layout()
fig.savefig('hera_scratch/peek38.png',dpi=110)
# dominant peak stability
from scipy.signal import find_peaks
for col in ['sr1_X','sr3_X']:
    pk=[]
    for lo in (1.0,1.5,2.0):
        Fa,A=fft(col,lo,Bhi);k=(Fa>2)&(Fa<150);Fk,Ak=Fa[k],A[k]
        p,_=find_peaks(Ak,height=0.4*Ak.max(),distance=20);pk.append([round(Fk[i],0) for i in p[np.argsort(Ak[p])[::-1]][:3]])
    print(f'{col} top peaks per window (lo=1/1.5/2): {pk}')
print('saved peek38.png')
