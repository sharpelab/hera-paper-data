"""Dev-set table and dominance statistics under the final grader (box quality, cost-model hours).

    uv run --no-project --with numpy --with scipy python3 devset.py
Writes episodes.csv, devset_stats.md, reference_set.json.
"""
import csv, json
import numpy as np
import common as C
import stats as S

ALL_MODELS = ('fable', 'opus', 'sol', 'astra', 'sonnet', 'haiku', 'luna')
SETS = [('matrix models, 08-22', C.MATRIX_MODELS, (C.CUT_0822,)),
        ('all models, 08-22', ALL_MODELS, (C.CUT_0822,)),
        ('all models, both cuts', ALL_MODELS, (C.CUT_0822, C.CUT_0821))]
QKEYS = ('quality', 'p4')
H_REFS = (6, 8, 12)


def scored(eps=None, **knobs):
    eps = eps if eps is not None else C.inventory()
    for e in eps:
        if e['ending'] == 'fan':
            s, h = C.score(e, **knobs)
            e.update(quality=s['quality'], p4=s['p_success'], A=s['A'], light=s['light']['score'],
                     split=s['split']['score'], hours=h, flags='; '.join(s['flags']))
    return eps


def counted(e):
    return e['ending'] in ('fan', 'probe', 'b0', 'none')


def cells_of(eps, qkey, policy, models, cuts=(C.CUT_0822,)):
    out = {}
    for m in models:
        for arm in ('corpus', 'none'):
            sel = [e for e in eps if counted(e) and e['model'] == m and e['corpus'] == arm and e['cut'] in cuts]
            out[(m, arm)] = S.place(sel, qkey, policy)
    return out


def arm_pooled(eps, qkey, policy, models, cuts=(C.CUT_0822,)):
    sel = lambda arm: [e for e in eps if counted(e) and e['model'] in models and e['corpus'] == arm and e['cut'] in cuts]
    return S.place(sel('corpus'), qkey, policy), S.place(sel('none'), qkey, policy)


def dhv1(h_ref):
    return lambda a, b: S.hv1(a, h_ref) - S.hv1(b, h_ref)


def n_models(cl, models):
    return sum(1 for m in models if len(cl[(m, 'corpus')]) and len(cl[(m, 'none')]))


