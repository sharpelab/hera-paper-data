import numpy as np, glob, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from hera.analysis import open_run

Vdc = np.linspace(-5,5,25); Idc = Vdc/1e8*1e9
rows = []
for d in sorted(glob.glob('data/*'), key=lambda x: int(os.path.basename(x)) if os.path.basename(x).isdigit() else -1):
    rid = os.path.basename(d)
    if not rid.isdigit() or int(rid) < 14: continue
    try:
        r = open_run(d)
        if r.recipe != 'temperature-dependence': continue
        T = np.nanmean(r.col('T'))*1e3
        hvi = r.col_indices('heater_volt')
        heater_on = bool(hvi) and abs(r.col_at(hvi[0])[0]) > 0.01
        dVdI = (r.col('sr830_3_X')/100.0)/1e-9
        zb = dVdI[np.argmin(np.abs(Idc))]
        Rn = np.median(dVdI[np.abs(Idc) > 40])
        depth = Rn - zb
        thr = 0.5*Rn
        p = Idc>=0; n = Idc<=0
        icp = Idc[p][np.argsort(Idc[p])][np.argmax(dVdI[p][np.argsort(Idc[p])]>thr)] if (dVdI[p]>thr).any() else 0.0
        icn = Idc[n][np.argsort(-Idc[n])][np.argmax(dVdI[n][np.argsort(-Idc[n])]>thr)] if (dVdI[n]>thr).any() else 0.0
        rows.append((T, zb, depth, (abs(icp)+abs(icn))/2, Rn, heater_on, int(rid)))
    except Exception:
        pass
rows.sort()
T = np.array([r[0] for r in rows]); depth = np.array([r[2] for r in rows])
Ic = np.array([r[3] for r in rows]); hon = np.array([r[5] for r in rows])

# onset Tc: highest T where dip depth still clearly > 0 (use a 3-Ohm floor), and lowest T where depth ~ 0
sc = depth > 3
Tc_lo = T[sc].max() if sc.any() else np.nan       # highest T with a clear dip
Tc_hi = T[~sc].min() if (~sc).any() else np.nan    # lowest T with no dip
print(f"onset Tc bracket: dip present up to {Tc_lo:.0f} mK, gone by {Tc_hi:.0f} mK -> Tc_onset ~ {(Tc_lo+Tc_hi)/2/1000:.2f} K")
print(f"{'T(mK)':>7}{'depth':>7}{'Ic':>6}{'heater':>8}{'run':>5}")
for r in rows:
    print(f"{r[0]:7.1f}{r[2]:7.1f}{r[3]:6.0f}{'ON' if r[5] else 'off':>8}{r[6]:5d}")

fig, ax = plt.subplots(1, 2, figsize=(13, 5))
ax[0].plot(T[~hon], depth[~hon], 'o-', color='tab:blue', label='passive cooldown (heater OFF, clean)')
ax[0].plot(T[hon], depth[hon], 's', color='tab:orange', alpha=0.8, label='heater-on ladder (e-T/remanence scatter)')
ax[0].axhspan(0, 3, color='gray', alpha=0.12)
if np.isfinite(Tc_lo) and np.isfinite(Tc_hi):
    ax[0].axvspan(Tc_lo, Tc_hi, color='red', alpha=0.12, label=f'onset Tc ~{(Tc_lo+Tc_hi)/2:.0f} mK')
ax[0].set(xlabel='T (mK)', ylabel='dip depth = Rn - dV/dI(0)  (Ohm)', title='SC dip depth vs T (order-parameter-like)')
ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)

# representative dV/dI traces collapsing
import matplotlib.cm as cm
reps = [23, 17, 16, 27, 26, 24, 30, 29]  # base ... 328mK
for rid in reps:
    try:
        r = open_run(f'data/{rid}'); Tt = np.nanmean(r.col('T'))*1e3
        dv = (r.col('sr830_3_X')/100.0)/1e-9
        ax[1].plot(Idc, dv, '-', label=f'{Tt:.0f} mK')
    except Exception: pass
ax[1].set(xlabel='I_dc (nA)', ylabel='dV/dI (Ohm)', title='supercurrent dip collapsing with T'); ax[1].legend(fontsize=7, ncol=2); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig('hera_scratch/tdep_full.png', dpi=120); print('saved hera_scratch/tdep_full.png')
