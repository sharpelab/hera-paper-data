"""Multiverse over the grader's pre-registered sensitivity axes: D_pool, arm-pooled D and ΔHV1 on the
dev set per universe. Exploratory: the grader was developed on these episodes.

    uv run --no-project --with numpy --with scipy python3 multiverse.py
Writes multiverse.csv, multiverse.md.

Axes (full factorial):
  tones    Halder_ABAB | corpus | env_lo | env_hi | B (refit)
  light    light-window floor 0.75 | 1.0 T
  lines    soft (m 2->3 rows, k 1.5->3.5 periods) | hard m = 3 | hard k = 3 | both hard
  columns  1/2 bin, cap 7 | 1 bin, cap 5 | 1/2 bin, no cap
  score    both parts | split only | P(call) | P(call) with the parts averaged | with their product |
           with a step at 4 points (P(>=4)) | with a linear curve
  A        on | off | noise model (vti-noise split-detection ratio, capped at 1; I*sqrt(tau) A where it has no row)
"""
import csv, itertools
import numpy as np
import common as C
import stats as S
import devset as DV

box = C.box
HARD = (3.0 - 1e-6, 3.0)
AXES = dict(
    tones=('Halder_ABAB', 'corpus', 'env_lo', 'env_hi', 'B'),
    light=(0.75, 1.0),
    lines=('soft', 'hard m', 'hard k', 'both hard'),
    columns=('1/2 bin, 7', '1 bin, 5', '1/2 bin, none'),
    score=('both', 'split', 'P(call)', 'parts averaged', 'parts product', 'step at 4', 'linear'),
    A=('on', 'off', 'noise model'),
)
LINES = {'soft': (box.M, box.K), 'hard m': (HARD, box.K), 'hard k': (box.M, HARD), 'both hard': (HARD, HARD)}
STEP = lambda x: (x >= 1).astype(float)
LINEAR = lambda x: np.clip(x, 0, 1)
PCOMB = {'P(call)': (min, box.smoothstep), 'parts averaged': (lambda g: float(np.mean(g)), box.smoothstep),
         'parts product': (lambda g: float(np.prod(g)), box.smoothstep), 'step at 4': (min, STEP), 'linear': (min, LINEAR)}
COLUMNS = {'1/2 bin, 7': (0.5, 7), '1 bin, 5': (1.0, 5), '1/2 bin, none': (0.5, None)}
SETS = [('matrix-0822', C.MATRIX_MODELS, (C.CUT_0822,)), ('all-0822', DV.ALL_MODELS, (C.CUT_0822,)),
        ('all-both', DV.ALL_MODELS, (C.CUT_0822, C.CUT_0821))]
NOISE = '/data/sharpelab/hera-data/vti-noise/generator/work/acq_factor_band_on.csv'


def noise_factors():
    """episode key suffix -> the noise model's split-detection ratio (own / reference), capped at 1."""
    out = {}
    for r in csv.DictReader(open(NOISE)):
        lab, _, rep = r['label'].partition(' #')
        key = lab if lab.startswith('live') else f"{lab}/{int(rep or 0):02d}"
        out[key] = min(1.0, float(r['fac_b']))
    return out


def parts(r, tones, light, m, k, spacing, cap):
    """Per part: (capped score, spread weights) at these knobs; box.score's column weights and selection."""
    B, n, _ = r['_design']
    s, _ = C.score(r, tone_model=tones, b_lo_light=light, m=m, k=k, spacing=spacing, cap=cap or len(n))
    out = {}
    B = np.unique(np.asarray(B, float)[np.asarray(B, float) > 0])
    fl = box.f_light(n, tones)
    electron = (n > 0) & ~np.isnan(fl)
    f = np.where(electron, fl, 0.0)
    acq = s['acquisition']
    clipped = (acq['I_A'] * box.r_max(n) >= box.CLIP_FRACTION * acq['sensitivity_V']
               if acq['sensitivity_V'] is not None and acq['I_A'] is not None else np.zeros(n.size, bool))
    usable = electron & ~clipped
    for name, tone, b_lo in (('light', f, light), ('split', box.FLN * np.where(electron, n, 0.0), C.BASE['b_lo_split'])):
        win = box.window(B, b_lo)
        gap = spacing / win['W_per_T'] if win['W_per_T'] else np.inf
        w = np.where(usable, box.ramp(f * box.w_eff(tone, win['intervals'], m), k), 0.0)
        _, spread = box.best_spaced(w, f, gap, n.size)
        out[name] = (s[name]['score'], w[spread])
    return out, s['A']


