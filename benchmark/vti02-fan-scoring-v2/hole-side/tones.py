"""Per-trace SdH tones on the hole side: peaks over window x background choices, consensus clusters, identities.

Floor: the empirical median |S| over [1.12 F_L, 0.95 Nyquist] (the live-check contrast floor), widened to 4 T above
1.12 F_L when the Nyquist band is narrower.  A peak counts at contrast >= 4.  Identity candidates are the Halder_ABAB
hole tones at the trace's reference density (QH ladder, LL fan or F_L tone; frames.csv) and their low-order
harmonics / combinations; a tone matches within max(0.6 dF, 0.08 F).  Writes tones_raw.csv and tones.csv."""
import sys
import numpy as np, pandas as pd
sys.path.insert(0, '/data/sharpelab/hera-data/vti02-fan-scoring-v2/hole-side')
from load_hole import load_all
from common import spec, model, peaks

# reference |n| (actual) per trace and its source; fans: grader frame (08-24; the LL-fan hole fit agrees to 2 %) / LL hole fit (08-23)
LL_0823_H = (0.935, -0.18)
def n_ref(t):
    if t['id'] == '0822-r7':
        return 0.907, 'own F_L-like tone 9.38 T (heavy/F_L 0.70-0.73 = Halder); QH ladder nu 7,6,5 at 6-8.4 T gives 1.011'
    if t['id'] == '0825-r7-c0':
        return 0.842, 'QH ladder nu 8,7,6 (+-0.010; branch 7,6,5 = 0.720 excluded by the heavy tone and frame)'
    if t['session'] == '0823':
        return abs(LL_0823_H[0] * (t['n_frame'] - LL_0823_H[1])), 'LL fan, hole side (s 0.935, n0 -0.18)'
    return abs(t['n_act_e']), 'grader frame (x0.90); LL fan hole fit and r5 F_L tone agree within 2 %'


WINDOWS = {'0822-r7': [(0.6, 3.0), (0.75, 3.0), (1.0, 3.0), (0.6, 4.5), (0.75, 4.5), (1.0, 4.5)],
           '0825-r7': [(1.5, 4.5), (1.8, 4.5), (1.5, 6.0), (1.8, 6.0)],
           '0824-r5': [(0.51, 4.0), (0.75, 4.0), (1.0, 4.0), (0.51, 6.1), (0.75, 6.1), (1.0, 6.1)],
           '0824-r4': [(0.76, 4.5), (1.0, 4.5), (0.76, 6.1), (1.0, 6.1)],
           '0823-r6': [(1.5, 6.0), (2.0, 6.0), (1.5, 8.1), (2.0, 8.1)]}


def combos(fl, fh, fL):
    c = {'light': fl, 'heavy': fh, 'F_L': fL, '2 heavy': 2 * fh, '3 heavy': 3 * fh, 'heavy-light': fh - fl, '2 light': 2 * fl,
         'F_L+heavy': fL + fh, '2 F_L': 2 * fL, 'heavy+2 light': fh + 2 * fl}
    return {k: v for k, v in c.items() if v > 0.3}


def floor_of(s, fL):
    a = 1.12 * fL; b = 0.95 * s['nyq']
    if b - a < 4.0:
        b = a + 4.0
    k = (s['F'] >= a) & (s['F'] <= min(b, s['F'][-1]))
    return float(np.median(s['S'][k])), (a, b)


