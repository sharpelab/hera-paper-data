"""Dingle figure: (A) 0825-r8 column n~2.79 (+ 0821-r5 n 2.77, to 0.70 T): local demodulated tone amplitudes vs 1/B with the
parametric Dingle fits, the mass-scaled light hypothesis and the light-tone 5-sigma floors; (B) light/heavy slope ratio vs n;
(C) candidate B_on,low(n)."""
import pickle, csv, json, numpy as np, warnings
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from pfit import design, RT
from common import load_run, ALPHA
warnings.filterwarnings('ignore')
C = dict(light='#2a78d6', heavy='#eb6834', FL='#1baf7a', gray='#6b6a64', ink='#2b2b29')
fits = pickle.load(open('pfit.pkl', 'rb'))
P = {(r['rec'], int(r['col'])): r for r in csv.DictReader(open('pfit.csv')) if r['Te'] == '1.2'}
E = {(r['rec'], int(r['col']), r['tone']): r for r in csv.DictReader(open('envelopes.csv'))}
def demod(u, y, F, periods=1.5):
    su = periods / 2.355 / F; cs = np.arange(u.min() + 2 * su, u.max() - 2 * su, su)
    out = []
    for c in cs:
        g = np.exp(-0.5 * ((u - c) / su) ** 2); m = g > 1e-3
        z = np.sum(y[m] * g[m] * np.exp(-2j * np.pi * F * u[m])); out.append(abs(z) / (0.5 * g[m].sum()))
    return cs, np.array(out)
fig, ax = plt.subplots(1, 3, figsize=(15, 4.8))
a = ax[0]; rec, col = '0825-r8', 48
f = fits[(rec, col, 1.2)]; r = P[(rec, col)]; n = float(r['n'])
m = [float(r[f'm_{t}']) for t in ('light', 'heavy', 'FL', 'light2', 'diff')]
A = design(f['u'], f['F'], f['s'], m, 1.2, f['u0'])
for k, t in enumerate(('light', 'heavy', 'FL')):
    keep = f['coef'].copy(); keep[4 + 2 * k: 6 + 2 * k] = 0          # remove this tone from the model
    y = f['y'] - A @ keep                                             # data minus everything else = this tone + noise
    cs, amp = demod(f['u'], y, f['F'][k])
    X = ALPHA * m[k] * 1.2 * cs
    a.semilogy(cs, amp * np.sinh(X) / X, 'o', ms=4, color=C[t], alpha=0.8, label=f"{t} {f['F'][k]:.1f} T (s = {f['s'][k]:.2f} T)")
    uu = np.linspace(f['u0'], 2.2, 200)
    env = f['amp0'][k] * np.exp(f['s'][k] * (uu - f['u0']))
    a.semilogy(uu[uu <= 1.0], env[uu <= 1.0], '-', color=C[t], lw=2)
    if t == 'light': a.semilogy(uu[uu >= 1.0], env[uu >= 1.0], '--', color=C[t], lw=1.5)
# mass-scaled light hypothesis anchored at u0
ratio = m[0] / m[1]; uu = np.linspace(f['u0'], 2.2, 200)
a.semilogy(uu, f['amp0'][0] * np.exp(ratio * f['s'][1] * (uu - f['u0'])), ':', color=C['gray'], lw=2, label=f'light if τ_q shared (s = {ratio:.2f}·s_heavy)')
# light 5-sigma floors (matched filter, 3 periods): reference operational / reference white / 10 nA 0.1 s
F = f['F'][0]; su = 3 / 2.355 / F; du = 0.00875
sig_op = float(E[(rec, col, 'heavy')]['sigma'])
for lab, sp, ls in (('5σ floor, 50 nA 0.3 s (as measured)', sig_op, '-'), ('5σ floor, 50 nA 0.3 s (white only)', 0.41, '--'),
                    ('5σ floor, 10 nA 0.1 s', np.hypot(2.07, 3.54), '-.')):
    a.axhline(5 * 0.751 * sp * np.sqrt(du / su), color=C['ink'], lw=0.8, ls=ls, label=lab)
