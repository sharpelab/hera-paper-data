import numpy as np, json, os
def F_tot(n): return abs(n*1e4)*6.62607e-34/(4*1.602177e-19)
def dom(d, ci, col, Blo, Bhi, N=4096):
    B=d[:,ci['magnet_mag']]; sel=(B>=Blo)&(B<=Bhi); x=1/B[sel]; r=d[sel,ci[col]]/5e-9
    o=np.argsort(x); x,r=x[o],r[o]; xu=np.linspace(x.min(),x.max(),N); ru=np.interp(xu,x,r)
    ru=ru-np.polyval(np.polyfit(xu,ru,6),xu); Fa=np.fft.rfftfreq(N,d=xu[1]-xu[0]); A=np.abs(np.fft.rfft(ru*np.hanning(N)))
    k=(Fa>1)&(Fa<40); return round(float(Fa[k][np.argmax(A[k])]),1)
for F,side,n in [('36','hole',-8e12),('37','electron',8e12)]:
    if not os.path.isdir(f'data/{F}'):
        print(f'file {F} missing'); continue
    m=json.load(open(f'data/{F}/metadata.json')); ci={c:i for i,c in enumerate(m['columns'])}
    fn=f'data/{F}/data.tsv.gz' if os.path.exists(f'data/{F}/data.tsv.gz') else f'data/{F}/data.tsv'
    d=np.loadtxt(fn); I=d[:,ci['sr0_X']]/m['measurement_config']['sr0_gain']
    print(f'--- file {F} {side} n={n:.0e} : {d.shape[0]}pts interrupted={m["interrupted"]} ---')
    print(f'  drain(B7) I med {np.median(I)*1e9:.2f} min {I.min()*1e9:.2f} max {I.max()*1e9:.2f} nA ; main F_tot~{F_tot(n):.0f}T')
    for col in ['sr1_X','sr2_X']:
        pk=[dom(d,ci,col,lo,4.0) for lo in (0.6,1.0,1.5,2.0)]
        tag='STABLE' if max(pk)-min(pk)<2 else 'WANDERS->aliasing/artifact'
        print(f'  {col} dom-peak[T] vs window lo=0.6/1/1.5/2: {pk}  {tag}')
