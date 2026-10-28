import numpy as np,json,os
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
F='36'
m=json.load(open(f'data/{F}/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
fn=f'data/{F}/data.tsv.gz' if os.path.exists(f'data/{F}/data.tsv.gz') else f'data/{F}/data.tsv'
d=np.loadtxt(fn);B=d[:,ci['magnet_mag']];I_bias=5e-9
I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
print('drain(B7) I over hole leg: med %.2f min %.2f max %.2f nA (%d pts)'%(np.median(I)*1e9,I.min()*1e9,I.max()*1e9,d.shape[0]))
F_tot=abs(-8e12*1e4)*6.62607e-34/(4*1.602177e-19)
print(f'Luttinger F_tot(n=-8e12)={F_tot:.0f} T (main/BL); ML expected low ~3-6 T')
def spec(col,Blo,Bhi,detr,N=2048):
    sel=(B>=Blo)&(B<=Bhi); x=1/B[sel]; r=d[sel,ci[col]]/I_bias
    o=np.argsort(x);x,r=x[o],r[o]; xu=np.linspace(x.min(),x.max(),N);ru=np.interp(xu,x,r);dx=xu[1]-xu[0]
    ru=(ru-np.polyval(np.polyfit(xu,ru,detr),xu))
    Fa=np.fft.rfftfreq(N,d=dx);A=np.abs(np.fft.rfft(ru*np.hanning(N)));return Fa,A
for col in ['sr1_X','sr2_X','sr3_X']:
    for (lbl,lo,hi) in [('B[0.6,4]',0.6,4.0),('B[1,4]',1.0,4.0)]:
        Fa,A=spec(col,lo,hi,6); k=(Fa>1)&(Fa<60);Fk,Ak=Fa[k],A[k]/A[k].max()
        pk,_=find_peaks(Ak,height=0.3,distance=max(1,int(2/(Fa[1]-Fa[0]))))
        pk=pk[np.argsort(Ak[pk])[::-1]][:4]
        print(f'{col} {lbl}: peaks[T]={sorted(round(p,1) for p in Fk[pk])}')