def selftest(fans):
    bad = 0
    for r in fans:
        pt, A = parts(r, 'Halder_ABAB', 0.75, box.M, box.K, box.SPACING, box.CAP)
        s, _ = C.score(r)
        q = A * (pt['light'][0] + pt['split'][0]) / (2 * box.CAP)
        p = min(box.p_call(list(A * pt[x][1])) for x in ('light', 'split'))
        bad += abs(q - s['quality']) > 1e-12 or abs(p - s['p_call']) > 1e-12
    assert bad == 0, f'{bad} fans disagree with box.score'


def delta8(fans, models, cuts=(C.CUT_0822,)):
    """The primary: mean over models with fans in both arms of mean v(corpus) − mean v(none),
    v = q_mv (P(call) in this universe) × [hours ≤ 8]; censored endings are not fans."""
    d = []
    for m in models:
        v = {a: [e['q_mv'] * (e['hours'] <= 8.0) for e in fans if e['model'] == m and e['corpus'] == a and e['cut'] in cuts]
             for a in ('corpus', 'none')}
        if v['corpus'] and v['none']:
            d.append(np.mean(v['corpus']) - np.mean(v['none']))
    return float(np.mean(d)) if d else np.nan


def main():
    eps = DV.scored()
    fans = [e for e in eps if e['ending'] == 'fan']
    for e in fans:
        C.score(e)
    selftest(fans)
    nf = noise_factors()
    has_noise = sum(e['key'].replace('vti02-fan-design-', '').replace('/episodes/', '/') in nf for e in fans)
    rows, primary = [], []
    for tones, light, lines, columns in itertools.product(AXES['tones'], AXES['light'], AXES['lines'], AXES['columns']):
        (m, k), (spacing, cap) = LINES[lines], COLUMNS[columns]
        per = {id(e): parts(e, tones, light, m, k, spacing, cap) for e in fans}
        for score, acq in itertools.product(AXES['score'], AXES['A']):
            for e in fans:
                pt, A = per[id(e)]
                key = e['key'].replace('vti02-fan-design-', '').replace('/episodes/', '/')
                a = {'on': A, 'off': 1.0, 'noise model': nf.get(key, A)}[acq]
                c = cap or 7
                e['q_mv'] = (a * (pt['light'][0] + pt['split'][0]) / (2 * c) if score == 'both' else
                             a * pt['split'][0] / c if score == 'split' else
                             PCOMB[score][0]([box.p_call(list(a * pt[x][1]), shape=PCOMB[score][1]) for x in ('light', 'split')]))
            qnorm = max(1.0, max(e['q_mv'] for e in fans))
            if score in PCOMB:
                for sname, models, cuts in SETS[:2]:
                    primary.append(dict(tones=tones, light=light, lines=lines, columns=columns, A=acq, set=sname,
                                        parts=score, delta8=delta8(fans, models, cuts)))
            for sname, models, cuts in SETS:
                for pol in ('floor', 'landed'):
                    cl = DV.cells_of(eps, 'q_mv', pol, models, cuts)
                    a_, b_ = DV.arm_pooled(eps, 'q_mv', pol, models, cuts)
                    rows.append(dict(tones=tones, light=light, lines=lines, columns=columns, score=score, A=acq,
                                     set=sname, policy=pol, D_pool=S.pooled(cl, S.D, models), D_armpooled=S.D(a_, b_),
                                     dHV1_pool=S.pooled(cl, lambda x, y: S.hv1(x, 8, qnorm) - S.hv1(y, 8, qnorm), models)))
    with open(C.OUT / 'multiverse.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    base = dict(tones='Halder_ABAB', light=0.75, lines='soft', columns='1/2 bin, 7', score='both', A='on')
    L = []
    P = L.append
    n_u = int(np.prod([len(v) for v in AXES.values()]))
    P(f'# Multiverse (dev set, exploratory): {n_u} universes\n')
    P('Axes: ' + '; '.join(f"{k} ∈ {{{', '.join(map(str, v))}}}" for k, v in AXES.items()) + '. '
      f'Noise-model A covers {has_noise} of {len(fans)} dev fans; the rest keep the I·√τ A. '
      'An uncapped universe normalizes by 14 as if capped at 7; ΔHV1 uses h_ref 8 h and the universe\'s own maximum '
      'quality when it exceeds 1.\n')
    P('## Over all universes\n')
    P('| set | policy | D_pool at the frozen grader | D_pool min / median / max | share of D_pool with its sign | '
      'arm-pooled D min / median / max | ΔHV1_pool min / median / max | share of ΔHV1 > 0 |')
    P('|---|---|---|---|---|---|---|---|')
    for sname, _, _ in SETS:
        for pol in ('floor', 'landed'):
            r = [x for x in rows if x['set'] == sname and x['policy'] == pol]
            b0 = next(x for x in r if all(x[k] == v for k, v in base.items()))
            d = np.array([x['D_pool'] for x in r]); da = np.array([x['D_armpooled'] for x in r])
            hv = np.array([x['dHV1_pool'] for x in r])
            same = np.mean(np.sign(d) == np.sign(b0['D_pool']))
            P(f"| {sname} | {pol} | {b0['D_pool']:+.2f} | {d.min():+.2f} / {np.median(d):+.2f} / {d.max():+.2f} | {same:.2f} | "
              f"{da.min():+.2f} / {np.median(da):+.2f} / {da.max():+.2f} | "
              f"{hv.min():+.3f} / {np.median(hv):+.3f} / {hv.max():+.3f} | {np.mean(hv > 0):.2f} |")
    P('\n## One axis at a time from the frozen grader (the other five at their frozen values)\n')
    for sname, pol in (('matrix-0822', 'floor'), ('all-0822', 'floor'), ('all-both', 'floor')):
        P(f'\n**{sname}, {pol}**\n')
        P('| axis | level | D_pool | arm-pooled D | ΔHV1_pool |')
        P('|---|---|---|---|---|')
        r = [x for x in rows if x['set'] == sname and x['policy'] == pol]
        for ax, levels in AXES.items():
            for lv in levels:
                x = next(x for x in r if x[ax] == lv and all(x[k] == v for k, v in base.items() if k != ax))
                P(f"| {ax} | {lv}{' (frozen)' if lv == base[ax] else ''} | {x['D_pool']:+.2f} | {x['D_armpooled']:+.2f} | {x['dHV1_pool']:+.3f} |")
    P('\n## Main effects (all universes; mean D_pool at each level)\n')
    for sname, pol in (('matrix-0822', 'floor'), ('all-0822', 'floor')):
        r = [x for x in rows if x['set'] == sname and x['policy'] == pol]
        P(f"- {sname}, {pol}: " + '; '.join(
            f"{ax}: " + ', '.join(f"{lv} {np.mean([x['D_pool'] for x in r if x[ax] == lv]):+.2f}" for lv in levels)
            for ax, levels in AXES.items()))
    P('\n## The primary, Δ(8 h), across the grader universes (P(call) per fan; censored endings excluded)\n')
    P('| set | P(call) variant | Δ(8 h) at the frozen knobs | min / median / max | share with the frozen grader\'s sign |')
    P('|---|---|---|---|---|')
    for sname, _, _ in SETS[:2]:
        at = lambda x: (x['tones'] == 'Halder_ABAB' and x['light'] == 0.75 and x['lines'] == 'soft'
                        and x['columns'] == '1/2 bin, 7' and x['A'] == 'on')
        rs = [x for x in primary if x['set'] == sname]
        frozen = next(x['delta8'] for x in rs if at(x) and x['parts'] == 'P(call)')
        for lab, r in [(c, [x for x in rs if x['parts'] == c]) for c in PCOMB] + [('all variants', rs)]:
            b0 = frozen if lab == 'all variants' else next(x['delta8'] for x in r if at(x))
            d = np.array([x['delta8'] for x in r])
            P(f"| {sname} | {lab} | {b0:+.2f} | {np.nanmin(d):+.2f} / {np.nanmedian(d):+.2f} / {np.nanmax(d):+.2f} | {np.mean(np.sign(d) == np.sign(frozen)):.2f} |")
    P('\nOne axis at a time (matrix models, 08-22), Δ(8 h):')
    r = [x for x in primary if x['set'] == 'matrix-0822']
    fz = dict(tones='Halder_ABAB', light=0.75, lines='soft', columns='1/2 bin, 7', A='on', parts='P(call)')
    for ax in fz:
        vals = ', '.join(f"{lv} {next(x['delta8'] for x in r if x[ax] == lv and all(x[k] == v for k, v in fz.items() if k != ax)):+.2f}"
                         for lv in (tuple(PCOMB) if ax == 'parts' else AXES[ax]))
        P(f"- {ax}: {vals}")
    open(C.OUT / 'multiverse.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
