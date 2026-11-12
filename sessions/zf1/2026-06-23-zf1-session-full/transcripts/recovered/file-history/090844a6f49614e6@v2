import sys, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from hera.analysis import open_run

THRESH = 2.0   # mK/min: "practical settle" = rolling slope below this
WIN = 75.0     # s, trailing window for the slope fit

def rolling_settle(rid):
    r = open_run(f'data/{rid}')
    t = r.col('time'); t = t - t[0]
    T = r.col('T')*1e3
    hv = r.col_at(r.col_indices('heater_volt')[0])[0]
    slope = np.full(len(t), np.nan)   # mK/min
    for i in range(len(t)):
        m = (t >= t[i]-WIN) & (t <= t[i])
        if m.sum() >= 5:
            a = np.polyfit(t[m], T[m], 1)[0]   # mK/s
            slope[i] = a*60.0
    # first time |slope| stays below THRESH for >=2 consecutive points
    t_settle = np.nan
    below = np.abs(slope) < THRESH
    for i in range(1, len(t)):
        if below[i] and below[i-1] and t[i] > WIN:
            t_settle = t[i]; break
    end_slope = np.nanmedian(slope[-3:])
    return dict(rid=rid, hv=hv, T0=T[0], Tend=T[-1], t_settle=t_settle, end_slope=end_slope, t=t, T=T, slope=slope)

rids = [int(x) for x in sys.argv[1:]]
res = [rolling_settle(r) for r in rids]
print(f"{'run':>3}{'V':>4}{'T0':>7}{'Tend':>7}{'settle(s)':>11}{'end dT/dt(mK/min)':>19}")
for d in res:
    ss = f"{d['t_settle']:.0f}" if np.isfinite(d['t_settle']) else f">{d['t'][-1]:.0f}"
    print(f"{d['rid']:>3}{d['hv']:>4.0f}{d['T0']:>7.1f}{d['Tend']:>7.1f}{ss:>11}{d['end_slope']:>19.1f}")
fig, ax = plt.subplots(1,2,figsize=(13,5))
for d in res:
    ax[0].plot(d['t'], d['T'], '.-', ms=2, label=f"{d['hv']:.0f}V")
    ax[1].plot(d['t'], np.abs(d['slope']), '-', label=f"{d['hv']:.0f}V")
ax[1].axhline(THRESH, color='r', ls=':', label=f'{THRESH} mK/min')
ax[0].set(xlabel='t since step (s)', ylabel='Probe1 T (mK)', title='settle traces'); ax[0].legend(fontsize=7)
ax[1].set(xlabel='t since step (s)', ylabel='|dT/dt| (mK/min)', title='rolling slope', yscale='log'); ax[1].legend(fontsize=7)
for a in ax: a.grid(alpha=.3)
plt.tight_layout(); plt.savefig('hera_scratch/settle2.png', dpi=120); print('saved hera_scratch/settle2.png')
