"""Precision / power of the pooled dominance statistic vs cell size, from the dev-set pilot.

    uv run --no-project --with numpy --with scipy python3 power.py [S] [B]
Writes power.md.

Pilot: per (matrix model, arm) cell, the 08-22-cut counted episodes under the floor policy,
quality = capped tone cells at the base knobs. Cells hold 1-6 episodes, so each cell's pilot
is a mixture: its own episodes with weight n_c / (n_c + N0), the arm's pool over all models
(sonnet, haiku, luna included) with weight N0 / (n_c + N0). N0 = 3 is a free parameter.
"""
import sys
import numpy as np
import common as C
import stats as S
import devset as DV

N0 = 3
MODELS = C.MATRIX_MODELS
QKEY = 'cells'


def pilot_points(eps, sel):
    """rows (q, h_placed, landed)"""
    out = []
    for e in eps:
        if not sel(e):
            continue
        if e['ending'] != 'fan':
            out.append((0.0, np.inf, 0.0))
        else:
            q = e[QKEY]
            out.append((q, e['hours'] if q > 0 else np.inf, 1.0))
    return np.array(out, float).reshape(-1, 3)


def build_pilots(eps):
    base = lambda e: DV.counted(e) and e['cut'] == C.CUT_0822
    pool = {arm: pilot_points(eps, lambda e: base(e) and e['corpus'] == arm) for arm in ('corpus', 'none')}
    both = np.vstack([pool['corpus'], pool['none']])
    own = {(m, a): pilot_points(eps, lambda e: base(e) and e['model'] == m and e['corpus'] == a) for m in MODELS for a in ('corpus', 'none')}
    return pool, both, own


def sampler(kind, pool, both, own):
    """-> f(model, arm, rng, size) drawing rows."""
    def draw(m, a, rng, size):
        if kind == 'pooled':
            src = [(pool[a], 1.0)]
        elif kind == 'null':
            src = [(both, 1.0)]
        else:  # smoothed
            nc = len(own[(m, a)])
            src = [(own[(m, a)], nc / (nc + N0)), (pool[a], N0 / (nc + N0))] if nc else [(pool[a], 1.0)]
        w = np.array([x[1] for x in src]); comp = rng.choice(len(src), size, p=w / w.sum())
        out = np.empty((size, 3))
        for i, (arr, _) in enumerate(src):
            idx = comp == i
            out[idx] = arr[rng.integers(0, len(arr), idx.sum())]
        return out
    return draw


def stop_rule_draw(draw, m, a, rng, N):
    """Episodes until N landed fans or 2N episodes."""
    rows = draw(m, a, rng, 2 * N)
    land = np.cumsum(rows[:, 2])
    k = np.searchsorted(land, N) + 1 if land[-1] >= N else 2 * N
    return rows[:k]


def pooled_ci(cells, rng, B):
    """D_pool and its stratified percentile bootstrap CI, via precomputed dominance matrices."""
    Ms = [S.dom_matrix(cells[(m, 'corpus')][:, :2], cells[(m, 'none')][:, :2]) for m in MODELS]
    est = np.mean([M.mean() for M in Ms])
    bs = np.zeros(B)
    for M in Ms:
        nc, nn = M.shape
        ic = rng.integers(0, nc, (B, nc))
        inn = rng.integers(0, nn, (B, nn))
        # mean of M[ic][:, inn] = (1/nc nn) sum_i sum_j M[ic_i, inn_j]  -> use counts
        cc = np.apply_along_axis(np.bincount, 1, ic, minlength=nc)
        cn = np.apply_along_axis(np.bincount, 1, inn, minlength=nn)
        bs += np.einsum('bi,ij,bj->b', cc, M, cn) / (nc * nn)
    bs /= len(Ms)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return est, lo, hi


