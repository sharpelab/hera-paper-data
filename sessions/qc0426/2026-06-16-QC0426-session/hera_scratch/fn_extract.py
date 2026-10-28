import numpy as np,json,os
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
m=json.load(open('data/39/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
fn='data/39/data.tsv.gz' if os.path.exists('data/39/data.tsv.gz') else 'data/39/data.tsv'
raw=np.genfromtxt(fn,invalid_raise=False);raw=raw[~np.isnan(raw).any(axis=1)]
nfast=31;nr=raw.shape[0]//nfast;g=raw[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci['magnet_mag']];n=np.linspace(2,8,nfast);Ib=5e-9
I=g[:,:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
print(f"COMPLETE: {nr}/225 rows, B {B.min():.2f}-{B.max():.2f}, interrupted={m['interrupted']}")
print(f"drain(B7) I med {np.median(I)*1e9:.2f} min {I.min()*1e9:.2f} nA")
def colpeaks(col,Blo,Bhi,N=8192):
    sel=(B>=Blo)&(B<=Bhi);x=1/B[sel];out=[]
    for j in range(nfast):
        r=g[sel,j,ci[col]]/Ib;o=np.argsort(x);xx=x[o];rr=r[o]
        xu=np.linspace(xx.min(),xx.max(),N);ru=np.interp(xu,xx,rr);ru=ru-np.polyval(np.polyfit(xu,ru,6),xu)
        Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);A=np.abs(np.fft.rfft(ru*np.hanning(N)))
        out.append((Fa,A))
    return out
F_lutt=np.abs(n*1e16)*6.62607e-34/(4*1.602177e-19)  # n in 1e12cm-2 -> m-2 *1e16
fig,ax=plt.subplots(1,2,figsize=(14,5.5))
for p,(col,lab) in enumerate([('sr1_X','sr1'),('sr2_X','sr2')]):
    specs=colpeaks(col,1.2,4.0)
    mains=[];seconds=[]
    for j,(Fa,A) in enumerate(specs):
        k=(Fa>3)&(Fa<95);Fk,Ak=Fa[k],A[k]
        pk,_=find_peaks(Ak,height=0.30*Ak.max(),distance=int(4/(Fa[1]-Fa[0])))
        pk=pk[np.argsort(Ak[pk])[::-1]]
        fs=sorted(Fk[pk][:3]) if len(pk) else []
        # main = highest-F strong peak; second = a low-F peak well below main
        if fs:
            mains.append(fs[-1]); low=[f for f in fs if f<fs[-1]-10]
            seconds.append(low[0] if low else np.nan)
        else: mains.append(np.nan);seconds.append(np.nan)
    ax[p].plot(n,mains,'o-',label='main tone',color='C0')
    ax[p].plot(n,seconds,'s-',label='2nd tone',color='C3')
    ax[p].plot(n,F_lutt,'k--',lw=1,label='full-density n·h/4e')
    ax[p].plot(n,F_lutt-np.array(mains),'g:',lw=1,label='full - main (expected 2nd)')
    ax[p].set(xlabel='n (1e12 cm^-2)',ylabel='F (T)',title=f'{lab} F(n)');ax[p].legend(fontsize=8);ax[p].set_ylim(0,95)
    print(f'{lab}: main F(n)={[round(x) for x in mains]}')
    print(f'{lab}: 2nd  F(n)={[round(x) if np.isfinite(x) else None for x in seconds]}')
fig.suptitle('F(n) Onsager from fan (file 39, 12.5mT) — per-column FFT');plt.tight_layout();fig.savefig('hera_scratch/fn_onsager.png',dpi=120);print('saved')
