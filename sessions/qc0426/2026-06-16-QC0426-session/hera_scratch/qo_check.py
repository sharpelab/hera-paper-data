import numpy as np,json,os
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
m=json.load(open('data/38/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
d=np.loadtxt('data/38/data.tsv.gz');B=d[:,ci['magnet_mag']];Ib=5e-9
fig,ax=plt.subplots(1,2,figsize=(14,4.8))
sel=B>0.6;x=1/B[sel];o=np.argsort(x);x=x[o]
for col,lab in [('sr1_X','sr1'),('sr2_X','sr2')]:
    R=(d[sel,ci[col]]/Ib)[o];osc=R-gaussian_filter1d(R,18)
    ax[0].plot(x,osc,lw=.9,label=lab)
ax[0].set(xlabel='1/B (1/T)',ylabel='ΔRxx (ohm)',title='file 38 n=+8e12: detrended ΔRxx vs 1/B');ax[0].legend()
ax[0].grid(alpha=.3)
# zoom high-field (low 1/B) where amplitude is biggest
sel2=B>1.5;x2=1/B[sel2];o2=np.argsort(x2);x2=x2[o2]
R2=(d[sel2,ci['sr1_X']]/Ib)[o2];osc2=R2-gaussian_filter1d(R2,12)
ax[1].plot(x2,osc2,'.-',ms=3,lw=.9,color='C0')
ax[1].set(xlabel='1/B (1/T)',ylabel='ΔRxx sr1 (ohm)',title='zoom B>1.5T (1/B<0.67): look for beat');ax[1].grid(alpha=.3)
fig.suptitle('QO check — file 38 (n=+8e12, 12.5mT) detrended in 1/B');plt.tight_layout();fig.savefig('hera_scratch/qo_check.png',dpi=120)
print('saved')
