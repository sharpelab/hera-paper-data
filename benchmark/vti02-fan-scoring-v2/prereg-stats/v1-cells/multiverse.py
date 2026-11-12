"""Multiverse over grader knobs: the primary statistic on the dev set per knob combination.
Exploratory, dev set only: the knobs were tuned on these same episodes.

    uv run --no-project --with numpy --with scipy python3 multiverse.py
Writes multiverse.csv, multiverse.md.
"""
import csv, itertools
import numpy as np
import common as C
import stats as S
import devset as DV

GRID = dict(k=(2.0, 2.5, 3.0), clip=(None, 0.55, 1.0), at2=(0.0, 0.25), cellw=(1, 2), tones=('model', 'emp'))
SETS = [('matrix-0822', C.MATRIX_MODELS, (C.CUT_0822,)),
        ('all-0822', DV.ALL_MODELS, (C.CUT_0822,)),
        ('all-both', DV.ALL_MODELS, (C.CUT_0822, C.CUT_0821))]
POLICIES = ('floor', 'landed')


def main():
    eps = C.inventory()
    rows = []
    for combo in itertools.product(*GRID.values()):
        kn = dict(zip(GRID, combo))
        DV.scored(kn, eps)
        for q in DV.QKEYS:
            if q == 'credit' and kn['cellw'] == 2:
                continue  # cellw does not touch credit
            if q != 'credit' and kn['at2'] == 0.25:
                continue  # at2 touches credit only
            for sname, models, cuts in SETS:
                for pol in POLICIES:
                    cl = DV.cells_of(eps, q, pol, models, cuts)
                    d = S.pooled(cl, S.D, models)
                    a, b = DV.arm_pooled(eps, q, pol, models, cuts)
                    rows.append(dict(**{k: ('none' if v is None else v) for k, v in kn.items()}, quality=q, set=sname,
                                     policy=pol, D_pool=d, D_armpooled=S.D(a, b),
                                     HV1_diff=S.hv1(a, 8, DV.QNORM[q]) - S.hv1(b, 8, DV.QNORM[q])))
    with open(C.OUT / 'multiverse.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    L = []
    P = L.append
    P('# Multiverse (dev set, exploratory)\n')
    P('Grid: k ∈ {2, 2.5, 3}; onset clip ∈ {none, 0.55, 1.0 T}; 2-period credit a ∈ {0, 0.25} (credit only); '
      'cell width ∈ {bare bin, Hann 2δF} (cells only); tones ∈ {corpus model, empirical F_light/F_L = 0.0394 n + 0.1235}.\n')
    P('| set | policy | quality | combos | D_pool min / median / max | share D_pool > 0 | D_armpooled min / median / max | HV1 diff min / median / max |')
    P('|---|---|---|---|---|---|---|---|')
    for sname, _, _ in SETS:
        for pol in POLICIES:
            for q in DV.QKEYS:
                r = [x for x in rows if x['set'] == sname and x['policy'] == pol and x['quality'] == q]
                d = np.array([x['D_pool'] for x in r]); da = np.array([x['D_armpooled'] for x in r]); hv = np.array([x['HV1_diff'] for x in r])
                P(f"| {sname} | {pol} | {q} | {len(r)} | {np.nanmin(d):+.2f} / {np.nanmedian(d):+.2f} / {np.nanmax(d):+.2f} | {np.mean(d > 0):.2f} | "
                  f"{da.min():+.2f} / {np.median(da):+.2f} / {da.max():+.2f} | {hv.min():+.3f} / {np.median(hv):+.3f} / {hv.max():+.3f} |")
    # knob main effects on the arm-pooled D, all-0822, floor, cells
    P('\n## Knob main effects (all models, 08-22, floor policy): mean D_armpooled at each knob level\n')
    for q in ('cells', 'credit'):
        r = [x for x in rows if x['set'] == 'all-0822' and x['policy'] == 'floor' and x['quality'] == q]
        parts = []
        for k in GRID:
            lv = sorted({str(x[k]) for x in r})
            if len(lv) < 2:
                continue
            parts.append(f"{k}: " + ', '.join(f"{v} {np.mean([x['D_armpooled'] for x in r if str(x[k]) == v]):+.2f}" for v in lv))
        P(f"- {q}: " + '; '.join(parts))
    P('\n## Knob main effects (all models, both cuts, landed policy): mean D_pool\n')
    for q in ('cells', 'credit', 'band'):
        r = [x for x in rows if x['set'] == 'all-both' and x['policy'] == 'landed' and x['quality'] == q]
        parts = []
        for k in GRID:
            lv = sorted({str(x[k]) for x in r})
            if len(lv) < 2:
                continue
            parts.append(f"{k}: " + ', '.join(f"{v} {np.nanmean([x['D_pool'] for x in r if str(x[k]) == v]):+.2f}" for v in lv))
        P(f"- {q}: " + '; '.join(parts))
    open(C.OUT / 'multiverse.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
