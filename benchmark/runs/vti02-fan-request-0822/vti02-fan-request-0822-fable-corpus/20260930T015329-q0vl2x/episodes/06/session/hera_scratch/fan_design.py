"""Landau-fan design (investigation step 4): model F(n)/m*(n) table over the
electron-side window, run-5 gate voltages, Nyquist/deltaF/cost numbers, and a
low-B onset re-check on run 6."""
import sys, json
import numpy as np
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_onset, SdhOnsetError, luttinger_frequency)

sys.path.insert(0, '/home/hera/measurement_env/hera/models/tetralayer_fs_count')
import fs_count_b0 as fs

cal = json.load(open('hera_scratch/cal_run5.json'))
from sharpelab_nb.gates import calc_gate_voltages

# ---- model F(n) table over candidate window (electron side) ----
print('n(e12)   F_L     ABAB orbits (F, m*)                 ABCA (F, m*)')
for n12 in [1.0, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.27]:
    n = n12 * 1e12
    FL = luttinger_frequency(n * 1e4)  # m^-2
    _, orb = fs.abab_fs(n)
    ms = fs.abab_mstar(n)
    ab = '  '.join(f'{F:5.1f}T({m:0.3f})' for F, m in ms)
    try:
        Ft, ma = fs.abca_mstar(n)
        ac = f'{Ft:5.1f}T({ma:0.3f})'
    except Exception as e:
        ac = f'ERR {e}'
    print(f'{n12:5.2f}  {FL:6.1f}   {ab:36s}  {ac}')

# ---- gate voltages at the window ends (run-5 cal, D=0) ----
for n12 in [1.2, 3.2, 3.27]:
    vt, vb = calc_gate_voltages(np.array([n12 * 1e12]), np.array([0.0]),
                                cal['c_tg'], cal['c_bg'],
                                cal['n_offset'] * 1e12, cal['D_offset'])
    print(f'n={n12:+.2f}e12 D=0 -> Vtg={vt[0]:+.4f}  Vbg={vb[0]:+.4f}')

# ---- design numbers ----
n_max = 3.27e12
FL_max = luttinger_frequency(n_max * 1e4)
d_invB_2 = 1 / (2 * FL_max)
d_invB_3 = 1 / (3 * FL_max)
print(f'\nF_L(n_max)={FL_max:.1f} T; d(1/B): 1/2={d_invB_2:.5f}, 1/3={d_invB_3:.5f} 1/T')
for B_lo in (0.5, 0.6, 0.7):
    span = 1 / B_lo - 1 / 10.0
    for d in (0.010, d_invB_2):
        print(f'B_lo={B_lo}: span={span:.3f} -> N_B={int(np.ceil(span/d))+1} at d(1/B)={d:.4f}')
    # partner 5-period floor: minimum f resolvable with 5 periods
    print(f'  5-period floor: f >= {5/span:.2f} T; deltaF(full record)={1/span:.2f} T')
# n-axis ray Nyquist at B_lo
eh = 2.418e10  # e/h in cm^-2 / T
for B_lo in (0.5, 0.6, 0.7):
    dn_ray = 4 * eh * B_lo
    print(f'B_lo={B_lo}: ray spacing dn={dn_ray:.2e} cm^-2 -> grid dn <= {dn_ray/2:.2e}')

# ---- timing calibration from this session ----
from datetime import datetime
for rid, shape in [(5, (63, 66)), (6, (921, 1)), (7, (486, 1))]:
    md = json.load(open(f'data/{rid}/metadata.json'))
    t0, t1 = md.get('start_time'), md.get('end_time')
    print(f'run {rid}: start {t0}  end {t1}  shape {shape}')

# ---- run 6 low-B onset re-check (b_lo down to 0.1) ----
run = open_run('data/6')
chs = resolve_channels(run.meta); cur = current_channel(chs)
volt = [c for c in chs if not c.is_current and c.cid == 'sr1'][0]
B = run.col('magnet_field')
R = np.abs((run.col(volt.col) / volt.gain) / (run.col(cur.col) / cur.gain))
o = np.argsort(B); B, R = B[o], R[o]
try:
    on = sdh_onset(R, B, b_lo=0.1, r_full_scale=50e-6 / 9.9e-9)
    print(on.summary())
except SdhOnsetError as e:
    print('low-B recheck:', e)
