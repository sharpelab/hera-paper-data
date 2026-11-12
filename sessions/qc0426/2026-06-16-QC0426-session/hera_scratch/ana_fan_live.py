# LIVE F(n) fan view — re-run to refresh as rows land.
import os, scipy.constants as cst
C_TG=cst.epsilon_0*3.0/15.6e-9; C_BG=1.298*C_TG; N_OFF=-7.095e14
# find the F(n) fan run (latest with that comment), else latest run dir
fid=None
for d in sorted([int(x) for x in os.listdir(file_path) if x.isdigit()], reverse=True):
    if 'landau-fan-vti' in ' '.join(load_meta(d).get('comments', [])):
        fid=d; break
if fid is None:
    print("no landau-fan-vti run found yet"); 
else:
    m=load_meta(fid); ci={c:i for i,c in enumerate(m['columns'])}
    fn=f"{file_path}/{fid}/data.tsv.gz" if os.path.exists(f"{file_path}/{fid}/data.tsv.gz") else f"{file_path}/{fid}/data.tsv"
    raw=np.genfromtxt(fn, invalid_raise=False)   # tolerate a half-written last line
    raw=raw[~np.isnan(raw).any(axis=1)]
    nfast=31; nr=raw.shape[0]//nfast
    if nr<1:
        print(f"fan file {fid}: <1 row so far ({raw.shape[0]} pts)")
    else:
        g=raw[:nr*nfast].reshape(nr,nfast,-1); I_bias=5e-9
        B=g[:,0,ci['magnet_mag']]; n=np.linspace(2,8,nfast)   # 1e12 cm^-2 (D=0 line)
        print(f"fan file {fid}: {nr}/225 B-rows, B {B[0]:.2f}->{B[-1]:.2f} T; drain med {np.median(g[:,:,ci['sr0_X']]/-1e6)*1e9:.2f} nA")
        fig,ax=plt.subplots(1,4,figsize=(19,4.3))
        for k,(nm,col,cm) in enumerate([('sr1 Rxx','sr1_X','viridis'),('sr2 Rxx','sr2_X','viridis'),('sr3 Rxy','sr3_X','seismic')]):
            R=g[:,:,ci[col]]/I_bias; vm=np.percentile(np.abs(R),99) if R.size else 1
            im=ax[k].pcolormesh(n,B,R,shading='auto',cmap=cm,vmin=(-vm if k==2 else 0),vmax=vm)
            fig.colorbar(im,ax=ax[k],label='ohm'); ax[k].set(xlabel='n (1e12 cm^-2)',ylabel='B (T)',title=nm)
        Im=g[:,:,ci['sr0_X']]/-1e6
        im=ax[3].pcolormesh(n,B,Im*1e9,shading='auto',cmap='inferno'); fig.colorbar(im,ax=ax[3],label='I (nA)')
        ax[3].set(xlabel='n (1e12 cm^-2)',ylabel='B (T)',title='drain B7 I')
        fig.suptitle(f'F(n) fan (file {fid}) LIVE — {nr}/225 rows, D=0 electron, 12.5 mT, Si=+50V'); plt.tight_layout(); plt.show()
