# Detrended SdH linecuts in 1/B (re-run to refresh). sr1 Rxx, no FFT.
import os
from scipy.ndimage import gaussian_filter1d
Ib=5e-9
def load(fid):
    m=load_meta(fid);ci={c:i for i,c in enumerate(m['columns'])}
    fn=f"{file_path}/{fid}/data.tsv.gz" if os.path.exists(f"{file_path}/{fid}/data.tsv.gz") else f"{file_path}/{fid}/data.tsv"
    raw=np.genfromtxt(fn,invalid_raise=False);return m,ci,raw[~np.isnan(raw).any(axis=1)]
fig,ax=plt.subplots(1,2,figsize=(14,5.5))
# Panel A: reference clean QO = file 38 (n=+8e12, full B 0->4 T)
m,ci,d=load(38);B=d[:,ci['magnet_mag']];sel=B>0.6;x=1/B[sel];o=np.argsort(x);x=x[o]
R=(d[sel,ci['sr1_X']]/Ib)[o];osc=R-gaussian_filter1d(R,18)
ax[0].plot(x,osc,lw=.9,color='C3')
ax[0].set(xlabel='1/B (1/T)',ylabel='ΔRxx (ohm)',title='REF file 38: n=+8e12 full B (clean QO)')
# Panel B: fan fixed-density detrended in 1/B, waterfall
fid=None
for dd in sorted([int(x) for x in os.listdir(file_path) if x.isdigit()],reverse=True):
    if 'landau-fan-vti' in ' '.join(load_meta(dd).get('comments',[])): fid=dd;break
m,ci,raw=load(fid);nfast=31;nr=raw.shape[0]//nfast;g=raw[:nr*nfast].reshape(nr,nfast,-1)
B=g[:,0,ci['magnet_mag']];n=np.linspace(2,8,nfast);xb=1/B;ob=np.argsort(xb);xb=xb[ob]
print(f"fan file {fid}: {nr}/225 rows, B {B.min():.2f}-{B.max():.2f} T -> 1/B span {xb.max()-xb.min():.3f}")
off=0;sig=max(3,nr//6)
for j in [30,23,15,7,0]:
    R=(g[:,j,ci['sr1_X']]/Ib)[ob];osc=R-gaussian_filter1d(R,sig)
    ax[1].plot(xb,osc+off,lw=.9,label=f'n={n[j]:.1f}');off+=ax[1].get_ylim()[1]*0+ (np.nanstd(osc)*4 if np.isfinite(np.nanstd(osc)) else 5)
ax[1].set(xlabel='1/B (1/T)',ylabel='ΔRxx (offset)',title=f'fan fixed-n detrended ΔRxx(1/B), {nr}/225 rows')
ax[1].legend(fontsize=8,title='n (1e12)')
fig.suptitle('Detrended SdH linecuts in 1/B (raw Rxx minus smooth background)');plt.tight_layout();plt.show()
