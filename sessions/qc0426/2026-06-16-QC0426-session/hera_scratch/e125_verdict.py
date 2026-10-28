import numpy as np,json,os
from scipy.signal import find_peaks
F='38';m=json.load(open(f'data/{F}/metadata.json'));ci={c:i for i,c in enumerate(m['columns'])}
fn=f'data/{F}/data.tsv.gz' if os.path.exists(f'data/{F}/data.tsv.gz') else f'data/{F}/data.tsv'
d=np.loadtxt(fn);B=d[:,ci['magnet_mag']];I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
print(f'file 38 COMPLETE: {d.shape[0]} pts, B {B[0]:.2f}->{B[-1]:.2f}, interrupted={m["interrupted"]}')
print(f'drain(B7) I med {np.median(I)*1e9:.2f} min {I.min()*1e9:.2f} max {I.max()*1e9:.2f} nA')
F_lutt=abs(8e12*1e4)*6.62607e-34/(4*1.602177e-19)
def fft(col,Blo,Bhi,N=8192):
    sel=(B>=Blo)&(B<=Bhi);x=1/B[sel];r=d[sel,ci[col]]/5e-9;o=np.argsort(x);x,r=x[o],r[o]
    xu=np.linspace(x.min(),x.max(),N);ru=np.interp(xu,x,r);ru=ru-np.polyval(np.polyfit(xu,ru,6),xu)
    Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]);A=np.abs(np.fft.rfft(ru*np.hanning(N)));return Fa,A
print(f'Luttinger full-density F_tot(n=+8e12) = {F_lutt:.0f} T')
for col in ['sr1_X','sr2_X','sr3_X']:
    print(f'--- {col}: peaks per window (lo=1/1.5/2 -> 4 T) ---')
    for lo in (1.0,1.5,2.0):
        Fa,A=fft(col,lo,4.0);k=(Fa>3)&(Fa<150);Fk,Ak=Fa[k],A[k]
        pk,_=find_peaks(Ak,height=0.30*Ak.max(),distance=15)
        pk=pk[np.argsort(Ak[pk])[::-1]][:4]
        print(f'   B[{lo},4]: {sorted(round(float(Fk[i]),0) for i in pk)}')
