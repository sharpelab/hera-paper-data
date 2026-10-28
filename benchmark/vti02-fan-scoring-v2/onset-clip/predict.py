"""Onset predictions from the parametric Dingle envelopes.
SNR model (same as sdh_onset's tracker): SNR(u) = A(u) / sigma_A, sigma_A = 0.751 * sigma_pt * sqrt(du / sigma_u),
sigma_u = 3 periods FWHM / 2.355 / F; onset where SNR = 5. sigma_pt scales as 1/(I sqrt(tau)) (white, 24 dB).
Validation: (1) heavy-tone onsets in the 0822-r8 / 0825-r8 fans at their own settings vs the tracker onsets;
(2) held out: 0821-r5 light onset (10 nA, 0.1 s, 24 mT steps, record to 0.70 T; tracker 1.41 T) predicted from the 0825-r8 fits."""
import csv, pickle, numpy as np, json
from common import ALPHA, mass
from pfit import RT
P = [r for r in csv.DictReader(open('pfit.csv')) if r['Te'] == '1.2']
E = {(r['rec'], int(r['col']), r['tone']): r for r in csv.DictReader(open('envelopes.csv'))}
f = float
def sig_A(sig_pt, du, F): return 0.751 * sig_pt * np.sqrt(du / (3 / 2.355 / F))
def onset_u(amp0, s, u0, m, sA, Te=1.2, thr=5.0, umax=6.0):
    u = np.linspace(0.05, umax, 6000); A = amp0 * np.exp(s * (u - u0)) * RT(m, Te, u)
    below = np.where((A < thr * sA) & (u > u0 * 0.5))[0]
    return u[below[0]] if below.size else umax
def good(r, t): return f(r[f'sse_{t}']) < 0.8 and f(r[f'A0_{t}']) > 0 and f(r[f's_{t}']) < 0
out = []
REF = dict(I=49.5, tau=0.3, du=(1/1.0 - 1/8.0) / 100)      # 08-25 r8 reference fan
for r in P:
    if r['rec'] not in ('0825-r8', '0822-r8'): continue
    j = int(r['col']); n = f(r['n'])
    e = E[(r['rec'], j, 'heavy')]; sig_rec = f(e['sigma']); du_rec = f(e['du_med']); I_rec = f(r['I_nA']); tau_rec = f(r['tau'])
    row = dict(rec=r['rec'], col=j, n=n)
    for t in ('light', 'heavy'):
        if not good(r, t): continue
        F = f(r[f'F_{t}']); s = f(r[f's_{t}']); a0 = f(r[f'A0_{t}']); u0 = f(r['u0']); m = f(r[f'm_{t}'])
        # own settings
        row[f'{t}_own'] = 1 / onset_u(a0, s, u0, m, sig_A(sig_rec, du_rec, F))
        for lab, I, tau in (('ref50_0.3', 49.5, 0.3), ('10_0.3', 10, 0.3), ('10_0.1', 10, 0.1)):
            sp = sig_rec * (I_rec / I) * np.sqrt(tau_rec / tau)
            row[f'{t}_{lab}'] = 1 / onset_u(a0, s, u0, m, sig_A(sp, REF['du'], F))
            row[f'{t}_{lab}_x3'] = 1 / onset_u(a0, s, u0, m, 3 * sig_A(sp, REF['du'], F))   # floor 3x white
        row[f's_{t}'] = s
        row[f'{t}_trk'] = f(E[(r['rec'], j, t)]['onset_b']) if E[(r['rec'], j, t)]['onset_b'] else np.nan
        row[f'{t}_trk_cens'] = E[(r['rec'], j, t)]['censored']
    out.append(row)
json.dump(out, open('predict.json', 'w'), indent=0, default=float)
# validation 1: heavy own-settings prediction vs tracker
for rec in ('0825-r8', '0822-r8'):
    a = [(x['heavy_own'], x['heavy_trk'], x['heavy_trk_cens']) for x in out if x['rec'] == rec and 'heavy_own' in x]
    unc = np.array([(p, t) for p, t, c in a if c == 'False'])
    cen = np.array([p for p, t, c in a if c == 'True'])
    print(f"{rec} heavy: uncensored N={len(unc)} pred med {np.median(unc[:,0]):.2f} vs trk med {np.median(unc[:,1]):.2f}; "
          f"median |log ratio| {np.median(np.abs(np.log(unc[:,0]/unc[:,1]))):.2f}; censored N={cen.size}, pred med {np.median(cen) if cen.size else np.nan:.2f} (trk <= ~1.19)")
# validation 2: held-out 0821-r5 light
x = [o for o in out if o['rec'] == '0825-r8' and 'light_own' in o and abs(o['n'] - 2.77) < 0.15]
e = E[('0821-r5', 0, 'light')]
sig21 = f(e['sigma']); 
Bs = np.arange(0.696, 1.6, 0.024); du21 = 0.024 / 1.0**2   # local du at 1 T
for o in x:
    r = next(p for p in P if p['rec'] == '0825-r8' and int(p['col']) == o['col'])
    # amplitude in Ohm is a device property at fixed n and T; 0821 n-scale differs (0.92) but column matched on actual n
    F = f(r['F_light']); s = f(r['s_light']); a0 = f(r['A0_light']); u0 = f(r['u0']); m = f(r['m_light'])
    for B in (1.0, 1.2, 1.4):
        pass
    uon = [onset_u(a0, s, u0, m, sig_A(sig21, 0.024 * (1 / Bx) ** 2, F)) for Bx in (1.0, 1.2, 1.4)]
    print(f"held-out 0821-r5 light (tracker 1.41 T, uncensored): from 0825 col n={o['n']:.2f}: predicted onset {1/np.mean(uon):.2f} T (sigma_pt 0821 = {sig21:.2f} Ohm)")
# summaries of light onsets
for rec in ('0825-r8', '0822-r8'):
    for k in ('light_own', 'light_ref50_0.3', 'light_ref50_0.3_x3', 'light_10_0.3', 'light_10_0.1', 'heavy_own', 'heavy_ref50_0.3', 'heavy_10_0.1'):
        v = np.array([o[k] for o in out if o['rec'] == rec and k in o and o['n'] >= 1.8])
        print(f"{rec} {k:20s} n>=1.8: N={v.size} median {np.median(v):.2f} T  IQR [{np.percentile(v,25):.2f}, {np.percentile(v,75):.2f}]")
