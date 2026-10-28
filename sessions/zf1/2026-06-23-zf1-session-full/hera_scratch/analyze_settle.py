import sys, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from hera.analysis import open_run

def settle(rid):
    r = open_run(f'data/{rid}')
    t = r.col('time'); t = t - t[0]
    T = r.col('T')*1e3                       # mK (Probe1)
    hv = r.col_at(r.col_indices('heater_volt')[0])[0]
    tags = ' '.join(r.tags) if hasattr(r,'tags') else ''
    Tf = np.median(T[int(0.85*len(T)):])     # asymptote = last 15%
    T0 = T[0]; dT = Tf - T0
    # settle within +/-2% of dT (min 2 mK band)
    band = max(0.02*abs(dT), 2.0)
    inside = np.abs(T - Tf) <= band
    # last time it ENTERS the band for good
    t_settle = np.nan
    for i in range(len(T)):
        if inside[i:].all():
            t_settle = t[i]; break
    # exponential fit T = Tf - dT*exp(-t/tau)
    tau = np.nan
    try:
        p,_ = curve_fit(lambda x,Tf_,dT_,tau_: Tf_-dT_*np.exp(-x/tau_), t, T,
                        p0=[Tf, dT, 120], maxfev=10000)
        tau = p[2]
    except Exception: pass
    return dict(rid=rid, hv=hv, T0=T0, Tf=Tf, dT=dT, t_settle=t_settle, tau=tau, t=t, T=T, tag=tags)

rids = [int(x) for x in sys.argv[1:]]
res = [settle(r) for r in rids]
fig, ax = plt.subplots(figsize=(8,5))
print(f"{'run':>3}{'heaterV':>8}{'T0(mK)':>8}{'Tf(mK)':>8}{'dT':>7}{'t_settle(s)':>12}{'tau(s)':>8}")
for d in res:
    ax.plot(d['t'], d['T'], '.-', ms=3, label=f"run{d['rid']} {d['hv']:.0f}V  ts={d['t_settle']:.0f}s")
    if np.isfinite(d['t_settle']): ax.axvline(d['t_settle'], ls=':', lw=.7)
    print(f"{d['rid']:>3}{d['hv']:>8.1f}{d['T0']:>8.1f}{d['Tf']:>8.1f}{d['dT']:>7.1f}{d['t_settle']:>12.0f}{d['tau']:>8.0f}")
ax.set(xlabel='time since step (s)', ylabel='Probe1 T (mK)', title='heater settle traces'); ax.legend(fontsize=7); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig('hera_scratch/settle.png', dpi=120); print('saved hera_scratch/settle.png')
