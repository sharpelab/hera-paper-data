import numpy as np, glob, os
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def reextract(t, T, thresh=1.0, win=150, sustain=90, t_min=180):
    below=None
    for i in range(len(t)):
        m = (t > t[i]-win) & (t <= t[i])
        if m.sum() < 4: continue
        sl = abs(np.polyfit(t[m], T[m], 1)[0]*60)
        if sl < thresh:
            if below is None: below=t[i]
            elif t[i]-below >= sustain and t[i] > t_min:
                return below
        else:
            below=None
    return np.nan

fig, ax = plt.subplots(1,2,figsize=(13,5))
rows=[]
for f in sorted(glob.glob('hera_scratch/settle_down_*.npz'), key=lambda x:-int(x.split('_')[-1].split('.')[0])):
    d=np.load(f); t=d['t']; T=d['T']; tgt=float(d['target']); st=float(d['settle_t'])
    st2=reextract(t,T)
    rows.append((tgt, T[0], T[-1], st, st2, t[-1]))
    ax[0].plot(t/60, T, '.-', ms=2, label=f"{tgt+1:.0f}->{tgt:.0f}V")
print(f"{'step':>9}{'T0':>7}{'Tf':>7}{'dT':>7}{'settle(cell)':>13}{'settle(reext)':>14}{'rec(min)':>9}")
for tgt,T0,Tf,st,st2,tend in rows:
    s1 = f"{st:.0f}s" if st>0 else "capped"
    s2 = f"{st2:.0f}s" if np.isfinite(st2) else "capped"
    print(f"{tgt+1:.0f}->{tgt:.0f}V {T0:7.1f}{Tf:7.1f}{Tf-T0:7.1f}{s1:>13}{s2:>14}{tend/60:9.1f}")
ax[0].set(xlabel='t since step (min)', ylabel='Probe1 T (mK)', title='DOWN ladder (cooling) settle traces'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
# settle vs level: down (cooling)
lv=[r[0]+0.5 for r in rows]   # mid-level of the step (e.g. 6->5 -> 5.5)
sd=[r[3] for r in rows]
ax[1].plot(lv, sd, 'o-', label='DOWN (cooling), adaptive')
ax[1].set(xlabel='heater step mid-level (V)', ylabel='settle time (s)', title='down-settle vs level'); ax[1].grid(alpha=.3); ax[1].legend()
plt.tight_layout(); plt.savefig('hera_scratch/down.png', dpi=120); print('saved hera_scratch/down.png')
