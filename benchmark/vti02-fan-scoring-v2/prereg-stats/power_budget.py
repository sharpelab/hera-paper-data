"""Power / precision of the headline: the success-within-budget share, with censoring.

    uv run --no-project --with numpy --with scipy python3 power_budget.py [S] [B]
Writes power_budget.md.

Per fan: v = P(call) * [hours <= T]. Spot-check, B = 0 and no-call endings are censored: counted,
not scored. Per (model, arm) cell: S = mean v over its fans. Estimand: Delta = mean over the matrix
models of S(corpus) - S(none). A cell runs until N fans, capped at 2N episodes.

Pilot (08-22 dev set): each cell's fans and censoring rate, shrunk toward its arm's pool with prior
weight N0 (`smoothed`); the arm's pool alone (`pooled`); both arms pooled (`null`).
"""
import sys
import numpy as np
import common as C
import devset as DV

N0 = 3
MODELS = C.MATRIX_MODELS
ARMS = ('corpus', 'none')
T_HEAD, T_SENS = 8.0, (6.0, 12.0)
NS = (5, 10, 20)
Z = 1.959964
MDE_K = (1.959964 + 0.841621) / 1.959964  # 80 % power at two-sided 5 %, in CI half-widths


def dev_cells(eps):
    """(model, arm) -> (fan rows [p, h], censored count, counted count); arm pools over all models."""
    base = [e for e in eps if DV.counted(e) and e['cut'] == C.CUT_0822]
    cell = lambda sel: (np.array([[e['p_call'], e['hours']] for e in sel if e['ending'] == 'fan'], float).reshape(-1, 2),
                        sum(e['ending'] != 'fan' for e in sel), len(sel))
    own = {(m, a): cell([e for e in base if e['model'] == m and e['corpus'] == a]) for m in MODELS for a in ARMS}
    pool = {a: cell([e for e in base if e['corpus'] == a]) for a in ARMS}
    both = cell(base)
    return own, pool, both


def pilot(kind, own, pool, both):
    """-> {(m, a): (fan sampler(rng, k) -> rows, censoring probability)}"""
    out = {}
    for m in MODELS:
        for a in ARMS:
            if kind == 'null':
                src, cz = [(both[0], 1.0)], both[1] / both[2]
            elif kind == 'pooled':
                src, cz = [(pool[a][0], 1.0)], pool[a][1] / pool[a][2]
            else:
                f, c, n = own[(m, a)]
                pf, pc, pn = pool[a]
                src = [(f, len(f) / (len(f) + N0)), (pf, N0 / (len(f) + N0))] if len(f) else [(pf, 1.0)]
                cz = (c + N0 * pc / pn) / (n + N0)
            out[(m, a)] = (src, cz)
    return out


def draw_fans(src, rng, k):
    w = np.array([x[1] for x in src]); comp = rng.choice(len(src), k, p=w / w.sum())
    rows = np.empty((k, 2))
    for i, (arr, _) in enumerate(src):
        idx = comp == i
        rows[idx] = arr[rng.integers(0, len(arr), idx.sum())]
    return rows


def run_cell(src, cz, rng, N):
    """One cell under the rule: episodes until N fans or 2N episodes. -> (fan rows, episodes, censored)"""
    fan = rng.random(2 * N) >= cz
    cum = np.cumsum(fan)
    n_ep = int(np.searchsorted(cum, N) + 1) if cum[-1] >= N else 2 * N
    k = int(cum[n_ep - 1])
    return draw_fans(src, rng, k) if k else np.zeros((0, 2)), n_ep, n_ep - k


def values(rows, T):
    return rows[:, 0] * (rows[:, 1] <= T)


def delta(cells, T):
    d = [values(cells[(m, 'corpus')], T).mean() - values(cells[(m, 'none')], T).mean() for m in MODELS
         if len(cells[(m, 'corpus')]) and len(cells[(m, 'none')])]
    return float(np.mean(d)) if d else np.nan


def boot_ci(cells, T, rng, B):
    ms = [m for m in MODELS if len(cells[(m, 'corpus')]) and len(cells[(m, 'none')])]
    if not ms:
        return np.nan, np.nan, np.nan
    acc = np.zeros(B)
    for m in ms:
        for a, sgn in (('corpus', 1), ('none', -1)):
            v = values(cells[(m, a)], T)
            acc += sgn * v[rng.integers(0, len(v), (B, len(v)))].mean(1)
    acc /= len(ms)
    lo, hi = np.percentile(acc, [2.5, 97.5])
    return delta(cells, T), lo, hi


def perm_p(cells, T, rng, n_perm):
    ms = [m for m in MODELS if len(cells[(m, 'corpus')]) and len(cells[(m, 'none')])]
    if not ms:
        return np.nan
    obs = delta(cells, T)
    acc = np.zeros(n_perm)
    for m in ms:
        vc, vn = values(cells[(m, 'corpus')], T), values(cells[(m, 'none')], T)
        v, nc = np.concatenate([vc, vn]), len(vc)
        perm = np.argsort(rng.random((n_perm, len(v))), 1)
        pv = v[perm]
        acc += pv[:, :nc].mean(1) - pv[:, nc:].mean(1)
    acc /= len(ms)
    return (np.sum(np.abs(acc) >= abs(obs) - 1e-12) + 1) / (n_perm + 1)


