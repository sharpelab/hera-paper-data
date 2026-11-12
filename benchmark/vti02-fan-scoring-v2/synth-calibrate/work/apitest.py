import sys, time, numpy as np
sys.path.insert(0, '..')
import vti02_sim as vs
rng = np.random.default_rng(0)
n = np.linspace(1.2, 3.05, 57)
grids = {
 '1/B 8->1 x101': 1 / np.linspace(1 / 8, 1, 101),
 'B-uniform 0.4->4 x451': np.linspace(0.4, 4, 451),
 'from 0 T 0->10 x200': np.linspace(0, 10, 200),
 'stitched 1/B 1-3 + B 3-10': np.r_[1 / np.linspace(1, 1 / 3, 80), np.linspace(3.1, 10, 60)],
}
for k, B in grids.items():
    t = time.time()
    R, Rc = vs.simulate(B, n, 10e-9, 0.3, 100e-6, rng, return_clean=True)
    R2 = vs.simulate(B, n, 10e-9, 0.3, 100e-6, rng, vs.observed_tones, delay_s=1.2)
    print(f'{k:28s} {time.time()-t:5.1f}s  shape {R.shape}  R range [{np.nanmin(Rc):.1f}, {np.nanmax(Rc):.1f}]  finite {np.isfinite(R).all() and np.isfinite(R2).all()}')
# wide n range incl low n and high n
B = 1 / np.linspace(1 / 10, 1 / 0.5, 120)
for nn in ([0.3, 0.6, 0.9], [4.0, 5.0, 5.9]):
    R = vs.simulate(B, np.array(nn), 10e-9, 0.1, 1e-3, rng)
    print(nn, 'ok', np.round(np.percentile(R, [1, 50, 99]), 1))
# clipping / quantization
R = vs.simulate(1 / np.linspace(0.1, 1, 50), n, 50e-9, 0.1, 5e-6, rng)
print('clip at 5uV/50nA: max R', R.max().round(1), '= 1.092*sens/I', 1.092 * 5e-6 / 50e-9)
R = vs.simulate(1 / np.linspace(0.1, 1, 50), n[:3], 10e-9, 0.1, 1e-3, rng)
print('LSB 1mV -> ohm grid', vs.lsb(1e-3) / 10e-9, 'unique steps', np.unique(np.round(np.diff(np.sort(R.ravel())) / (vs.lsb(1e-3) / 10e-9), 3))[:5])
try:
    vs.simulate(B, np.array([-1.0]), 10e-9, 0.3, 1e-4, rng)
except ValueError as e:
    print('negative n ->', e)