# 0821-r5 light envelope, n 2.77, to 0.70 T (different session; same device and pair)
r5 = load_run(21, 5); o = (r5['B'] >= 0.70) & (r5['B'] <= 4.0)
Bs, Rs = r5['B'][o], r5['R'][o]; u5 = 1 / Bs
p = np.polyfit(u5, Rs, 3); y5 = Rs - np.polyval(p, u5)
F5 = float(P[('0821-r5', 0)]['F_light']); cs, amp = demod(u5[::-1], y5[::-1], F5)
a.semilogy(cs, amp, 's', mfc='none', ms=5, color=C['light'], alpha=0.6, label='light, 0821-r5 spot (10 nA 0.1 s)')
a.axvline(1.0, color=C['gray'], lw=0.6); a.text(1.02, 0.12, 'fan edge 1.0 T', fontsize=7, color=C['gray'])
a.set_xlim(0.1, 2.2); a.set_ylim(0.1, 60); a.set_xlabel('1/B (1/T)'); a.set_ylabel('A·sinh X / X  (Ω), T_e = 1.2 K')
a.set_title(f'A. Dingle plot, 08-25 r8 column n = {n:.2f}', fontsize=10, loc='left'); a.legend(fontsize=6.5, loc='lower left', frameon=False)
sec = a.secondary_xaxis('top', functions=(lambda x: 1 / np.maximum(x, 1e-3), lambda x: 1 / np.maximum(x, 1e-3)))
sec.set_xticks([4, 2, 1, 0.75, 0.6, 0.5]); sec.set_xlabel('B (T)', fontsize=8)
# B: slope ratio
b = ax[1]
for rec, mk in (('0825-r8', 'o'), ('0822-r8', 's')):
    L = [r for (rr, _), r in P.items() if rr == rec and float(r['sse_light']) < 0.8 and float(r['sse_heavy']) < 0.8 and float(r['n']) >= 1.5]
    nn = [float(r['n']) for r in L]; q = [float(r['s_light']) / float(r['s_heavy']) for r in L]
    b.plot(nn, q, mk, ms=5, mfc='none' if mk == 's' else C['light'], color=C['light'], label=f'{rec} ({"50" if "25" in rec else "10"} nA)')
nm = np.linspace(1.5, 3.1, 20)
from common import mass
b.plot(nm, [mass(x, 'm_l') / mass(x, 'm_h') for x in nm], '-', color=C['gray'], lw=2, label='model m_l/m_h (shared τ_q)')
b.fill_between(nm, 0.49, 0.70, color=C['gray'], alpha=0.15, label='LK-measured m_l/m_h (08-22)')
b.axhline(1, color=C['ink'], lw=0.6)
b.set_ylim(0, 3); b.set_xlabel('n actual (1e12 cm⁻²)'); b.set_ylabel('s_light / s_heavy'); b.legend(fontsize=7, frameon=False)
b.set_title('B. Light vs heavy Dingle slope, per column', fontsize=10, loc='left')
# C: candidate clips
c = ax[2]; cv = json.load(open('curves.json')); fits_c = json.load(open('curve_fits.json'))
L = [r for r in cv if r['rec'] == '0825-r8']
c.plot([r['n'] for r in L], [r['b_ref_op'] for r in L], 'o', ms=4, color=C['light'], alpha=0.6)
c.plot([r['n'] for r in L], [r['a_model'] for r in L], 'o', ms=4, mfc='none', color=C['gray'], alpha=0.7)
nn = np.linspace(1.8, 3.1, 10)
for key, lab, col, ls in (('0825-r8:a_model', '(a) mass-scaled, model ratio', C['gray'], ':'), ('0825-r8:a_meas_hi', '(a) mass-scaled, LK ratio 0.70', C['gray'], '--'),
                          ('0825-r8:b_ref_white', '(b) Dingle, ref acq, white noise', C['light'], '--'), ('0825-r8:b_ref_op', '(b) Dingle, ref acq, as measured', C['light'], '-'),
                          ('0825-r8:b_10_0.1', '(b) Dingle, 10 nA 0.1 s', C['heavy'], '-')):
    p = fits_c[key]; c.plot(nn, np.polyval(p, nn), ls, color=col, lw=2, label=lab)
c.axhline(1.0, color=C['ink'], lw=1.5, label='(c) observed floor 1.0 T'); c.axhline(0.55, color=C['ink'], lw=0.8, ls=':', label='doc table clip 0.55 T')
c.set_ylim(0.3, 1.3); c.set_xlabel('n actual (1e12 cm⁻²)'); c.set_ylabel('B_on,low (T)'); c.legend(fontsize=7, frameon=False, loc='upper left')
c.set_title('C. Candidate light-tone onset clips', fontsize=10, loc='left')
for x in ax: x.spines[['right']].set_visible(False); x.tick_params(labelsize=8)
fig.tight_layout(); fig.savefig('dingle_onset.png', dpi=150); print('ok')
