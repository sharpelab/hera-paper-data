"""Dev-set table and dominance statistics.

    uv run --no-project --with numpy --with scipy python3 devset.py
Writes episodes.csv, devset_stats.md.
"""
import csv, json
import numpy as np
import common as C
import stats as S

BASE = dict(k=3.0, clip=0.55, at2=0.0, cellw=1, tones='model')
QKEYS = ('band', 'credit', 'cells', 'cells_acq')
QNORM = {'band': 15.0, 'credit': 15.0, 'cells': 1.0, 'cells_acq': 1.0}  # HV normalisation (band/credit capped at 15)


def scored(knobs=BASE, eps=None):
    eps = eps if eps is not None else C.inventory()
    for e in eps:
        if e['ending'] == 'fan':
            if '_design' not in e:
                e['_design'] = C.design(e)
            B, n, h, acq = e['_design']
            e.update(C.score(B, n, knobs, acq), hours=h, **{f'acq_{k}': v for k, v in acq.items()})
    return eps


def counted(e):
    return e['ending'] in ('fan', 'probe', 'b0', 'none')


def cells_of(eps, qkey, policy, models, cuts=(C.CUT_0822,), effort=None):
    out = {}
    for m in models:
        for arm in ('corpus', 'none'):
            sel = [e for e in eps if counted(e) and e['model'] == m and e['corpus'] == arm and e['cut'] in cuts
                   and (effort is None or e['effort'] == effort)]
            out[(m, arm)] = S.place(sel, qkey, policy)
    return out


def arm_pooled(eps, qkey, policy, models, cuts=(C.CUT_0822,)):
    sel = lambda arm: [e for e in eps if counted(e) and e['model'] in models and e['corpus'] == arm and e['cut'] in cuts]
    return S.place(sel('corpus'), qkey, policy), S.place(sel('none'), qkey, policy)


ALL_MODELS = ('fable', 'opus', 'sol', 'astra', 'sonnet', 'haiku', 'luna')


