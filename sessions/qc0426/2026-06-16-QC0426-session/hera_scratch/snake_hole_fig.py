import numpy as np,json,os
import matplotlib;matplotlib.use("Agg");import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
F='36';m=json.load(open(f'data/{F}/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
fn=f'data/{F}/data.tsv.gz' if os.path.exists(f'data/{F}/data.tsv.gz') else f'data/{F}/data.tsv'
d=np.loadtxt(fn);B=d[:,ci['magnet_mag']];I_bias=5e-9
R1=d[:,ci['sr1_X']]/I_bias;R2=d[:,ci['sr2_X']]/I_bias
fig,ax=plt.subplots(1,3,figsize=(16,4.5))
ax[0].plot(B,R1,'.-',ms=3,label='sr1');ax[0].plot(B,R2,'.-',ms=3,label='sr2')
ax[0].set(xlabel='B (T)',ylabel='Rxx (ohm)',title='raw Rxx(B) n=-8e12, 200uV');ax[0].legend()
# detrend vs 1/B
sel=B>0.5;x=1/B[sel];o=np.argsort(x);x=x[o]
for col,lab,axi in [('sr1_X','sr1',1),('sr2_X','sr2',1)]:
    r=(d[sel,ci[col]]/I_bias)[o]; bg=gaussian_filter1d(r,5); osc=r-bg
    ax[1].plot(x,osc,'.-',ms=3,label=f'{lab} ΔRxx')
ax[1].set(xlabel='1/B (1/T)',ylabel='ΔRxx (ohm)',title='detrended osc vs 1/B (B>0.5T)');ax[1].legend()
# FFT sr1, window B[0.6,4]
for lo in (0.6,1.0):
    s2=(B>=lo)&(B<=4);x2=1/B[s2];r2=d[s2,ci['sr1_X']]/I_bias;oo=np.argsort(x2);x2,r2=x2[oo],r2[oo]
    N=4096;xu=np.linspace(x2.min(),x2.max(),N);ru=np.interp(xu,x2,r2);ru=ru-np.polyval(np.polyfit(xu,ru,6),xu)
    Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);A=np.abs(np.fft.rfft(ru*np.hanning(N)));k=(Fa>1)&(Fa<40)
    ax[2].plot(Fa[k],A[k]/A[k].max(),label=f'sr1 B[{lo},4]')
ax[2].set(xlabel='F (T)',ylabel='|FFT|',title='SdH FFT (sr1)');ax[2].legend();ax[2].set_xlim(0,40)
fig.suptitle('Snake hole leg (file 36, n=-8e12, Si=+50V, 200uV) — B7 alive');plt.tight_layout()
fig.savefig('hera_scratch/snake_hole.png',dpi=110);print('saved')
