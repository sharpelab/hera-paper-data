import numpy as np
from hera.analysis import open_run, resolve_channels, current_channel
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, nnom, bwin) in enumerate([(6, 3.2, (0.9, 7.6)), (7, -1.2, (0.9, 8.4))]):
    r = open_run(f'data/{rid}')
    ch = resolve_channels(r.meta); cur = current_channel(ch)
    I = r.col_at(cur.idx)/cur.gain
    vc = [c for c in ch if not c.is_current][0]
    R = np.abs((r.col_at(vc.idx)/vc.gain)/I); B = r.col('magnet_field')
    o = np.argsort(B); B, R = B[o], R[o]
    m = (B >= bwin[0]) & (B <= bwin[1]); Bw, Rw = B[m], R[m]
    Rs = gaussian_filter1d(Rw, 2.0)
    mins, _ = find_peaks(-Rs, prominence=0.10*(Rs.max()-Rs.min()))
    Bmin = Bw[mins]
    ax[0,k].plot(Bw, Rw, lw=0.6); ax[0,k].plot(Bw, Rs, lw=1.0)
    ax[0,k].plot(Bmin, Rs[mins], 'rv'); ax[0,k].set_title(f'run {rid} (n_nom={nnom:+.1f}e12) minima in [{bwin[0]},{bwin[1]}] T')
    ax[0,k].set_xlabel('B (T)')
    inv = 1/Bmin
    print(f'--- run {rid}: {len(Bmin)} minima at B = ' + ', '.join(f'{b:.3f}' for b in Bmin))
    print('    1/B = ' + ', '.join(f'{x:.4f}' for x in inv))
    print('    d(1/B) = ' + ', '.join(f'{d:.4f}' for d in np.diff(inv)))
    # index: assume consecutive integers, fit 1/B = (j + phi)/F
    j = np.arange(len(inv))[::-1]   # increasing index toward low B
    cf = np.polyfit(j, inv, 1)
    F = 1/cf[0]; resid = inv - np.polyval(cf, j)
    print(f'    consecutive-index fit: F = {F:.2f} T, intercept phi = {cf[1]/cf[0]:.2f}, rms resid {np.std(resid):.4f} 1/T '
          f'({100*np.std(resid)/abs(cf[0]):.1f}% of a period)')
    ax[1,k].plot(j, inv, 'o-'); ax[1,k].plot(j, np.polyval(cf,j), 'k--')
    ax[1,k].set_xlabel('assigned index'); ax[1,k].set_ylabel('1/B_min'); ax[1,k].set_title(f'run {rid} index fan: F={F:.2f} T')
    # what ratio nu/index would make nominal n consistent?
    for nu in (1,2,4):
        n_impl = nu*1.602176634e-19*F/6.62607015e-34/1e16
        print(f'    if the period is dnu={nu}: implied |n| = {n_impl:.3f}e12 (nominal {abs(nnom):.2f}) -> lever ratio {abs(nnom)/n_impl:.2f}')
plt.tight_layout(); plt.savefig('hera_scratch/index67.png', dpi=110); print('saved')