def main():
    eps = scored()
    live = [e for e in C.live_fans() if e['ending'] == 'fan']
    scored(live)
    cols = ['key', 'model', 'corpus', 'effort', 'cut', 'status', 'stop_cell', 'cells', 'ending', 'source',
            'light', 'split', 'A', 'quality', 'p4', 'hours', 'flags', 'cost_usd',
            'tok_input', 'tok_cache_creation', 'tok_cache_read', 'tok_output']
    with open(C.OUT / 'episodes.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for e in eps:
            t = e.get('tokens') or {}
            w.writerow([e.get(c) if not c.startswith('tok_') else t.get(c[4:]) for c in cols])
    L = []
    P = L.append
    P('# Dev-set dominance statistics (box grader at its frozen parameters; exploratory)\n')
    P('## Inventory (observed model)\n')
    P('| model | arm | cut | fan | probe | b0 | none | excluded | ungraded |')
    P('|---|---|---|---|---|---|---|---|---|')
    for m in ALL_MODELS:
        for arm in ('corpus', 'none'):
            for cut in (C.CUT_0822, C.CUT_0821, 'other'):
                sel = [e for e in eps if e['model'] == m and e['corpus'] == arm and
                       (e['cut'] == cut if cut != 'other' else e['cut'] not in (C.CUT_0822, C.CUT_0821))]
                if not sel:
                    continue
                c = lambda k: sum(e['ending'] == k for e in sel)
                ex = sum(e['ending'].startswith('excluded') for e in sel)
                P(f"| {m} | {arm} | {'08-22' if cut == C.CUT_0822 else '08-21' if cut == C.CUT_0821 else 'other'} | "
                  f"{c('fan')} | {c('probe')} | {c('b0')} | {c('none')} | {ex} | {c('ungraded')} |")
    P('\n## Fans\n')
    P('| episode | model | arm | effort | cut | src | light | split | A | quality | P(≥4) | h |')
    P('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for e in sorted([x for x in eps if x['ending'] == 'fan'], key=lambda x: (x['cut'] != C.CUT_0822, x['model'], x['corpus'])):
        P(f"| {e['key'].replace('vti02-fan-design-', '')} | {e['model']} | {e['corpus']} | {e['effort']} | "
          f"{'08-22' if e['cut'] == C.CUT_0822 else '08-21'} | {e['source']} | {e['light']:.2f} | {e['split']:.2f} | "
          f"{e['A']:.2f} | {e['quality']:.2f} | {e['p4']:.2f} | {e['hours']:.2f} |")
    for e in live:
        P(f"| {e['key']} | — | — | — | live | grader | {e['light']:.2f} | {e['split']:.2f} | {e['A']:.2f} | "
          f"{e['quality']:.2f} | {e['p4']:.2f} | {e['hours']:.2f} |")

    rng = np.random.default_rng(1)
    P('\n## D_pool: mean over models of P(corpus ≻ none) − P(none ≻ corpus); 95 % stratified bootstrap (B 2000), '
      'within-model permutation p (10 000)\n')
    P('| set | score | floor | own | landed | p (floor) |')
    P('|---|---|---|---|---|---|')
    for name, models, cuts in SETS:
        for q in QKEYS:
            row = []
            for pol in ('floor', 'own', 'landed'):
                cl = cells_of(eps, q, pol, models, cuts)
                est, lo, hi = S.boot(cl, S.D, models, B=2000, rng=rng)
                row.append(f"{est:+.2f} [{lo:+.2f}, {hi:+.2f}] (m={n_models(cl, models)})")
            p = S.perm_p(cells_of(eps, q, 'floor', models, cuts), models, 10000, rng)
            P(f"| {name} | {q} | " + ' | '.join(row) + f" | {p:.3f} |")
    P('\n## ΔHV1_pool: mean over models of [mean HV1 corpus − mean HV1 none], HV1 = Q·(1 − h/h_ref)+; floor\n')
    P('| set | h_ref 6 | h_ref 8 | h_ref 12 |')
    P('|---|---|---|---|')
    for name, models, cuts in SETS:
        cl = cells_of(eps, 'quality', 'floor', models, cuts)
        vals = [S.boot(cl, dhv1(h), models, B=2000, rng=rng) for h in H_REFS]
        P(f"| {name} | " + ' | '.join(f"{e:+.3f} [{lo:+.3f}, {hi:+.3f}]" for e, lo, hi in vals) + ' |')
    P('\n## Per model (08-22 cut, floor, quality)\n')
    P('| model | corpus: episodes (fans) | none: episodes (fans) | D | ΔHV1 (h_ref 8) | frontier share c / n |')
    P('|---|---|---|---|---|---|')
    for m in ALL_MODELS:
        cl = cells_of(eps, 'quality', 'floor', (m,))
        a, b = cl[(m, 'corpus')], cl[(m, 'none')]
        if not len(a) and not len(b):
            continue
        nf = lambda x: int(np.isfinite(x[:, 1]).sum()) if len(x) else 0
        both = len(a) and len(b)
        fs = S.frontier_share(a, b) if both else (np.nan, np.nan)
        P(f"| {m} | {len(a)} ({nf(a)}) | {len(b)} ({nf(b)}) | {S.D(a, b):+.2f} | "
          f"{dhv1(8)(a, b) if both else np.nan:+.3f} | {fs[0]:.2f} / {fs[1]:.2f} |")
    P('\n## Arm-pooled, ignoring model (08-22, quality): the stratification check\n')
    P('| models | policy | n corpus / none | arm-pooled D | D_pool | ΔHV1 h_ref 6 / 8 / 12 | frontier share c / n |')
    P('|---|---|---|---|---|---|---|')
    for mname, models in (('matrix', C.MATRIX_MODELS), ('all', ALL_MODELS)):
        for pol in ('floor', 'landed'):
            a, b = arm_pooled(eps, 'quality', pol, models)
            fs = S.frontier_share(a, b)
            P(f"| {mname} | {pol} | {len(a)} / {len(b)} | {S.D(a, b):+.2f} | {S.pooled(cells_of(eps, 'quality', pol, models), S.D, models):+.2f} | "
              + ' / '.join(f"{dhv1(h)(a, b):+.3f}" for h in H_REFS) + f" | {fs[0]:.2f} / {fs[1]:.2f} |")
    a, _ = arm_pooled(eps, 'quality', 'floor', ALL_MODELS)
    P('\nSet hypervolume grows with cloud size (corpus arm, floor, h_ref 8; mean over 2000 random subsets):\n')
    P('| subset size | 1 | 2 | 5 | 10 | all |')
    P('|---|---|---|---|---|---|')
    vals = [np.mean([S.hv_set(a[rng.choice(len(a), k, replace=False)], 8) for _ in range(2000)]) if k <= len(a) else np.nan
            for k in (1, 2, 5, 10)]
    P('| set HV | ' + ' | '.join(f"{v:.3f}" for v in vals) + f" | {S.hv_set(a, 8):.3f} |")
    open(C.OUT / 'devset_stats.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    R = S.place([e for e in eps if counted(e) and e['cut'] == C.CUT_0822], 'quality', 'floor')
    json.dump({'grader': 'box', 'params': {k: (list(v) if isinstance(v, tuple) else v) for k, v in C.BASE.items()},
               'quality': 'quality', 'policy': 'floor',
               'points': [[float(q), None if np.isinf(h) else float(h)] for q, h in R]},
              open(C.OUT / 'reference_set.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