def perm_p(cells, rng, n_perm):
    """Two-sided p of D_pool: arm labels shuffled within each model, cell sizes kept."""
    obs = np.mean([S.D(cells[(m, 'corpus')][:, :2], cells[(m, 'none')][:, :2]) for m in MODELS])
    allm = [(np.vstack([cells[(m, 'corpus')][:, :2], cells[(m, 'none')][:, :2]]), len(cells[(m, 'corpus')])) for m in MODELS]
    Ms = [S.dom_matrix(X, X) for X, _ in allm]
    cnt = 0
    for _ in range(n_perm):
        v = []
        for (X, nc), M in zip(allm, Ms):
            pi = rng.permutation(len(X))
            v.append(M[np.ix_(pi[:nc], pi[nc:])].mean())
        cnt += abs(np.mean(v)) >= abs(obs) - 1e-12
    return (cnt + 1) / (n_perm + 1)


def cell_u_hw(rows, R, rng, B):
    u = S.ref_score(rows[:, :2], R)
    bm = u[rng.integers(0, len(u), (B, len(u)))].mean(1)
    lo, hi = np.percentile(bm, [2.5, 97.5])
    return (hi - lo) / 2, u.mean()


def main(Ssim=200, B=300):
    eps = DV.scored()
    pool, both, own = build_pilots(eps)
    R = both[:, :2]  # frozen reference set = every counted 08-22 episode (floor policy)
    rng = np.random.default_rng(7)
    L = []
    P = L.append
    P(f'# Power / precision of D_pool (4 matrix models), pilot = 08-22 dev set, quality = {QKEY}, floor policy\n')
    P(f'Outer simulations S = {Ssim}, inner bootstrap B = {B}. Mixture prior weight N0 = {N0}.\n')
    P('Pilot cells (episodes / landed fans / Q>0 fans):')
    for (m, a), v in own.items():
        P(f'- {m} {a}: {len(v)} / {int(v[:, 2].sum())} / {int(np.isfinite(v[:, 1]).sum())}')
    P(f"- pool corpus: {len(pool['corpus'])} / {int(pool['corpus'][:, 2].sum())}; pool none: {len(pool['none'])} / {int(pool['none'][:, 2].sum())}\n")
    # true D per pilot (large-sample)
    for kind in ('smoothed', 'pooled', 'null'):
        draw = sampler(kind, pool, both, own)
        big = {(m, a): draw(m, a, rng, 3000) for m in MODELS for a in ('corpus', 'none')}
        tD = np.mean([S.dom_matrix(big[(m, 'corpus')][:1500, :2], big[(m, 'none')][:1500, :2]).mean() for m in MODELS])
        P(f'Pilot `{kind}`: population D_pool ≈ {tD:+.3f}; landing rate corpus / none = '
          f"{np.mean([big[(m, 'corpus')][:, 2].mean() for m in MODELS]):.2f} / {np.mean([big[(m, 'none')][:, 2].mean() for m in MODELS]):.2f}")
    P('\n## Fixed n episodes per cell\n')
    P('| pilot | n / cell | median D̂ | median CI half-width | P(CI lower > 0) | P(CI upper < 0) | median per-cell ū half-width |')
    P('|---|---|---|---|---|---|---|')
    for kind in ('smoothed', 'pooled', 'null'):
        draw = sampler(kind, pool, both, own)
        for n in (5, 10, 20, 40):
            res, uhw = [], []
            for s in range(Ssim):
                cells = {(m, a): draw(m, a, rng, n) for m in MODELS for a in ('corpus', 'none')}
                res.append(pooled_ci(cells, rng, B))
                uhw.append(np.median([cell_u_hw(v, R, rng, B)[0] for v in cells.values()]))
            r = np.array(res)
            P(f'| {kind} | {n} | {np.median(r[:, 0]):+.2f} | {np.median((r[:, 2] - r[:, 1]) / 2):.3f} | {np.mean(r[:, 1] > 0):.2f} | {np.mean(r[:, 2] < 0):.2f} | {np.median(uhw):.3f} |')
    P('\n## Stopping rule: N landed fans, capped at 2N episodes\n')
    P('| pilot | N | mean episodes / cell (corpus, none) | median D̂ | median CI half-width | P(lower > 0) | P(upper < 0) | cells at cap | median per-cell ū half-width |')
    P('|---|---|---|---|---|---|---|---|---|')
    for kind in ('smoothed', 'pooled', 'null'):
        draw = sampler(kind, pool, both, own)
        for N in (5, 10, 20):
            res, ne, cap, uhw = [], {'corpus': [], 'none': []}, [], []
            for s in range(Ssim):
                cells = {(m, a): stop_rule_draw(draw, m, a, rng, N) for m in MODELS for a in ('corpus', 'none')}
                res.append(pooled_ci(cells, rng, B))
                for (m, a), v in cells.items():
                    ne[a].append(len(v))
                    cap.append(v[:, 2].sum() < N)
                uhw.append(np.median([cell_u_hw(v, R, rng, B)[0] for v in cells.values()]))
            r = np.array(res)
            P(f"| {kind} | {N} | {np.mean(ne['corpus']):.1f}, {np.mean(ne['none']):.1f} | {np.median(r[:, 0]):+.2f} | {np.median((r[:, 2] - r[:, 1]) / 2):.3f} | {np.mean(r[:, 1] > 0):.2f} | {np.mean(r[:, 2] < 0):.2f} | {np.mean(cap):.2f} | {np.median(uhw):.3f} |")
    P('\n## Staged precision rule: stages N = 5, 10, 20 landed fans (each capped at 2N episodes); a cell stops at the first stage whose per-cell ū 95 % half-width <= δ\n')
    P('| pilot | δ | mean episodes / cell | share of cells stopping at N = 5 / 10 / 20 | median D̂ | mean D̂ | median D_pool half-width | P(lower > 0) | P(upper < 0) |')
    P('|---|---|---|---|---|---|---|---|---|')
    for kind in ('smoothed', 'pooled', 'null'):
        draw = sampler(kind, pool, both, own)
        for delta in (0.15, 0.20, 0.25):
            res, ne, st = [], [], []
            for s in range(Ssim):
                cells = {}
                for m in MODELS:
                    for a in ('corpus', 'none'):
                        rows = draw(m, a, rng, 40)
                        for j, N in enumerate((5, 10, 20)):
                            land = np.cumsum(rows[:, 2])
                            k = np.searchsorted(land, N) + 1 if land[2 * N - 1] >= N else 2 * N
                            v = rows[:k]
                            if cell_u_hw(v, R, rng, B)[0] <= delta or N == 20:
                                break
                        cells[(m, a)] = v; ne.append(len(v)); st.append(j)
                res.append(pooled_ci(cells, rng, B))
            r = np.array(res); st = np.array(st)
            P(f"| {kind} | {delta} | {np.mean(ne):.1f} | {np.mean(st == 0):.2f} / {np.mean(st == 1):.2f} / {np.mean(st == 2):.2f} | {np.median(r[:, 0]):+.3f} | {np.mean(r[:, 0]):+.3f} | {np.median((r[:, 2] - r[:, 1]) / 2):.3f} | {np.mean(r[:, 1] > 0):.2f} | {np.mean(r[:, 2] < 0):.2f} |")
    P('\n## Decision calibration under the N-landed rule: bootstrap-CI vs within-model permutation test (two-sided α = 0.05)\n')
    P('| pilot | N | rejection rate, CI excludes 0 | rejection rate, permutation p < 0.05 | mean D̂ | population D |')
    P('|---|---|---|---|---|---|')
    for kind in ('null', 'smoothed'):
        draw = sampler(kind, pool, both, own)
        big = {(m, a): draw(m, a, rng, 3000) for m in MODELS for a in ('corpus', 'none')}
        tD = np.mean([S.dom_matrix(big[(m, 'corpus')][:1500, :2], big[(m, 'none')][:1500, :2]).mean() for m in MODELS])
        for N in (5, 10):
            rc, rp, ds = [], [], []
            for s in range(Ssim):
                cells = {(m, a): stop_rule_draw(draw, m, a, rng, N) for m in MODELS for a in ('corpus', 'none')}
                est, lo, hi = pooled_ci(cells, rng, B)
                rc.append(lo > 0 or hi < 0); ds.append(est)
                rp.append(perm_p(cells, rng, 400) < 0.05)
            P(f'| {kind} | {N} | {np.mean(rc):.3f} | {np.mean(rp):.3f} | {np.mean(ds):+.3f} | {tD:+.3f} |')
    open(C.OUT / 'power.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    a = sys.argv[1:]
    main(int(a[0]) if a else 200, int(a[1]) if len(a) > 1 else 300)
