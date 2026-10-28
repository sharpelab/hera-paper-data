# F(n) Onsager map — |FFT|(n,F) per column. Branches = bright ridges. (re-run to refresh)
import os
fid=None
for d in sorted([int(x) for x in os.listdir(file_path) if x.isdigit()],reverse=True):
    if 'landau-fan-vti' in ' '.join(load_meta(d).get('comments',[])): fid=d;break
m=load_meta(fid);ci={c:i for i,c in enumerate(m['columns'])}
fn=f"{file_path}/{fid}/data.tsv.gz" if os.path.exists(f"{file_path}/{fid}/data.tsv.gz") else f"{file_path}/{fid}/data.tsv"
raw=np.genfromtxt(fn,invalid_raise=False);raw=raw[~np.isnan(raw).any(axis=1)]
nfast=31;nr=raw.shape[0]//nfast;g=raw[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci['magnet_mag']];n=np.linspace(2,8,nfast);Ib=5e-9
F_lutt=np.abs(n*1e16)*6.62607e-34/(4*1.602177e-19)
def colfft(col,Blo,Bhi,N=8192):
    sel=(B>=Blo)&(B<=Bhi);x=1/B[sel];o=np.argsort(x);xs=x[o];SP=[]
    for j in range(nfast):
        r=(g[sel,j,ci[col]]/Ib)[o];xu=np.linspace(xs.min(),xs.max(),N);ru=np.interp(xu,xs,r)
        ru=ru-np.polyval(np.polyfit(xu,ru,6),xu);SP.append(np.abs(np.fft.rfft(ru*np.hanning(N))))
    Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);return Fa,np.array(SP)
fig,ax=plt.subplots(1,2,figsize=(14,5.5))
for p,(col,lab) in enumerate([('sr1_X','sr1'),('sr2_X','sr2')]):
    Fa,SP=colfft(col,1.2,4.0);k=(Fa>3)&(Fa<95);Fk=Fa[k];img=SP[:,k];img=img/img.max(axis=1,keepdims=True)
    ax[p].pcolormesh(n,Fk,img.T,shading='auto',cmap='inferno')
    ax[p].plot(n,F_lutt,'c--',lw=1.5,label='full-density n·h/4e')
    ax[p].set(xlabel='n (1e12 cm^-2)',ylabel='F (T)',title=f'{lab}: |FFT|(n,F)');ax[p].legend(fontsize=8);ax[p].set_ylim(0,95)
fig.suptitle(f'F(n) Onsager map (fan {fid}, 12.5mT) — main tone tracks full-density; no clean 2nd branch');plt.tight_layout();plt.show()
print(f'{nr}/225 rows. Main ridge tracks n·h/4e (single full-density pocket -> consistent-with ABC); no resolved 2nd Onsager branch.')
