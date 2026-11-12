import numpy as np
from hera.analysis import open_run
r = open_run('data/6')
B = r.col('magnet_field'); I = r.col('sr0_X')/(-1e6); R = (r.col('sr1_X'))/I
o = np.argsort(B); B, R, V = B[o], R[o], r.col('sr1_X')[o]
for lo, hi in [(1.0,2.0),(4.0,5.0),(8.0,9.0),(9.0,10.0)]:
    m = (B>=lo)&(B<hi)
    d = np.diff(R[m]); dv = np.diff(V[m])
    print(f'B {lo}-{hi}: R med {np.median(R[m]):7.1f} Ohm  pt-to-pt std(dR)/sqrt2 = {np.std(d)/np.sqrt(2):6.2f} Ohm '
          f'({np.std(dv)/np.sqrt(2)*1e9:5.1f} nV;  {np.std(dv)/np.sqrt(2)/50e-6*100:.3f} % of 50uV FS)')
r7 = open_run('data/7'); B7=r7.col('magnet_field'); I7=r7.col('sr0_X')/(-1e6); R7=r7.col('sr1_X')/I7
o7=np.argsort(B7); B7,R7=B7[o7],R7[o7]
m=(B7>=9)&(B7<10); print('run7 B9-10: R med %.1f, ptp noise %.2f Ohm'%(np.median(R7[m]), np.std(np.diff(R7[m]))/np.sqrt(2)))
# CNP resistance at B=0 from run 5 along D=0
