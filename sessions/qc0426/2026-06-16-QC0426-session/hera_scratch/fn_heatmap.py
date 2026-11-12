import numpy as np,json,os
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
m=json.load(open('data/39/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
fn='data/39/data.tsv.gz' if os.path.exists('data/39/data.tsv.gz') else 'data/39/data.tsv'
raw=np.genfromtxt(fn,invalid_raise=False);raw=raw[~np.isnan(raw).any(axis=1)]
nfast=31;nr=raw.shape[0]//nfast;g=raw[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci['magnet_mag']];n=np.linspace(2,8,nfast);Ib=5e-9
F_lutt=np.abs(n*1e16)*6.62607e-34/(4*1.602177e-19)
def colfft(col,Blo,Bhi,N=8192):
    sel=(B>=Blo)&(B<=Bhi);x=1/B[sel];o=np.argsort(x);xs=x[o]
    SP=[]
    for j in range(nfast):
        r=(g[sel,j,ci[col]]/Ib)[o];xu=np.linspace(xs.min(),xs.max(),N);ru=np.interp(xu,xs,r)
        ru=ru-np.polyval(np.polyfit(xu,ru,6),xu);A=np.abs(np.fft.rfft(ru*np.hanning(N)))
        SP.append(A)
    Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);return Fa,np.array(SP)
fig,ax=plt.subplots(1,2,figsize=(14,5.5))
for p,(col,lab) in enumerate([('sr1_X','sr1'),('sr2_X','sr2')]):
    Fa,SP=colfft(col,1.2,4.0);k=(Fa>3)&(Fa<95);Fk=Fa[k]
    img=SP[:,k];img=img/img.max(axis=1,keepdims=True)   # normalize each column
    im=ax[p].pcolormesh(n,Fk,img.T,shading='auto',cmap='inferno')
    ax[p].plot(n,F_lutt,'c--',lw=1.5,label='full-density n·h/4e')
    ax[p].plot(n,0.5*F_lutt,'w:',lw=1,label='½ full-density (ref)')
    ax[p].set(xlabel='n (1e12 cm^-2)',ylabel='F (T)',title=f'{lab}: |FFT|(n,F)');ax[p].legend(fontsize=8);ax[p].set_ylim(0,95)
fig.suptitle('F(n) Onsager map from fan (file 39, 12.5mT, B[1.2,4]) — bright ridges = Fermi-surface branches');plt.tight_layout()
fig.savefig('hera_scratch/fn_heatmap.png',dpi=120);print('saved; rows',nr)
