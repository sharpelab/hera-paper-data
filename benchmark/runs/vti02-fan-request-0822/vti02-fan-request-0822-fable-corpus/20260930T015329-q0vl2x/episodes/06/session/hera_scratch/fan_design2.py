"""Fan design v2 — correct units (m^-2), MR/dynamic-range from runs 6/7,
timing calibration."""
import sys, json
import numpy as np
from hera.analysis import (open_run, resolve_channels, current_channel,
                           luttinger_frequency)
sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count')
import fs_count_b0 as fs
from sharpelab_nb.gates import calc_gate_voltages

cal = json.load(open('hera_scratch/cal_run5.json'))

print('n(e12)   F_L      ABAB (F, m*)                          ABCA (F, m*)')
for n12 in [1.0, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.27]:
    n = n12 * 1e16  # m^-2
    FL = luttinger_frequency(n)
    ms = fs.abab_mstar(n)
    ab = '  '.join(f'{F:5.1f}T({m:0.3f})' for F, m in ms)
    Ft, ma = fs.abca_mstar(n)
    print(f'{n12:5.2f}  {FL:6.1f}   {ab:38s}  {Ft:5.1f}T({ma:0.3f})')

print()
for n12 in [1.2, 1.6, 3.2, 3.27]:
    vt, vb = calc_gate_voltages(np.array([n12 * 1e16]), np.array([0.0]),
                                cal['c_tg'], cal['c_bg'],
                                cal['n_offset'] * 1e16, cal['D_offset'])
    print(f'n={n12:+.2f}e12 D=0 -> Vtg={vt[0]:+.4f}  Vbg={vb[0]:+.4f}')

# ---- MR / dynamic range from runs 6 & 7 ----
for rid in (6, 7):
    run = open_run(f'data/{rid}')
    chs = resolve_channels(run.meta); cur = current_channel(chs)
    volt = [c for c in chs if not c.is_current and c.cid == 'sr1'][0]
    B = run.col('magnet_field')
    X = run.col(volt.col)
    I = np.abs(run.col(cur.col) / cur.gain)
    R = np.abs(X / volt.gain / I)
    frac = np.abs(X) / 50e-6
    print(f'run {rid}: R min/med/max = {R.min():.0f}/{np.median(R):.0f}/{R.max():.0f} Ohm; '
          f'|X|/sens max = {frac.max():.2f} at B={B[np.argmax(frac)]:.2f} T; '
          f'I min = {I.min()*1e9:.2f} nA; MR factor R(max)/R(B~0) = {R.max()/np.median(R[B<0.2]):.1f}')

# ---- timing ----
# run 5 gatemap: 63 rows x 66 pts, fast_delay? from cell; wall 4873 s
print('\nrun5: 4873 s / 4158 pts = %.2f s/pt (incl. row turnaround)' % (4873/4158.))
print('run6: 7222 s, 921 pts, 10 T traverse (bare 4380 s) -> per-pt overhead %.2f s' % ((7222-4380)/921.))
print('run7: 5741 s, 486 pts, 9.7 T traverse (bare 4249 s) -> per-pt overhead %.2f s' % ((5741-4249)/486.))

# ---- fan cost table ----
tau = 0.3
for B_lo, n_lo12, Nn in [(0.5, 1.2, 87), (0.6, 1.2, 73), (0.6, 1.6, 59), (0.7, 1.6, 51)]:
    span = 1/B_lo - 0.1
    NB = int(np.ceil(span / 0.01)) + 1
    # per-point: fast_delay 4*tau + reads ~0.24 (calibrate: file20 precedent 1.44 s/pt)
    t_pt = 1.44
    t_grid = NB * Nn * t_pt
    t_ramp = (10 - B_lo) / 0.137 * 60
    t_turn = NB * (3 + 1.0)   # settle 3 s + slow_delay/flyback
    tot = t_grid + t_ramp + t_turn
    print(f'B_lo={B_lo} n_lo={n_lo12} NB={NB} Nn={Nn}: grid {t_grid/3600:.2f} h + ramp {t_ramp/3600:.2f} h '
          f'+ turn {t_turn/3600:.2f} h = {tot/3600:.2f} h  (+10%% -> {tot*1.1/3600:.2f} h)')
