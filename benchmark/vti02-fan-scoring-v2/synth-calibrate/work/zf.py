import json, gzip, io, numpy as np
p='/home/zack/sharpelab/measurement-env/hera/docs/notes/2026-08-25-vti-02-session/data/4'
m=json.load(open(p+'/metadata.json')); cols=m['columns']; print(cols); print(m['measurement_config'])
X=np.loadtxt(io.StringIO(gzip.decompress(open(p+'/data.tsv.gz','rb').read()).decode()),delimiter='\t')
g=lambda c: X[:,cols.index(c)]
I=g('sr0_X')/m['measurement_config']['sr0_gain']; R=g('sr1_X')/I
vt=g('k_2400_tg_volt'); vb=g('k_2400_bg_volt')
n=1.570*(vt-0.0203)+1.307*vb
# D ~ proportional to (vb*c_bg - vt*c_tg); D=0: vb = vt/0.832
dD=vb-vt/0.832
for nn in np.arange(-1,3.3,0.25):
    s=(np.abs(n-nn)<0.08)&(np.abs(dD)<0.15)
    if s.sum(): print(f'n={nn:.2f} R0={np.median(R[s]):.1f} ohm  (N={s.sum()}, range {R[s].min():.1f}-{R[s].max():.1f})')
