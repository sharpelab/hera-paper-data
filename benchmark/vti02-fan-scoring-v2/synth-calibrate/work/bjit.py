import sys, numpy as np
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/live-check')
from load import load
d = load('0824-r4'); B = d['B']; Br = d['g']('magnet_field', 1)
e = Br - B[:, None]
print('cols', [c for c in d['cols'] if 'magnet' in c])
np.set_printoptions(linewidth=200, precision=4, suppress=True)
print('row mean err (mT):', (e.mean(1) * 1e3))
print('row std within row (mT):', (e.std(1) * 1e3))
print('B', B)
