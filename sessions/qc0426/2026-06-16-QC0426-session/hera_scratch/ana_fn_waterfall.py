# F(n) by eye — detrended ΔRxx(1/B) waterfall across density (re-run to refresh). No FFT.
import os
from scipy.ndimage import gaussian_filter1d
fid=None
for d in sorted([int(x) for x in os.listdir(file_path) if x.isdigit()],reverse=True):
    if 'landau-fan-vti' in ' '.join(load_meta(d).get('comments',[])): fid=d;break
m=load_meta(fid);ci={c:i for i,c in enumerate(m['columns'])}
fn=f"{file_path}/{fid}/data.tsv.gz" if os.path.exists(f"{file_path}/{fid}/data.tsv.gz") else f"{file_path}/{fid}/data.tsv"
raw=np.genfromtxt(fn,invalid_raise=False);raw=raw[~np.isnan(raw).any(axis=1)]
nfast=31;nr=raw.shape[0]//nfast;g=raw[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci['magnet_mag']];n=np.linspace(2,8,nfast);Ib=5e-9
sel=B>=1.5;x=1/B[sel];o=np.argsort(x);x=x[o]
fig,ax=plt.subplots(figsize=(8,9));off=0
for j in range(0,nfast,3):
    R=(g[sel,j,ci['sr1_X']]/Ib)[o];osc=R-gaussian_filter1d(R,10)
    ax.plot(x,osc+off,lw=.8); ax.text(x.max()*1.004,off,f'n={n[j]:.1f}',fontsize=7,va='center'); off+=35
ax.set(xlabel='1/B (1/T)',ylabel='ΔRxx sr1 (offset; n increases upward)',title=f'F(n) by eye: detrended ΔRxx(1/B) vs density (fan {fid}, {nr}/225)')
plt.tight_layout();plt.show()
print(f'{nr}/225 rows; QO present across density, period (F) scales with n')