def main(Ssim=400, B=500, n_perm=400):
    eps = DV.scored()
    own, pool, both = dev_cells(eps)
    usd = C.EPISODE_USD
    rng = np.random.default_rng(11)
    L = []
    P = L.append
    P('# Power of the headline: share of fans supporting the call within T hours (censored design)\n')
    P(f'v = P(call)·[h ≤ T] per fan; S = mean v over a cell\'s fans; Δ = mean over {", ".join(MODELS)} of '
      f'S(corpus) − S(none). Spot-check, B = 0 and no-call endings censored. Each cell runs to N fans, capped at 2N '
      f'episodes. Simulations {Ssim}, bootstrap {B}, permutations {n_perm}; prior weight N0 = {N0}.\n')
    P('## Dev set, 08-22 cut (the pilot)\n')
    P('| model | arm | episodes | censored | fans: P(call) @ h |')
    P('|---|---|---|---|---|')
    for (m, a), (f, c, n) in own.items():
        P(f"| {m} | {a} | {n} | {c} | " + (', '.join(f"{p:.2f} @ {h:.1f}" for p, h in f) or '—') + ' |')
    for a in ARMS:
        f, c, n = pool[a]
        P(f"| all models | {a} | {n} | {c} | {len(f)} fans, mean v(8 h) {values(f, 8).mean():.2f} |")
    dev = {k: v[0] for k, v in own.items()}
    P(f"\nDev-set Δ(8 h) over the models with fans in both arms: {delta(dev, 8):+.2f} "
      f"(permutation p {perm_p(dev, 8, rng, 10000):.2f}); exploratory.\n")
    pilots = {k: pilot(k, own, pool, both) for k in ('smoothed', 'pooled', 'null')}
    P('## Population Δ and censoring by pilot\n')
    P('| pilot | Δ(6 h) | Δ(8 h) | Δ(12 h) | censoring rate corpus / none (mean over models) |')
    P('|---|---|---|---|---|')
    for k, pl in pilots.items():
        big = {c: draw_fans(pl[c][0], rng, 40000) for c in pl}
        dz = [delta(big, T) for T in (6.0, 8.0, 12.0)]
        cz = [np.mean([pl[(m, a)][1] for m in MODELS]) for a in ARMS]
        P(f"| {k} | {dz[0]:+.3f} | {dz[1]:+.3f} | {dz[2]:+.3f} | {cz[0]:.2f} / {cz[1]:.2f} |")
    P('\n## Precision, power and cost under the rule (T = 8 h)\n')
    P('| pilot | N | episodes / cell corpus, none | censored / cell corpus, none | cells short of N | median Δ̂ | '
      'CI half-width | MDE (80 %) | P(CI > 0) | P(CI < 0) | E[$] per cut |')
    P('|---|---|---|---|---|---|---|---|---|---|---|')
    sims = {}
    for k, pl in pilots.items():
        for N in NS:
            res, ne, nc, short, dollars = [], {a: [] for a in ARMS}, {a: [] for a in ARMS}, [], []
            cells_list = []
            for _ in range(Ssim):
                cells, cost = {}, 0.0
                for (m, a), (src, cz) in pl.items():
                    rows, n_ep, n_c = run_cell(src, cz, rng, N)
                    cells[(m, a)] = rows
                    ne[a].append(n_ep); nc[a].append(n_c); short.append(len(rows) < N)
                    cost += n_ep * usd[m]
                res.append(boot_ci(cells, T_HEAD, rng, B)); dollars.append(cost); cells_list.append(cells)
            r = np.array(res)
            hw = np.nanmedian((r[:, 2] - r[:, 1]) / 2)
            sims[(k, N)] = cells_list
            P(f"| {k} | {N} | {np.mean(ne['corpus']):.1f}, {np.mean(ne['none']):.1f} | {np.mean(nc['corpus']):.1f}, "
              f"{np.mean(nc['none']):.1f} | {np.mean(short):.2f} | {np.nanmedian(r[:, 0]):+.3f} | {hw:.3f} | {MDE_K * hw:.3f} | "
              f"{np.nanmean(r[:, 1] > 0):.2f} | {np.nanmean(r[:, 2] < 0):.2f} | {np.mean(dollars):.0f} |")
    P('\n## Half-width at the budget sensitivities (smoothed pilot)\n')
    P('| N | T = 6 h | T = 8 h | T = 12 h |')
    P('|---|---|---|---|')
    for N in NS:
        hws = []
        for T in (6.0, 8.0, 12.0):
            r = np.array([boot_ci(c, T, rng, B) for c in sims[('smoothed', N)]])
            hws.append(np.nanmedian((r[:, 2] - r[:, 1]) / 2))
        P(f"| {N} | " + ' | '.join(f"{h:.3f}" for h in hws) + ' |')
    P('\n## Decision calibration (two-sided α = 0.05, T = 8 h)\n')
    P('| pilot | N | rejection, CI excludes 0 | rejection, permutation p < 0.05 | mean Δ̂ |')
    P('|---|---|---|---|---|')
    for k in ('null', 'smoothed', 'pooled'):
        for N in NS:
            rc, rp, ds = [], [], []
            for cells in sims[(k, N)]:
                est, lo, hi = boot_ci(cells, T_HEAD, rng, B)
                rc.append(lo > 0 or hi < 0); ds.append(est)
                rp.append(perm_p(cells, T_HEAD, rng, n_perm) < 0.05)
            P(f"| {k} | {N} | {np.mean(rc):.3f} | {np.mean(rp):.3f} | {np.nanmean(ds):+.3f} |")
    P(f"\n$ per episode (common.EPISODE_USD: measured for fable, opus, astra; estimated for the rest): "
      + ', '.join(f"{m} {usd[m]:.2f}" for m in MODELS)
      + '. Censored episodes are paid for. The 2 × 2 cut design doubles the cost.')
    open(C.OUT / 'power_budget.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    a = sys.argv[1:]
    main(int(a[0]) if a else 400, int(a[1]) if len(a) > 1 else 500)
