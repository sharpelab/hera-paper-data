"""Precision of the secondary contrasts: Δ per model, and model contrasts within an arm.

    uv run --no-project --with numpy --with scipy python3 power_per_model.py [S] [B]
Writes power_per_model.md. Same design and pilots as power_budget.py (T = 8 h).
"""
import itertools, sys
import numpy as np
import common as C
import devset as DV
import power_budget as PB


def hw(vals_a, vals_b, rng, B):
    """95 % percentile-bootstrap half-width of mean(a) − mean(b)."""
    if not len(vals_a) or not len(vals_b):
        return np.nan
    d = (vals_a[rng.integers(0, len(vals_a), (B, len(vals_a)))].mean(1)
         - vals_b[rng.integers(0, len(vals_b), (B, len(vals_b)))].mean(1))
    lo, hi = np.percentile(d, [2.5, 97.5])
    return (hi - lo) / 2


def main(Ssim=400, B=500):
    eps = DV.scored()
    own, pool, both = PB.dev_cells(eps)
    rng = np.random.default_rng(13)
    L = []
    P = L.append
    P('# Precision of the per-model contrasts (T = 8 h)\n')
    P(f'Each cell runs to N fans, capped at 2N episodes; {Ssim} simulations × {B} bootstraps. '
      'MDE = the difference detectable with 80 % power at two-sided 5 % ≈ 1.43 × the 95 % half-width.\n')
    P('| pilot | N | Δ per model: half-width (MDE), by model | model contrast within an arm: median half-width (MDE) |')
    P('|---|---|---|---|')
    for kind in ('smoothed', 'pooled'):
        pl = PB.pilot(kind, own, pool, both)
        for N in (10, 20, 30):
            per = {m: [] for m in PB.MODELS}
            con = []
            for _ in range(Ssim):
                cells = {c: PB.run_cell(src, cz, rng, N)[0] for c, (src, cz) in pl.items()}
                v = {c: PB.values(r, PB.T_HEAD) for c, r in cells.items()}
                for m in PB.MODELS:
                    per[m].append(hw(v[(m, 'corpus')], v[(m, 'none')], rng, B))
                for a in PB.ARMS:
                    for m1, m2 in itertools.combinations(PB.MODELS, 2):
                        con.append(hw(v[(m1, a)], v[(m2, a)], rng, B))
            pm = ', '.join(f"{m} {np.nanmedian(per[m]):.2f} ({PB.MDE_K * np.nanmedian(per[m]):.2f})" for m in PB.MODELS)
            c = np.nanmedian(con)
            P(f"| {kind} | {N} | {pm} | {c:.2f} ({PB.MDE_K * c:.2f}) |")
    P('\nThe per-model half-width is about twice the pooled Δ\'s (power_budget.md), as four models average down '
      'the pooled one. A per-model Δ is also noisier where a cell is near 0.5 than where it is near 0 or 1.')
    open(C.OUT / 'power_per_model.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    a = sys.argv[1:]
    main(int(a[0]) if a else 400, int(a[1]) if len(a) > 1 else 500)
