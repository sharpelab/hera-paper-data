import numpy as np,json,os
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
fn='data/39/data.tsv.gz' if os.path.exists('data/39/data.tsv.gz') else 'data/39/data.tsv'
m=json.load(open('data/39/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
raw=np.genfromtxt(fn,invalid_raise=False);raw=raw[~np.isnan(raw).any(axis=1)]
nfast=31;nr=raw.shape[0]//nfast;g=raw[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci['magnet_mag']];n=np.linspace(2,8,nfast);Ib=5e-9
sel=B>=1.5;x=1/B[sel];o=np.argsort(x);x=x[o]
print(f"{nr}/225 rows, B[1.5,4] -> {sel.sum()} pts, 1/B span {x.max()-x.min():.3f}")
fig,ax=plt.subplots(figsize=(8,9))
off=0
for j in range(0,nfast,3):   # ~11 densities
    R=(g[sel,j,ci['sr1_X']]/Ib)[o];osc=R-gaussian_filter1d(R,10)
    ax.plot(x,osc+off,lw=.8)
    ax.text(x.max()*1.005,off,f'n={n[j]:.1f}',fontsize=7,va='center')
    off+=35
ax.set(xlabel='1/B (1/T)',ylabel='ΔRxx sr1 (offset) — increasing n upward',title=f'F(n) by eye: detrended ΔRxx(1/B) vs density (fan {nr}/225)')
plt.tight_layout();fig.savefig('hera_scratch/fn_waterfall.png',dpi=120);print('saved')