if __name__ == '__main__':
    raw, cons = [], []
    for t in load_all():
        key = t['id'].rsplit('-c', 1)[0] if t['session'] != '0822' else t['id']
        n, src = n_ref(t)
        if n < 0.3:
            continue
        fl, fh, fL = model(n)
        fl = 0.0 if np.isnan(fl) else fl
        for lo, hi in WINDOWS[key]:
            for deg in (3, 5):
                s = spec(t['B'], t['R'], max(lo, t['B'].min()), min(hi, t['B'].max()), deg, Fmax=45, dFgrid=0.01)
                if s is None or s['rows'] < 12:
                    continue
                fl0, band = floor_of(s, fL)
                Z = s['S'] / fl0
                fmax = min(0.95 * s['nyq'], 2.2 * fL + 2, 40)
                for f, z in peaks(s['F'], Z, 0.75 * s['dF'], fmax, 4.0, 12):
                    raw.append(dict(trace=t['id'], n_ref=round(n, 3), lo=round(s['lo'], 2), hi=round(s['hi'], 2), deg=deg, dF=round(s['dF'], 3),
                                    nyq=round(s['nyq'], 1), F=round(f, 3), contrast=round(z, 1), amp_ohm=round(float(np.interp(f, s['F'], s['amp'])), 2),
                                    floor_band=f'{band[0]:.1f}-{band[1]:.1f}'))
        r = pd.DataFrame([x for x in raw if x['trace'] == t['id']])
        nch = len(WINDOWS[key]) * 2
        if r.empty:
            cons.append(dict(trace=t['id'], n_frame=round(t['n_frame'], 3), n_grader=round(abs(t['n_act_e']), 3), n_ref=round(n, 3), n_ref_src=src,
                             F=np.nan, tone='none above contrast 4'))
            continue
        # cluster across choices: greedy on contrast, radius 0.6 x the coarsest dF
        rad = 0.6 * r.dF.max(); left = r.sort_values('contrast', ascending=False).copy(); cl = []
        while len(left):
            f0 = left.iloc[0].F; m = (left.F - f0).abs() <= rad
            cl.append(left[m]); left = left[~m]
        for c in cl:
            F = float(c.F.median()); dF = float(c.dF.median())
            tol = max(0.6 * dF, 0.08 * F)
            cand = {k: v for k, v in combos(fl, fh, fL).items() if abs(F - v) <= tol}
            ident = ', '.join(f'{k} ({v:.2f})' for k, v in sorted(cand.items(), key=lambda kv: abs(F - kv[1]))) or 'unassigned'
            lowF = F < 2.5
            cons.append(dict(trace=t['id'], n_frame=round(t['n_frame'], 3), n_grader=round(abs(t['n_act_e']), 3), n_ref=round(n, 3), n_ref_src=src,
                             F=round(F, 2), F_iqr=round(float(c.F.quantile(0.75) - c.F.quantile(0.25)), 2), F_min=round(float(c.F.min()), 2), F_max=round(float(c.F.max()), 2),
                             found_in=f'{c[["lo", "hi", "deg"]].drop_duplicates().shape[0]}/{nch}', frac=round(c[['lo', 'hi', 'deg']].drop_duplicates().shape[0] / nch, 2),
                             contrast_med=round(float(c.contrast.median()), 1), amp_ohm_med=round(float(c.amp_ohm.median()), 1),
                             model_light=round(fl, 2), model_heavy=round(fh, 2), model_F_L=round(fL, 2), F_over_FL=round(F / fL, 3),
                             tone=ident, low_F_band=lowF))
    pd.DataFrame(raw).to_csv('tones_raw.csv', index=False)
    C = pd.DataFrame(cons).sort_values(['trace', 'F']); C.to_csv('tones.csv', index=False)
    pd.set_option('display.width', 250); pd.set_option('display.max_rows', 500); pd.set_option('display.max_colwidth', 60)
    for tid in ['0822-r7', '0824-r5-c0', '0825-r7-c0']:
        print(C[C.trace == tid][['trace', 'n_ref', 'F', 'F_min', 'F_max', 'found_in', 'contrast_med', 'amp_ohm_med', 'F_over_FL', 'tone']].to_string(index=False))
    D = C[C.trace.str.startswith('0824-r4') & (C.frac >= 0.5)]
    print(D[['trace', 'n_ref', 'F', 'found_in', 'contrast_med', 'F_over_FL', 'tone']].to_string(index=False))
    E = C[C.trace.str.startswith('0823-r6') & (C.frac >= 0.5)]
    print(E[['trace', 'n_ref', 'F', 'found_in', 'contrast_med', 'F_over_FL', 'tone']].to_string(index=False))