def main():
    eps = scored()
    live = C.live_fans()
    for e in live:
        if e['ending'] == 'fan':
            B, n, h, acq = C.design(e)
            e.update(C.score(B, n, BASE, acq), hours=h)
    # ---- episodes.csv
    cols = ['key', 'model', 'corpus', 'effort', 'cut', 'status', 'stop_cell', 'cells', 'ending', 'source',
            'band', 'credit', 'cells', 'n_cells', 'cells_acq', 'hours', 'acq_snr', 'acq_quant', 'cost_usd',
            'tok_input', 'tok_cache_creation', 'tok_cache_read', 'tok_output']
    with open(C.OUT / 'episodes.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(dict.fromkeys(cols))
        for e in eps:
            t = e.get('tokens') or {}
            w.writerow([e.get(c) if not c.startswith('tok_') else t.get(c[4:]) for c in cols])
    L = []
    P = L.append
    P('# Dev-set dominance statistics (exploratory; base knobs k 3, clip 0.55 T, a 0, bare bin, model tones)\n')
    # ---- inventory counts
    P('## Inventory (observed model, not case name)\n')
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
                P(f"| {m} | {arm} | {'08-22' if cut == C.CUT_0822 else '08-21' if cut == C.CUT_0821 else 'other'} | {c('fan')} | {c('probe')} | {c('b0')} | {c('none')} | {ex} | {c('ungraded')} |")
    P('\n## Fans (base knobs)\n')
    P('| episode | model | arm | effort | cut | src | band | credit | cells (n_cells) | cells×acq | h |')
    P('|---|---|---|---|---|---|---|---|---|---|---|')
    for e in sorted([x for x in eps if x['ending'] == 'fan'], key=lambda x: (x['cut'] != C.CUT_0822, x['model'], x['corpus'])):
        P(f"| {e['key'].replace('vti02-fan-design-', '')} | {e['model']} | {e['corpus']} | {e['effort']} | {'08-22' if e['cut'] == C.CUT_0822 else '08-21'} | {e['source']} | {e['band']} | {e['credit']:.1f} | {e['cells']:.2f} ({e['n_cells']}) | {e['cells_acq']:.3f} | {e['hours']:.2f} |")
    for e in live:
        if e['ending'] == 'fan':
            P(f"| {e['key']} | — | — | — | live | grader | {e['band']} | {e['credit']:.1f} | {e['cells']:.2f} ({e['n_cells']}) | {e['cells_acq']:.3f} | {e['hours']:.2f} |")
    # ---- statistics by set / policy / quality
    rng = np.random.default_rng(1)
    sets = [('matrix models, 08-22', C.MATRIX_MODELS, (C.CUT_0822,)),
            ('all models, 08-22', ALL_MODELS, (C.CUT_0822,)),
            ('all models, both cuts', ALL_MODELS, (C.CUT_0822, C.CUT_0821))]
    P('\n## Pooled-over-models pairwise dominance D (mean over models with both arms), 95 % stratified bootstrap\n')
    P('| set | quality | floor | own | landed |')
    P('|---|---|---|---|---|')
    for name, models, cuts in sets:
        for q in QKEYS:
            row = []
            for pol in ('floor', 'own', 'landed'):
                cl = cells_of(eps, q, pol, models, cuts)
                est, lo, hi = S.boot(cl, S.D, models, B=1000, rng=rng)
                nm = sum(1 for m in models if len(cl[(m, 'corpus')]) and len(cl[(m, 'none')]))
                row.append(f"{est:+.2f} [{lo:+.2f}, {hi:+.2f}] (m={nm})")
            P(f"| {name} | {q} | " + ' | '.join(row) + ' |')
    P('\n## Per-model D (08-22 cut, floor policy, quality = cells) and cell sizes\n')
    P('| model | n corpus (fans) | n none (fans) | D | HV1 diff (h_ref 8) | frontier share c / n |')
    P('|---|---|---|---|---|---|')
    for m in ALL_MODELS:
        cl = cells_of(eps, 'cells', 'floor', (m,))
        a, b = cl[(m, 'corpus')], cl[(m, 'none')]
        if not len(a) and not len(b):
            continue
        fa, fb = int(np.isfinite(a[:, 1]).sum()) if len(a) else 0, int(np.isfinite(b[:, 1]).sum()) if len(b) else 0
        fs = S.frontier_share(a, b) if len(a) and len(b) else (np.nan, np.nan)
        P(f"| {m} | {len(a)} ({fa}) | {len(b)} ({fb}) | {S.D(a, b):+.2f} | {S.hv1(a, 8) - S.hv1(b, 8) if len(a) and len(b) else np.nan:+.3f} | {fs[0]:.2f} / {fs[1]:.2f} |")
    P('\n## Arm-pooled (ignoring model) statistics, all models, 08-22 cut, quality = cells\n')
    P('| policy | n c / n | D | set-HV diff h_ref 6 / 8 / 12 | HV1 diff h_ref 6 / 8 / 12 | frontier share c / n |')
    P('|---|---|---|---|---|---|')
    for pol in ('floor', 'own', 'landed'):
        a, b = arm_pooled(eps, 'cells', pol, ALL_MODELS)
        hvs = ' / '.join(f"{S.hv_set(a, r) - S.hv_set(b, r):+.3f}" for r in (6, 8, 12))
        hv1 = ' / '.join(f"{S.hv1(a, r) - S.hv1(b, r):+.3f}" for r in (6, 8, 12))
        fs = S.frontier_share(a, b)
        P(f"| {pol} | {len(a)} / {len(b)} | {S.D(a, b):+.2f} | {hvs} | {hv1} | {fs[0]:.2f} / {fs[1]:.2f} |")
    # set-HV n-dependence: HV of random k-subsets of the corpus arm
    a, _ = arm_pooled(eps, 'cells', 'floor', ALL_MODELS)
    P('\nSet-hypervolume grows with cloud size (corpus arm, floor, h_ref 8; mean over 2000 random subsets):')
    P('| subset size | 1 | 2 | 5 | 10 | 15 | all |')
    P('|---|---|---|---|---|---|---|')
    vals = []
    for k in (1, 2, 5, 10, 15):
        vals.append(np.mean([S.hv_set(a[rng.choice(len(a), k, replace=False)], 8) for _ in range(2000)]) if k <= len(a) else np.nan)
    P('| set HV | ' + ' | '.join(f"{v:.3f}" for v in vals) + f" | {S.hv_set(a, 8):.3f} |")
    open(C.OUT / 'devset_stats.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    # frozen reference set for the per-cell stopping score: every counted 08-22 episode, base knobs, floor
    R = S.place([e for e in eps if counted(e) and e['cut'] == C.CUT_0822], 'cells', 'floor')
    json.dump({'knobs': BASE, 'quality': 'cells', 'policy': 'floor', 'points': [[float(q), None if np.isinf(h) else float(h)] for q, h in R]},
              open(C.OUT / 'reference_set.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
