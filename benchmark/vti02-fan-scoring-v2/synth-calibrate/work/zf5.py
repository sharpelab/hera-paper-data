import json, gzip, io, numpy as np
p='/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-08-25-vti-02-session/data/5'
m=json.load(open(p+'/metadata.json')); cols=m['columns']; print(m['comments'])
X=np.loadtxt(io.StringIO(gzip.decompress(open(p+'/data.tsv.gz','rb').read()).decode()),delimiter='\t')
g=lambda c: X[:,cols.index(c)]
I=g('sr0_X')/m['measurement_config']['sr0_gain']; R=g('sr1_X')/I
vt=g('k_2400_tg_volt'); vb=0*vt; B=g('magnet_field')
n=1.570*(vt-0.0203)+1.307*vb
print('vb',np.unique(vb.round(3)))
for Bv in np.unique(B.round(2)):
    s=np.abs(B-Bv)<0.01
    out=[]
    for nn in (1.0,1.5,2.0,2.5,3.0):
        k=s&(np.abs(n-nn)<0.05)
        out.append(f'{np.median(R[k]):7.1f}' if k.sum() else '   -   ')
    print(f'B={Bv:5.2f}', ' '.join(out))
